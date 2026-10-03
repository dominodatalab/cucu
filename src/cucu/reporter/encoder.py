"""Video encoding for scenario screenshots using per-frame timestamps."""

import logging
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

from cucu.config import CONFIG
from cucu.db import step

logger = logging.getLogger(__name__)

_STATUS_COLORS = {
    "passed": (26, 127, 55),
    "failed": (207, 34, 46),
    "error": (207, 34, 46),
    "skipped": (5, 80, 174),
    "untested": (145, 152, 161),
}

_FONT_CACHE = {}

# No cross-platform OS API exists for font discovery without adding dependencies;
# fc-list (Linux) and CoreText (macOS) require subprocess or native bindings.
# These known paths cover the three target platforms with load_default() as fallback.
_FONT_PATHS = [
    "/System/Library/Fonts/Courier.dfont",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "C:/Windows/Fonts/cour.ttf",
]


def _load_font(size):
    """Load a monospace font at the given size, cached by size."""
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    font = None
    for font_path in _FONT_PATHS:
        try:
            font = ImageFont.truetype(font_path, size=size)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()
    _FONT_CACHE[size] = font
    return font


def _render_text_card(
    text,
    keyword,
    status,
    width,
    height,
    font_size_keyword=48,
    font_size_text=26,
):
    """Render step text onto a PIL Image."""
    # Light background matching --vp-stage color
    bg_color = (240, 242, 245)
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    font_keyword = _load_font(font_size_keyword)
    font_text = _load_font(font_size_text)

    keyword_color = _STATUS_COLORS.get(status, (145, 152, 161))
    text_color = (31, 35, 40)

    # Center content vertically and horizontally
    y_pos = height // 3

    # Draw keyword (status-colored)
    draw.text(
        (width // 2, y_pos),
        keyword,
        fill=keyword_color,
        font=font_keyword,
        anchor="mm",
    )

    # Draw step name below keyword
    y_pos += 60
    lines = text.split("\n") if text else [""]
    for line in lines:
        if line:
            draw.text(
                (width // 2, y_pos),
                line,
                fill=text_color,
                font=font_text,
                anchor="mm",
            )
            y_pos += 40

    return img


def _resolve_image_path(img_data, scenario_dir):
    """Resolve a screenshot dict to a Path, or None if not loadable."""
    if not (img_data and isinstance(img_data, dict)):
        return None
    src = img_data.get("html_src") or img_data.get("filepath")
    if not src:
        return None
    img_path = Path(scenario_dir) / src
    if not img_path.exists():
        abs_path = Path(img_data.get("filepath", ""))
        if abs_path.is_absolute() and abs_path.exists():
            img_path = abs_path
    return img_path if img_path.exists() else None


def _resolve_dimensions(steps_list, scenario_dir):
    """Return even (width, height) from the first loadable screenshot, or CONFIG defaults."""
    width = CONFIG.get("CUCU_BROWSER_WINDOW_WIDTH", 1366)
    height = CONFIG.get("CUCU_BROWSER_WINDOW_HEIGHT", 768)
    for s in steps_list:
        for img_data in s.screenshots or []:
            img_path = _resolve_image_path(img_data, scenario_dir)
            if img_path:
                img = Image.open(img_path)
                width, height = img.size
                img.close()
                break
        else:
            continue
        break
    # H.264 requires even dimensions
    return (width // 2) * 2, (height // 2) * 2


def _concat_entry(frame_path):
    """Format one concat-demuxer list entry for a frame shown for 1 second."""
    # The concat demuxer quotes paths with single quotes; an embedded single
    # quote is escaped shell-style as '\''.
    escaped = str(frame_path).replace("'", "'\\''")
    return f"file '{escaped}'\nduration 1"


def gather_scenario_frames(scenario_obj, scenario_dir):
    """Collect frame specs for a scenario without decoding any images.

    Must run in the caller's thread: it reads the scenario's steps from the
    DB and applies CONFIG.hide_secrets with the scenario's config loaded.
    The returned specs are plain data safe to hand to worker threads.

    Args:
        scenario_obj: Scenario model object from DB
        scenario_dir: Path to scenario results directory

    Returns: (frame_specs, width, height) or None if there is nothing to
        encode. Each frame spec is ("image", path) or
        ("card", text, keyword, status).
    """
    scenario_dir = Path(scenario_dir)
    results_dir = scenario_dir.parent.parent
    steps_list = list(scenario_obj.steps.order_by(step.seq))

    if not steps_list:
        logger.error(f"No steps: '{scenario_dir.relative_to(results_dir)}'")
        return None

    width, height = _resolve_dimensions(steps_list, scenario_dir)

    frame_specs = []
    for s in steps_list:
        step_specs = []
        for img_data in s.screenshots or []:
            img_path = _resolve_image_path(img_data, scenario_dir)
            if img_path:
                step_specs.append(("image", str(img_path)))
        if not step_specs:
            step_text = f"{s.keyword} {s.name}"
            if s.text:
                step_text += "\n" + (
                    "\n".join(s.text)
                    if isinstance(s.text, list)
                    else str(s.text)
                )
            step_text = CONFIG.hide_secrets(step_text)
            step_specs.append(
                ("card", step_text, s.keyword, s.status or "untested")
            )
        frame_specs.extend(step_specs)

    if not frame_specs:
        logger.error(
            f"No frames generated for scenario {scenario_obj.scenario_run_id}"
        )
        return None

    return frame_specs, width, height


def encode_frame_specs(frame_specs, output_path, width, height):
    """Encode frames to an MP4, letting ffmpeg decode the PNGs directly.

    Screenshot paths are passed to ffmpeg via its concat demuxer so decoding,
    scaling, and x264 encoding all happen in one subprocess — ~2.5x faster
    than decoding in Python and holds no decoded frames in process memory.
    Text cards (steps without screenshots) are rendered with PIL to temporary
    PNGs first.

    Thread-safe: touches no CONFIG or DB state, so multiple encodes can run
    concurrently and all heavy work happens in per-call ffmpeg subprocesses.

    Args:
        frame_specs: List of specs from gather_scenario_frames
        output_path: Output MP4 file path
        width: Video width in pixels
        height: Video height in pixels

    Returns: output_path or None if encoding failed
    """
    try:
        with tempfile.TemporaryDirectory(prefix="cucu-video-") as tmp_dir:
            entries = []
            for i, spec in enumerate(frame_specs):
                if spec[0] == "image":
                    frame_path = spec[1]
                else:
                    _, text, keyword, status = spec
                    card = _render_text_card(
                        text, keyword, status, width, height
                    )
                    frame_path = os.path.join(tmp_dir, f"card-{i}.png")
                    card.save(frame_path)
                entries.append(_concat_entry(frame_path))
            # The concat demuxer ignores the last entry's duration, so repeat
            # the final frame and trim back to the exact count with -frames:v.
            entries.append(entries[-1])
            list_path = Path(tmp_dir) / "frames.txt"
            list_path.write_text("\n".join(entries), encoding="utf-8")

            result = subprocess.run(
                [
                    imageio_ffmpeg.get_ffmpeg_exe(),
                    "-y",
                    "-loglevel",
                    "error",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(list_path),
                    # lanczos matches the PIL resize previously used for
                    # frames whose size differs from the video dimensions
                    "-vf",
                    f"scale={width}:{height}:flags=lanczos,format=yuv420p",
                    "-r",
                    "1",
                    "-frames:v",
                    str(len(frame_specs)),
                    "-c:v",
                    "libx264",
                    # Screenshot slideshows at 1 fps don't benefit from
                    # slower presets: ultrafast encodes ~15x faster than the
                    # libx264 default (medium) for a modest size increase.
                    "-preset",
                    "ultrafast",
                    "-crf",
                    "28",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
            )
        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or f"ffmpeg exited {result.returncode}"
            )
        return output_path
    except Exception as e:
        logger.error(f"Video encoding failed for {output_path}: {e}")
        if Path(output_path).exists():
            Path(output_path).unlink()
        return None


def encode_workers():
    """Worker count for parallel video encoding.

    Uses CUCU_VIDEO_ENCODE_WORKERS when set; otherwise min(6, cpu count).
    Benchmarks on real report workloads plateau around 6 workers (each
    ffmpeg subprocess also runs its own x264 threads), so going wider only
    oversubscribes the CPU.
    """
    configured = str(CONFIG.get("CUCU_VIDEO_ENCODE_WORKERS", "") or "").strip()
    if configured:
        return max(1, int(configured))
    return max(1, min(6, os.cpu_count() or 1))


def encode_videos_parallel(jobs, workers=None):
    """Encode scenario videos concurrently on a thread pool.

    Args:
        jobs: list of (frame_specs, width, height, output_path, copy_to)
            tuples; copy_to (or None) is a destination the finished MP4 is
            copied to (e.g. the report directory).
        workers: thread count; defaults to encode_workers()

    Returns: number of successfully encoded videos
    """
    if workers is None:
        workers = encode_workers()

    def _encode_one(job):
        frame_specs, width, height, output_path, copy_to = job
        try:
            result = encode_frame_specs(
                frame_specs, output_path, width, height
            )
            if result and Path(result).exists():
                if copy_to:
                    shutil.copy2(result, copy_to)
                return True
        except Exception as ex:
            logger.error(f"Video encoding failed for {output_path}: {ex}")
        return False

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return sum(pool.map(_encode_one, jobs))


def encode_scenario_video(scenario_obj, scenario_dir):
    """Encode video for a scenario with one frame per step.

    Args:
        scenario_obj: Scenario model object from DB
        scenario_dir: Path to scenario results directory

    Returns: output_path or None if encoding failed
    """
    output_path = Path(scenario_dir) / "screenshots.mp4"
    results_dir = Path(scenario_dir).parent.parent

    if output_path.exists() and output_path.stat().st_size > 0:
        logger.debug(f"Skip existing: {output_path.relative_to(results_dir)}")
        return output_path

    gathered = gather_scenario_frames(scenario_obj, scenario_dir)
    if gathered is None:
        return None

    frame_specs, width, height = gathered
    return encode_frame_specs(frame_specs, output_path, width, height)

"""Video encoding for scenario screenshots using per-frame timestamps."""

import logging
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import imageio.v2 as iio
import numpy as np
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


def _encode_with_imageio(frames, output_path, width, height):
    """Encode video from PIL Image frames using imageio-ffmpeg (libx264, browser-compatible).

    Args:
        frames: List of PIL Image objects (RGB)
        output_path: Output MP4 file path
        width: Video width in pixels
        height: Video height in pixels
    """
    try:
        writer = iio.get_writer(
            str(output_path),
            fps=1,
            codec="libx264",
            pixelformat="yuv420p",
            macro_block_size=1,
            quality=None,
            # Screenshot slideshows at 1 fps don't benefit from slower
            # presets: ultrafast encodes ~15x faster than the libx264
            # default (medium) for a modest size increase.
            ffmpeg_params=["-preset", "ultrafast", "-crf", "28"],
            ffmpeg_log_level="error",
        )
        try:
            for pil_img in frames:
                img = pil_img.convert("RGB")
                if img.width != width or img.height != height:
                    img = img.resize((width, height), Image.LANCZOS)
                writer.append_data(np.asarray(img))
        finally:
            writer.close()
        return output_path
    except Exception as e:
        logger.error(f"Video encoding failed for {output_path}: {e}")
        if Path(output_path).exists():
            Path(output_path).unlink()
        return None


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
    """Decode/render frames from specs and encode them to an MP4.

    Thread-safe: touches no CONFIG or DB state, so multiple encodes can run
    concurrently (the x264 work happens in a per-writer ffmpeg subprocess).

    Args:
        frame_specs: List of specs from gather_scenario_frames
        output_path: Output MP4 file path
        width: Video width in pixels
        height: Video height in pixels

    Returns: output_path or None if encoding failed
    """
    frames = []
    for spec in frame_specs:
        if spec[0] == "image":
            frames.append(Image.open(spec[1]).convert("RGB"))
        else:
            _, text, keyword, status = spec
            frames.append(
                _render_text_card(text, keyword, status, width, height)
            )
    return _encode_with_imageio(frames, output_path, width, height)


def encode_workers():
    """Worker count for parallel video encoding.

    Uses CUCU_VIDEO_ENCODE_WORKERS when set; otherwise min(3, cpu count).
    The default is capped because each in-flight scenario holds all its
    decoded frames in memory while encoding.
    """
    configured = str(CONFIG.get("CUCU_VIDEO_ENCODE_WORKERS", "") or "").strip()
    if configured:
        return max(1, int(configured))
    return max(1, min(3, os.cpu_count() or 1))


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

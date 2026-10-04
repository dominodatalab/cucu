"""Video encoding for scenario screenshots using per-frame timestamps."""

import hashlib
import json
import logging
import math
import os
import shutil
import sqlite3
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

from cucu.config import CONFIG
from cucu.db import step
from cucu.utils import ellipsize_filename

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


def _concat_entry(frame_path, duration=1):
    """Format one concat-demuxer list entry for a frame shown `duration` seconds."""
    # The concat demuxer quotes paths with single quotes; an embedded single
    # quote is escaped shell-style as '\''.
    escaped = str(frame_path).replace("'", "'\\''")
    return f"file '{escaped}'\nduration {duration}"


def _merge_identical_frames(frame_specs):
    """Collapse runs of consecutive identical frames into [spec, count] pairs.

    Steps that don't change the page (waits, visibility checks) produce
    byte-identical screenshots — ~44% of frames in a real smoke run. ffmpeg
    then decodes each distinct frame once and holds it for `count` seconds,
    so the output still has exactly one frame per spec.
    """
    runs = []
    prev_key = None
    for spec in frame_specs:
        if spec[0] == "image":
            key = hashlib.md5(
                Path(spec[1]).read_bytes(), usedforsecurity=False
            ).hexdigest()
        else:
            key = spec
        if runs and key == prev_key:
            runs[-1][1] += 1
        else:
            runs.append([spec, 1])
        prev_key = key
    return runs


def gather_scenario_frames(steps_list, scenario_dir):
    """Collect frame specs for a scenario without decoding any images.

    Must run in the caller's thread with the scenario's config loaded, since
    it applies CONFIG.hide_secrets to step text. The returned specs are plain
    data safe to hand to worker threads.

    Args:
        steps_list: the scenario's steps ordered by seq; each needs keyword,
            name, text, status, and screenshots attributes
        scenario_dir: Path to scenario results directory

    Returns: (frame_specs, width, height) or None if there is nothing to
        encode. Each frame spec is ("image", path) or
        ("card", text, keyword, status).
    """
    scenario_dir = Path(scenario_dir)
    results_dir = scenario_dir.parent.parent

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
            f"No frames generated: '{scenario_dir.relative_to(results_dir)}'"
        )
        return None

    return frame_specs, width, height


def encode_frame_specs(frame_specs, output_path, width, height):
    """Encode frames to an MP4, letting ffmpeg decode the PNGs directly.

    Screenshot paths are passed to ffmpeg via its concat demuxer so decoding,
    scaling, and x264 encoding all happen in one subprocess, and runs of
    identical consecutive frames are decoded once. Text cards (steps without
    screenshots) are rendered with PIL to temporary PNGs first.

    The video is written to a .partial file and renamed into place, so an
    interrupted encode never leaves a truncated screenshots.mp4 behind for
    the report to reuse.

    Thread-safe: touches no CONFIG or DB state, so multiple encodes can run
    concurrently and all heavy work happens in per-call ffmpeg subprocesses.

    Args:
        frame_specs: List of specs from gather_scenario_frames
        output_path: Output MP4 file path
        width: Video width in pixels
        height: Video height in pixels

    Returns: output_path or None if encoding failed
    """
    partial_path = Path(output_path).with_name(
        Path(output_path).name + ".partial"
    )
    try:
        with tempfile.TemporaryDirectory(prefix="cucu-video-") as tmp_dir:
            entries = []
            for i, (spec, count) in enumerate(
                _merge_identical_frames(frame_specs)
            ):
                if spec[0] == "image":
                    frame_path = spec[1]
                else:
                    _, text, keyword, status = spec
                    card = _render_text_card(
                        text, keyword, status, width, height
                    )
                    frame_path = os.path.join(tmp_dir, f"card-{i}.png")
                    card.save(frame_path)
                entries.append(_concat_entry(frame_path, count))
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
                    "-f",
                    "mp4",
                    str(partial_path),
                ],
                capture_output=True,
                text=True,
            )
        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or f"ffmpeg exited {result.returncode}"
            )
        os.replace(partial_path, output_path)
        return output_path
    except Exception as e:
        logger.error(f"Video encoding failed for {output_path}: {e}")
        partial_path.unlink(missing_ok=True)
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


def encode_start_remaining(workers):
    """Unfinished-feature count at which `cucu run` starts encoding videos.

    Uses CUCU_VIDEO_ENCODE_START_REMAINING when set (negative disables
    encoding during the run); otherwise ceil(workers / 2) - 1, so encoding
    starts once more than half the run's workers are idle.
    """
    configured = str(
        CONFIG.get("CUCU_VIDEO_ENCODE_START_REMAINING", "") or ""
    ).strip()
    if configured:
        return int(configured)
    return math.ceil(workers / 2) - 1


def _encode_job(job):
    """Encode one (frame_specs, width, height, output_path, copy_to) job."""
    frame_specs, width, height, output_path, copy_to = job
    try:
        result = encode_frame_specs(frame_specs, output_path, width, height)
        if result and Path(result).exists():
            if copy_to:
                shutil.copy2(result, copy_to)
            return True
    except Exception as ex:
        logger.error(f"Video encoding failed for {output_path}: {ex}")
    return False


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

    # largest first, so the biggest scenario doesn't start last and set the
    # wall time on its own
    jobs = sorted(jobs, key=lambda job: len(job[0]), reverse=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return sum(pool.map(_encode_job, jobs))


def _json_column(value):
    return json.loads(value) if value else None


class RunVideoEncoder:
    """Encodes scenario videos while `cucu run` finishes its last features.

    Once at most `start_remaining` features are unfinished, every finished
    feature's scenarios are encoded on a thread pool, so the report step only
    copies the videos. Steps are read from the per-worker run DBs, which are
    only consolidated into run.db after the run. Frame gathering runs in the
    caller's thread because it swaps CONFIG to each scenario's saved config
    for secret redaction, exactly like the report does.
    """

    def __init__(self, results_dir, start_remaining, workers):
        self.results_dir = Path(results_dir)
        self.start_remaining = start_remaining
        self.workers = workers
        self.pool = None
        self.futures = []
        self.done_features = set()

    def poll(self, remaining):
        """Call from the run's polling loop with the unfinished feature count."""
        if self.pool is None:
            if remaining > self.start_remaining:
                return
            logger.info(
                f"{remaining} features remaining, encoding scenario videos "
                f"with {self.workers} workers during the run"
            )
            self.pool = ThreadPoolExecutor(max_workers=self.workers)
        for job in self._gather_finished():
            self.futures.append(self.pool.submit(_encode_job, job))

    def finish(self, cancel=False):
        """Encode what's left (unless cancelled) and wait for in-flight encodes.

        Safe to call more than once. Returns the number of videos encoded.
        """
        if not cancel:
            self.poll(0)
        if self.pool is None:
            return 0
        self.pool.shutdown(wait=True, cancel_futures=cancel)
        self.pool = None
        self.start_remaining = -1  # never restart after finishing
        encoded = sum(
            1 for f in self.futures if not f.cancelled() and f.result()
        )
        logger.info(f"Encoded {encoded} scenario videos during the run")
        return encoded

    def _gather_finished(self):
        jobs = []
        run_id = CONFIG["CUCU_RUN_ID"]
        for db_path in sorted(self.results_dir.glob(f"run_{run_id}_*.db")):
            try:
                with closing(
                    sqlite3.connect(
                        db_path.resolve().as_uri() + "?mode=ro",
                        uri=True,
                        timeout=1,
                    )
                ) as conn:
                    self._gather_db(conn, jobs)
            except sqlite3.Error as e:
                # a worker may be mid-write; its features are retried next poll
                logger.debug(f"Skipping {db_path.name} this poll: {e}")
        return jobs

    def _gather_db(self, conn, jobs):
        features = conn.execute(
            "SELECT feature_run_id, name FROM feature "
            "WHERE end_at IS NOT NULL AND COALESCE(status, '') != 'untested'"
        ).fetchall()
        for feature_run_id, feature_name in features:
            if feature_run_id in self.done_features:
                continue
            feature_dir = self.results_dir / ellipsize_filename(feature_name)
            scenarios = conn.execute(
                "SELECT scenario_run_id, name FROM scenario "
                "WHERE feature_run_id = ? ORDER BY seq",
                (feature_run_id,),
            ).fetchall()
            for scenario_run_id, scenario_name in scenarios:
                scenario_dir = feature_dir / ellipsize_filename(scenario_name)
                output_path = scenario_dir / "screenshots.mp4"
                if not scenario_dir.is_dir() or (
                    output_path.exists() and output_path.stat().st_size > 0
                ):
                    continue
                steps_list = [
                    SimpleNamespace(
                        keyword=keyword,
                        name=name,
                        status=status,
                        text=_json_column(text),
                        screenshots=_json_column(screenshots),
                    )
                    for keyword, name, status, text, screenshots in conn.execute(
                        "SELECT keyword, name, status, text, screenshots "
                        "FROM step WHERE scenario_run_id = ? ORDER BY seq",
                        (scenario_run_id,),
                    )
                ]
                config_path = scenario_dir / "logs" / "cucu.config.yaml.txt"
                CONFIG.snapshot("run-video-gather")
                try:
                    if config_path.exists():
                        CONFIG.load(config_path)
                    gathered = gather_scenario_frames(steps_list, scenario_dir)
                except Exception as e:
                    logger.warning(
                        f"Failed to gather frames for {scenario_dir}: {e}"
                    )
                    gathered = None
                finally:
                    CONFIG.restore(with_pop=True)
                if gathered:
                    frame_specs, width, height = gathered
                    jobs.append(
                        (frame_specs, width, height, output_path, None)
                    )
            self.done_features.add(feature_run_id)


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

    gathered = gather_scenario_frames(
        list(scenario_obj.steps.order_by(step.seq)), scenario_dir
    )
    if gathered is None:
        return None

    frame_specs, width, height = gathered
    return encode_frame_specs(frame_specs, output_path, width, height)

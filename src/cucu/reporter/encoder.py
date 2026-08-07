"""Video encoding for scenario screenshots using per-frame timestamps."""

import logging
from pathlib import Path

import imageio.v3 as iio
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
        with iio.imopen(str(output_path), "w", plugin="FFMPEG") as writer:
            writer.init_video_stream(
                "libx264",
                fps=1,
                pixel_format="yuv420p",
            )
            for pil_img in frames:
                img = pil_img.convert("RGB")
                if img.width != width or img.height != height:
                    img = img.resize((width, height), Image.LANCZOS)
                writer.write_frame(np.asarray(img))
        return output_path
    except Exception as e:
        logger.error(f"Video encoding failed for {output_path}: {e}")
        if Path(output_path).exists():
            Path(output_path).unlink()
        return None


def encode_scenario_video(scenario_obj, scenario_dir):
    """Encode video for a scenario with one frame per step.

    Args:
        scenario_obj: Scenario model object from DB
        scenario_dir: Path to scenario results directory

    Returns: output_path or None if encoding failed
    """
    output_path = Path(scenario_dir) / "screenshots.mp4"
    steps_list = list(scenario_obj.steps.order_by(step.seq))

    if output_path.exists():
        logger.warning(
            f"Video already exists for scenario {scenario_obj.scenario_run_id}, skipping encoding"
        )
        return output_path

    if not steps_list:
        logger.warning(
            f"No steps found for scenario {scenario_obj.scenario_run_id}"
        )
        return None

    width, height = _resolve_dimensions(steps_list, scenario_dir)

    frames = []
    for s in steps_list:
        step_frames = []
        for img_data in s.screenshots or []:
            img_path = _resolve_image_path(img_data, scenario_dir)
            if img_path:
                step_frames.append(Image.open(img_path).convert("RGB"))
        if not step_frames:
            step_text = f"{s.keyword} {s.name}"
            if s.text:
                step_text += "\n" + (
                    "\n".join(s.text)
                    if isinstance(s.text, list)
                    else str(s.text)
                )
            step_text = CONFIG.hide_secrets(step_text)
            step_frames.append(
                _render_text_card(
                    step_text,
                    s.keyword,
                    s.status or "untested",
                    width,
                    height,
                )
            )
        frames.extend(step_frames)

    if not frames:
        logger.warning(
            f"No frames generated for scenario {scenario_obj.scenario_run_id}"
        )
        return None

    return _encode_with_imageio(frames, output_path, width, height)

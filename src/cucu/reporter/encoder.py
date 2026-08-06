"""Video encoding for scenario screenshots using per-frame timestamps."""

import logging
from pathlib import Path

import cv2
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

_FONT_PATHS = [
    "/System/Library/Fonts/Courier.dfont",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
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


def _encode_with_opencv(frames, output_path, width, height):
    """Encode video from PIL Image frames using opencv-python-headless.

    Args:
        frames: List of PIL Image objects (RGB)
        output_path: Output MP4 file path
        width: Video width in pixels
        height: Video height in pixels
    """
    fps = 1
    # H.264 requires even dimensions
    width = (width // 2) * 2
    height = (height // 2) * 2

    # Try mp4v (MPEG-4) first; fall back to avc1 (H.264).
    writer = cv2.VideoWriter(
        str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )
    if not writer.isOpened():
        writer.release()
        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*"avc1"),
            fps,
            (width, height),
        )
    if not writer.isOpened():
        writer.release()
        raise RuntimeError(
            "Could not open VideoWriter with mp4v or avc1 codecs"
        )
    try:
        for pil_img in frames:
            bgr = np.array(pil_img)[:, :, ::-1]  # PIL RGB → cv2 BGR
            if bgr.shape[1] != width or bgr.shape[0] != height:
                if bgr.shape[1] <= width + 1 and bgr.shape[0] <= height + 1:
                    bgr = bgr[:height, :width]
                else:
                    logger.warning(
                        f"Frame size {bgr.shape[1]}x{bgr.shape[0]} does not match expected {width}x{height}, resizing"
                    )
                    bgr = cv2.resize(
                        bgr, (width, height), interpolation=cv2.INTER_LANCZOS4
                    )
            writer.write(bgr)
        return True
    except Exception as e:
        logger.error(f"Video encoding failed for {output_path}: {e}")
        if output_path.exists():
            output_path.unlink()
        return False
    finally:
        writer.release()


def encode_scenario_video(scenario_obj, scenario_dir):
    """Encode video for a scenario with one frame per step.

    Args:
        scenario_obj: Scenario model object from DB
        scenario_dir: Path to scenario results directory

    Returns: (output_path, frame_count) or None if encoding failed
    """
    output_path = Path(scenario_dir) / "screenshots.mp4"
    steps_list = list(scenario_obj.steps.order_by(step.seq))

    if output_path.exists():
        return (output_path, len(steps_list))

    if not steps_list:
        return None

    # Resolve video dimensions from the first loadable PNG so text-card
    # frames match and no PNG gets resized during encoding.
    width = CONFIG.get("CUCU_BROWSER_WINDOW_WIDTH", 1366)
    height = CONFIG.get("CUCU_BROWSER_WINDOW_HEIGHT", 768)
    for s in steps_list:
        for img_data in s.screenshots or []:
            img_path = _resolve_image_path(img_data, scenario_dir)
            if img_path:
                width, height = Image.open(img_path).size
                break
        else:
            continue
        break

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
        return None

    if not _encode_with_opencv(frames, output_path, width, height):
        return None
    return (output_path, len(frames))

"""Video encoding for scenario screenshots using per-frame timestamps."""

import logging
from pathlib import Path

from cucu.config import CONFIG
from cucu.db import step

logger = logging.getLogger(__name__)


def _render_text_card(
    text,
    keyword,
    status,
    width,
    height,
    font_size_keyword=48,
    font_size_text=26,
    font_size_detail=18,
):
    """Render step text onto a PIL Image."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise RuntimeError(
            "Pillow is required for video encoding. Install with: uv sync --extra video"
        )

    # Light background matching --vp-stage color
    bg_color = (240, 242, 245)
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load monospace font, fallback to default
    font_paths = [
        "/System/Library/Fonts/Courier.dfont",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    font_keyword = None
    font_text = None
    for font_path in font_paths:
        try:
            font_keyword = ImageFont.truetype(
                font_path, size=font_size_keyword
            )
            font_text = ImageFont.truetype(font_path, size=font_size_text)
            break
        except (OSError, IOError):
            continue
    if not font_keyword:
        font_keyword = ImageFont.load_default()
    if not font_text:
        font_text = ImageFont.load_default()

    # Status-based text colors (matching CSS)
    status_colors = {
        "passed": (26, 127, 55),
        "failed": (207, 34, 46),
        "error": (207, 34, 46),
        "skipped": (5, 80, 174),
        "untested": (145, 152, 161),
    }
    keyword_color = status_colors.get(status, (145, 152, 161))
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


def _get_screenshot_dimensions():
    width = CONFIG.get("CUCU_BROWSER_WINDOW_WIDTH", 1366)
    height = CONFIG.get("CUCU_BROWSER_WINDOW_HEIGHT", 768)
    return width, height


def _encode_with_opencv(frames, output_path, width, height, fps=1):
    """Encode video from PIL Image frames using opencv-python-headless.

    Args:
        frames: List of PIL Image objects
        output_path: Output MP4 file path
        width: Video width in pixels
        height: Video height in pixels
        fps: Frames per second (default: 1)
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        raise RuntimeError(
            "opencv-python-headless is required for video encoding. "
            "Install with: uv sync --extra video"
        )

    # H.264 requires even dimensions
    width = (width // 2) * 2
    height = (height // 2) * 2

    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    try:
        for pil_img in frames:
            arr = np.array(pil_img.convert("RGB"))
            bgr = arr[:, :, ::-1]  # PIL RGB → cv2 BGR
            if bgr.shape[1] != width or bgr.shape[0] != height:
                bgr = cv2.resize(
                    bgr, (width, height), interpolation=cv2.INTER_LANCZOS4
                )
            writer.write(bgr)
    finally:
        writer.release()


def encode_scenario_video(scenario_obj, scenario_dir):
    """Encode video for a scenario with one frame per step.

    Args:
        scenario_obj: Scenario model object from DB
        scenario_dir: Path to scenario results directory

    Returns: (output_path, frame_count, fps) or None if encoding failed
    """
    output_path = Path(scenario_dir) / "screenshots.mp4"

    # Check if video already exists
    if output_path.exists():
        try:
            steps_list = list(scenario_obj.steps.order_by(step.seq))
            fps = CONFIG.get("CUCU_SCREENSHOT_VIDEO_FPS", 1)
            return (output_path, len(steps_list), fps)
        except Exception:
            pass

    # Get steps
    try:
        steps_list = list(scenario_obj.steps.order_by(step.seq))
        if not steps_list:
            logger.warning(
                f"No steps found for scenario {scenario_obj.scenario_run_id}"
            )
            return None
    except Exception as e:
        logger.error(f"Failed to fetch scenario steps: {e}")
        return None

    width, height = _get_screenshot_dimensions()

    # Build frames list — one frame per step
    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError(
            "Pillow is required for video encoding. Install with: uv sync --extra video"
        )

    frames = []
    for s in steps_list:
        frame = None
        if s.screenshots:
            # Try to use the first screenshot
            for img_data in s.screenshots:
                if img_data and isinstance(img_data, dict):
                    path = img_data.get("filepath")
                    if path:
                        img_path = Path(scenario_dir) / path
                        if img_path.exists():
                            try:
                                frame = Image.open(img_path)
                                break
                            except Exception:
                                continue
        if not frame:
            # Render text-card if no screenshot available
            step_text = f"{s.keyword} {s.name}"
            if s.text:
                if isinstance(s.text, list):
                    step_text += "\n" + "\n".join(s.text)
                else:
                    step_text += "\n" + str(s.text)
            step_text = CONFIG.hide_secrets(step_text)
            status = s.status or "untested"
            frame = _render_text_card(
                step_text, s.keyword, status, width, height
            )
        frames.append(frame)

    if not frames:
        logger.warning(
            f"No frames generated for scenario {scenario_obj.scenario_run_id}"
        )
        return None

    # Encode video
    try:
        fps = CONFIG.get("CUCU_SCREENSHOT_VIDEO_FPS", 1)
        _encode_with_opencv(frames, output_path, width, height, fps)
        logger.info(f"Successfully encoded video: {output_path}")
        return (output_path, len(frames), fps)
    except Exception as e:
        logger.error(f"Video encoding error: {e}")
        if output_path.exists():
            output_path.unlink()
        return None

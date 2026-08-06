"""Unit tests for video encoder module."""

from unittest.mock import MagicMock, patch

import pytest

try:
    import PIL  # noqa: F401

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from cucu.reporter.encoder import _render_text_card, _resolve_dimensions

skip_no_pillow = pytest.mark.skipif(
    not HAS_PILLOW, reason="Pillow not installed"
)


@skip_no_pillow
def test_render_text_card_creates_image():
    img = _render_text_card(
        text="Test step",
        keyword="Given",
        status="passed",
        width=1366,
        height=768,
    )
    assert img is not None
    assert img.size == (1366, 768)
    assert img.mode == "RGB"


@skip_no_pillow
def test_render_text_card_with_multiline_text():
    img = _render_text_card(
        text="Line 1\nLine 2\nLine 3",
        keyword="When",
        status="failed",
        width=1366,
        height=768,
    )
    assert img.size == (1366, 768)


@skip_no_pillow
def test_render_text_card_different_statuses():
    for status in ["passed", "failed", "skipped", "untested"]:
        img = _render_text_card(
            text=f"Test {status}",
            keyword="Then",
            status=status,
            width=1280,
            height=720,
        )
        assert img.size == (1280, 720)


def test_resolve_dimensions_returns_config_defaults_when_no_screenshots():
    step = MagicMock()
    step.screenshots = []
    width, height = _resolve_dimensions([step], "/some/dir")
    assert width == 1366
    assert height == 768


def test_resolve_dimensions_returns_image_size_from_first_screenshot():
    step = MagicMock()
    step.screenshots = [{"html_src": "step_0.png"}]
    fake_img = MagicMock()
    fake_img.size = (1920, 1080)
    with (
        patch(
            "cucu.reporter.encoder._resolve_image_path",
            return_value="/some/dir/step_0.png",
        ),
        patch("cucu.reporter.encoder.Image.open", return_value=fake_img),
    ):
        width, height = _resolve_dimensions([step], "/some/dir")
    assert width == 1920
    assert height == 1080

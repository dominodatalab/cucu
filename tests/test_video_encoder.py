"""Unit tests for video encoder module."""

import pytest

try:
    import PIL  # noqa: F401

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from cucu.reporter.encoder import _render_text_card

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

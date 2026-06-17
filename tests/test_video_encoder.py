"""Unit tests for video encoder module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

try:
    import PIL  # noqa: F401

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from cucu.video.encoder import (
    _get_screenshot_dimensions,
    _render_text_card,
)


@pytest.mark.skipif(not HAS_PILLOW, reason="Pillow not installed")
class TestRenderTextCard:
    """Tests for text-card rendering."""

    def test_render_text_card_creates_image(self):
        """Test that render_text_card creates a valid PIL Image."""
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

    def test_render_text_card_with_multiline_text(self):
        """Test rendering with multi-line step text."""
        img = _render_text_card(
            text="Line 1\nLine 2\nLine 3",
            keyword="When",
            status="failed",
            width=1366,
            height=768,
        )
        assert img.size == (1366, 768)

    def test_render_text_card_different_statuses(self):
        """Test rendering with different step statuses."""
        for status in ["passed", "failed", "skipped", "untested"]:
            img = _render_text_card(
                text=f"Test {status}",
                keyword="Then",
                status=status,
                width=1280,
                height=720,
            )
            assert img.size == (1280, 720)


class TestGetScreenshotDimensions:
    """Tests for screenshot dimension detection."""

    def test_dimensions_from_no_screenshots(self):
        """Test fallback to config defaults when no screenshots exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            steps_list = []
            width, height = _get_screenshot_dimensions(
                Path(tmpdir), steps_list
            )
            # Should use config defaults
            assert width == 1366  # CUCU_BROWSER_WINDOW_WIDTH default
            assert height == 768  # CUCU_BROWSER_WINDOW_HEIGHT default

    def test_dimensions_from_empty_screenshots(self):
        """Test fallback when steps have empty screenshot lists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock steps with empty screenshots
            mock_step = MagicMock()
            mock_step.screenshots = []
            steps_list = [mock_step]

            width, height = _get_screenshot_dimensions(
                Path(tmpdir), steps_list
            )
            assert width == 1366
            assert height == 768

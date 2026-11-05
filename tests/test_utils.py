from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import pytest_check as check

from cucu import utils
from cucu.utils import get_top_level_rect_and_size


class FakeElement:
    def __init__(self, rect=None):
        self.rect = rect


class FakeBrowser:
    """
    models a driver switched into nested iframes: frame_stack holds the
    iframes entered (outermost first), and execute returns the rect of the
    element/iframe in the frame the browser is currently switched into
    """

    def __init__(self, frame_stack, viewport):
        self.frame_stack = list(frame_stack)
        self.viewport = viewport
        self.switch_calls = []
        self.scripts = []

    def execute(self, javascript, *args):
        self.scripts.append(javascript)
        if args:
            return dict(args[0].rect)
        return self.viewport

    def switch_to_parent_frame(self):
        self.frame_stack.pop()
        self.switch_calls.append("parent")

    def switch_to_frame(self, frame):
        self.frame_stack.append(frame)
        self.switch_calls.append(frame)


@pytest.mark.parametrize(
    "frame_rects, expected_x, expected_y",
    [
        pytest.param([], 10, 20, id="top-level-element"),
        pytest.param([(100, 200)], 110, 220, id="one-iframe"),
        pytest.param(
            [(100, 200), (5, 7)], 115, 227, id="nested-iframes-accumulate"
        ),
    ],
)
def test_get_top_level_rect_and_size_sums_iframe_offsets(
    frame_rects, expected_x, expected_y
):
    frames = [
        FakeElement({"x": x, "y": y, "width": 0, "height": 0})
        for x, y in frame_rects
    ]
    element = FakeElement({"x": 10, "y": 20, "width": 126, "height": 36})
    viewport = {"width": 1280, "height": 800}
    browser = FakeBrowser(frames, viewport)

    rect, size = get_top_level_rect_and_size(browser, element)

    check.equal(rect["x"], expected_x)
    check.equal(rect["y"], expected_y)
    check.equal((rect["width"], rect["height"]), (126, 36))
    check.equal(size, viewport)
    check.equal(
        browser.frame_stack, frames, msg="browser is back in the same frame"
    )
    check.is_false(
        any("frameElement" in script for script in browser.scripts),
        msg="no cross-frame JS (hangs chromedriver in VSCode webviews)",
    )


@pytest.mark.parametrize(
    "element, expects_frame_walk",
    [
        pytest.param(None, False, id="no-element-reads-current-frame-size"),
        pytest.param(
            FakeElement(), True, id="element-uses-top-level-geometry"
        ),
    ],
)
def test_take_screenshot_only_walks_frames_for_element(
    tmp_path, element, expects_frame_walk
):
    ctx = MagicMock()
    ctx.scenario_dir = str(tmp_path)
    ctx.step_index = 0
    ctx.current_step = SimpleNamespace(step_run_id="id")
    ctx.browser = MagicMock()
    ctx.browser.execute.return_value = {"width": 100, "height": 200}
    config = MagicMock()
    config.__getitem__.side_effect = {
        "__STEP_SCREENSHOT_COUNT": 0,
        "CUCU_MONITOR_PNG": None,
    }.__getitem__
    config.hide_secrets.side_effect = lambda text: text

    with (
        patch.object(utils, "CONFIG", config),
        patch.object(
            utils,
            "get_top_level_rect_and_size",
            return_value=(
                {"x": 1, "y": 2, "width": 10, "height": 20},
                {"width": 100, "height": 200},
            ),
        ) as walk,
    ):
        utils.take_screenshot(ctx, "step", element=element)

    assert walk.called is expects_frame_walk

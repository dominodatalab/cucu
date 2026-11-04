from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from cucu import utils
from cucu.utils import get_top_level_rect


class FakeElement:
    pass


class MockBrowser:
    def __init__(self, rect: dict):
        self._rect = rect
        self.execute_calls: list[tuple[str, tuple]] = []

    def screenshot(self, filepath):
        pass

    def execute(self, javascript, *args):
        self.execute_calls.append((javascript, args))
        return self._rect


def test_get_top_level_rect_passes_element_and_returns_browser_result():
    rect = {"x": 67, "y": 1232, "width": 126, "height": 36}
    element = FakeElement()
    browser = MockBrowser(rect)

    result = get_top_level_rect(browser, element)

    assert result == rect
    [(script, args)] = browser.execute_calls
    assert args == (element,)
    assert "getBoundingClientRect" in script
    assert "frameElement" in script


@pytest.mark.parametrize(
    "element, expects_frame_climb",
    [
        pytest.param(None, False, id="no-element-skips-frame-climb"),
        pytest.param(FakeElement(), True, id="element-climbs-frames"),
    ],
)
def test_take_screenshot_only_climbs_frames_for_element(
    tmp_path, element, expects_frame_climb
):
    rect = {"x": 1, "y": 2, "width": 10, "height": 20}
    ctx = MagicMock()
    ctx.scenario_dir = str(tmp_path)
    ctx.step_index = 0
    ctx.current_step = SimpleNamespace(step_run_id="id")
    ctx.browser = MockBrowser({**rect, "width": 100, "height": 200})

    config = MagicMock()
    config.__getitem__.side_effect = {
        "__STEP_SCREENSHOT_COUNT": 0,
        "CUCU_MONITOR_PNG": None,
    }.__getitem__
    config.hide_secrets.side_effect = lambda text: text
    with patch.object(utils, "CONFIG", config):
        utils.take_screenshot(ctx, "step", element=element)

    [(size_script, _), *_] = ctx.browser.execute_calls
    assert ("frameElement" in size_script) is expects_frame_climb

from cucu.utils import get_top_level_rect


class FakeElement:
    pass


class MockBrowser:
    def __init__(self, rect: dict):
        self._rect = rect
        self.execute_calls: list[tuple[str, tuple]] = []

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

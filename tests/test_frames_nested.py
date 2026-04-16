import pytest

from cucu.browser.core import Browser
from cucu.browser.frames import (
    search_in_all_frames_nested,
    search_in_all_frames_nested_and_deep,
    switch_to_frame_path,
)


class FakeFrame:
    def __init__(self, path: tuple[int, ...]):
        self.path = path


class MockBrowser:
    def __init__(self, children_map: dict[tuple[int, ...], list[FakeFrame]]):
        self._children_map = children_map
        self._path: tuple[int, ...] = ()
        self.switch_to_default_count = 0
        self.switch_to_frame_calls: list[FakeFrame] = []

    @property
    def frame_path(self) -> tuple[int, ...]:
        return self._path

    def switch_to_default_frame(self):
        self.switch_to_default_count += 1
        self._path = ()

    def switch_to_frame(self, frame: FakeFrame):
        self.switch_to_frame_calls.append(frame)
        self._path = frame.path

    def execute(self, javascript, *args, **kwargs):
        if "iframe" in javascript:
            return list(self._children_map[self._path])
        raise AssertionError(f"unexpected script {javascript!r}")


def test_switch_to_frame_path_follows_indices():
    f00 = FakeFrame((0, 0))
    f0 = FakeFrame((0,))
    f1 = FakeFrame((1,))
    browser = MockBrowser(
        {
            (): [f0, f1],
            (0,): [f00],
            (1,): [],
            (0, 0): [],
        }
    )

    switch_to_frame_path(browser, (0, 0))
    assert browser.frame_path == (0, 0)


def test_search_in_all_frames_nested_bfs_order():
    f00 = FakeFrame((0, 0))
    f0 = FakeFrame((0,))
    f1 = FakeFrame((1,))
    browser = MockBrowser(
        {
            (): [f0, f1],
            (0,): [f00],
            (1,): [],
            (0, 0): [],
        }
    )
    visited: list[tuple[int, ...]] = []

    def search():
        visited.append(browser.frame_path)
        return None

    search_in_all_frames_nested(browser, search)
    assert visited[0] == ()
    assert visited[1] == ()
    assert visited[2:] == [(0,), (1,), (0, 0)]


def test_search_in_all_frames_nested_respects_max_depth():
    f00 = FakeFrame((0, 0))
    f0 = FakeFrame((0,))
    browser = MockBrowser(
        {
            (): [f0, FakeFrame((1,))],
            (0,): [f00],
            (1,): [],
            (0, 0): [],
        }
    )
    visited: list[tuple[int, ...]] = []

    def search():
        visited.append(browser.frame_path)
        return None

    search_in_all_frames_nested(browser, search, max_depth=1)
    assert (0, 0) not in visited


def test_search_in_all_frames_nested_returns_first_hit():
    f00 = FakeFrame((0, 0))
    f0 = FakeFrame((0,))
    f1 = FakeFrame((1,))
    browser = MockBrowser(
        {
            (): [f0, f1],
            (0,): [f00],
            (1,): [],
            (0, 0): [],
        }
    )

    def search():
        if browser.frame_path == (1,):
            return "second-top"
        return None

    assert search_in_all_frames_nested(browser, search) == "second-top"


def test_search_in_all_frames_nested_and_deep_requires_selenium_browser():
    browser = Browser()
    with pytest.raises(TypeError):
        search_in_all_frames_nested_and_deep(browser, "div")

import pytest

from cucu.browser.frames import search_in_all_frames


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


def _three_level_browser():
    f00 = FakeFrame((0, 0))
    f0 = FakeFrame((0,))
    f1 = FakeFrame((1,))
    return MockBrowser(
        {
            (): [f0, f1],
            (0,): [f00],
            (1,): [],
            (0, 0): [],
        }
    )


def test_search_in_all_frames_nested_bfs_order():
    browser = _three_level_browser()
    visited: list[tuple[int, ...]] = []

    def search():
        visited.append(browser.frame_path)
        return None

    search_in_all_frames(browser, search, include_nested_frames=True)
    # First two calls are the initial-context and default-content searches;
    # both happen at path ().
    assert visited[0] == ()
    assert visited[1] == ()
    assert visited[2:] == [(0,), (1,), (0, 0)]


def test_search_in_all_frames_nested_respects_max_depth():
    browser = _three_level_browser()
    visited: list[tuple[int, ...]] = []

    def search():
        visited.append(browser.frame_path)
        return None

    search_in_all_frames(
        browser, search, include_nested_frames=True, max_depth=1
    )
    assert (0, 0) not in visited


def test_search_in_all_frames_max_depth_zero_skips_iframes():
    browser = _three_level_browser()
    visited: list[tuple[int, ...]] = []

    def search():
        visited.append(browser.frame_path)
        return None

    search_in_all_frames(
        browser, search, include_nested_frames=True, max_depth=0
    )
    # Only the two default-content searches; no iframe walks.
    assert visited == [(), ()]


def test_search_in_all_frames_nested_returns_first_hit():
    browser = _three_level_browser()

    def search():
        if browser.frame_path == (1,):
            return "second-top"
        return None

    assert (
        search_in_all_frames(browser, search, include_nested_frames=True)
        == "second-top"
    )


def test_search_in_all_frames_shallow_does_not_reach_nested_only_match():
    browser = _three_level_browser()

    def search():
        if browser.frame_path == (0, 0):
            return "deep"
        return None

    assert (
        search_in_all_frames(browser, search, include_nested_frames=False)
        is None
    )

    browser = _three_level_browser()
    assert (
        search_in_all_frames(browser, search, include_nested_frames=True)
        == "deep"
    )


# Parametrized tests for is_conclusive ranking (frame ranking fix)


@pytest.mark.parametrize(
    "search_results,expected_result,expected_final_path",
    [
        pytest.param(
            {
                (): None,
                (0,): ("elem_0", "label_0", 11, True),
                (1,): ("elem_1", "label_1", 500, True),
            },
            ("elem_0", "label_0", 11, True),
            (0,),
            id="conclusive-in-early-frame-stops-walk",
        ),
        pytest.param(
            {
                (): None,
                (0,): ("elem_0", "label_0", 11, False),
                (1,): ("elem_1", "label_1", 500, True),
            },
            ("elem_1", "label_1", 500, True),
            (1,),
            id="inconclusive-early-conclusive-late-chooses-conclusive",
        ),
        pytest.param(
            {
                (): None,
                (0,): ("elem_0", "label_0", 11, False),
                (1,): ("elem_1", "label_1", 200, False),
            },
            ("elem_0", "label_0", 11, False),
            (0,),
            id="inconclusive-only-returns-first-re-resolved",
        ),
        pytest.param(
            {(): None, (0,): ("elem_0", "label_0", 11, False), (1,): None},
            ("elem_0", "label_0", 11, False),
            (0,),
            id="fallback-rerun-after-no-conclusive-found",
        ),
        pytest.param(
            {(): None, (0,): ("elem_0", "label_0", 11, False), (1,): None},
            ("elem_0", "label_0", 11, False),
            (0,),
            id="is-conclusive-with-shallow-frames",
        ),
    ],
)
def test_search_in_all_frames_is_conclusive_ranking(
    search_results, expected_result, expected_final_path
):
    """Test the is_conclusive parameter that ranks matches by discovery rule."""
    browser = _three_level_browser()
    visited_paths: list[tuple[int, ...]] = []

    def search():
        path = browser.frame_path
        visited_paths.append(path)
        return search_results.get(path)

    result = search_in_all_frames(
        browser,
        search,
        include_nested_frames=True,
        is_conclusive=lambda r: (
            r[3] if isinstance(r, tuple) and len(r) == 4 else True
        ),
    )

    assert result == expected_result
    assert browser.frame_path == expected_final_path


def test_search_in_all_frames_is_conclusive_shallow():
    """Test is_conclusive with include_nested_frames=False."""
    browser = _three_level_browser()
    visited_paths: list[tuple[int, ...]] = []

    def search():
        path = browser.frame_path
        visited_paths.append(path)
        if path == ():
            return None
        if path == (0,):
            return ("elem_0", "label_0", 11, False)  # inconclusive
        return None

    result = search_in_all_frames(
        browser,
        search,
        include_nested_frames=False,
        is_conclusive=lambda r: (
            r[3] if isinstance(r, tuple) and len(r) == 4 else True
        ),
    )

    # Should visit default and top-level frames only
    assert result == ("elem_0", "label_0", 11, False)
    assert (0, 0) not in visited_paths


def test_search_in_all_frames_no_predicate_unchanged():
    """Test that behavior is unchanged when is_conclusive is not provided."""
    browser = _three_level_browser()
    visited: list[tuple[int, ...]] = []

    def search():
        visited.append(browser.frame_path)
        if browser.frame_path == (1,):
            return "found-at-frame-1"
        return None

    result = search_in_all_frames(browser, search, include_nested_frames=True)
    assert result == "found-at-frame-1"
    # With no predicate, should probe as-is and default before walking frames
    assert visited[0] == ()
    assert visited[1] == ()
    assert (1,) in visited

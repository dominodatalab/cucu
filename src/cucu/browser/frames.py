from collections import deque

from cucu.browser.core import Browser


def search_in_all_frames(browser, search_function):
    """
    search all frames on the page for an element

    Warning: This leaves the browser in whatever frame was last searched so that
    users of this method are in that frame.

    parameters:
      browser           - the cucu.browser.Browser object
      search_function   - function to search for the element (within a frame)
    returns:
        the WebElement that matches (if found)
    """
    # check whatever frame we're currently in
    result = search_function()

    if not result:
        # we might have not been in the default frame so check again
        browser.switch_to_default_frame()

        result = search_function()
        if result:
            return result

        frames = browser.execute('return document.querySelectorAll("iframe");')
        for frame in frames:
            # need to be in the default frame in order to switch to a child
            # frame w/o getting a stale element exception
            browser.switch_to_default_frame()
            browser.switch_to_frame(frame)
            result = search_function()

            if result:
                return result

    return result


def run_in_all_frames(browser, search_function):
    """
    run the search function on all of the available frames and return the
    appending of all the arrays.

    Warning: This leaves the browser in whatever frame was last searched so that
    users of this method are in that frame.

    parameters:
      browser           - the cucu.browser.Browser object
      search_function   - function that returns an array of WebElements
    returns:
        the array of all of the WebElements found.
    """
    result = []

    browser.switch_to_default_frame()
    result += search_function()

    frames = browser.execute('return document.querySelectorAll("iframe");')
    for frame in frames:
        # need to be in the default frame in order to switch to a child
        # frame w/o getting a stale element exception
        browser.switch_to_default_frame()
        browser.switch_to_frame(frame)
        result += search_function()

    return result


def try_in_frames_until_success(browser: Browser, function_to_run) -> None:
    """
    Run the function on all of the possible frames one by one. It terminates
    if the function doesn't raise an exception on a frame.

    Warning: This leaves the browser in whatever frame the function is run successfully
    so that users of the this method are in that frame.

    Args:
        browser (Browser): the browser session
        function_to_run : a function that raises an exception if it fails

    Raises:
        AssertionError: when the function fails in all frames
    """
    browser.switch_to_default_frame()
    try:
        function_to_run()
    except Exception:
        frames = browser.execute('return document.querySelectorAll("iframe");')
        for frame in frames:
            # need to be in the default frame in order to switch to a child
            # frame w/o getting a stale element exception
            browser.switch_to_default_frame()
            browser.switch_to_frame(frame)
            try:
                function_to_run()
            except Exception:
                if frames.index(frame) < len(frames) - 1:
                    continue
                else:
                    raise AssertionError(
                        f"{function_to_run.__name__} failed in all frames"
                    )
            return


def switch_to_frame_path(browser, path: tuple[int, ...]) -> None:
    """
    Switch to default content, then for each index resolve
    document.querySelectorAll("iframe") in the current document and
    switch_to.frame(iframe[index]). Re-queries iframes from the top on each
    call to reduce stale element issues.

    parameters:
      browser - the cucu.browser.Browser object
      path      - tuple of iframe indices from default content
    """
    browser.switch_to_default_frame()
    for idx in path:
        frames = browser.execute('return document.querySelectorAll("iframe");')
        browser.switch_to_frame(frames[idx])


def search_in_all_frames_nested(
    browser, search_function, *, max_depth: int = 15
):
    """
    Like search_in_all_frames, but descends into nested iframes breadth-first
    by index path from default content (up to max_depth levels).

    Warning: This leaves the browser in whatever frame was last searched so
    callers remain in that frame.

    parameters:
      browser         - the cucu.browser.Browser object
      search_function - function to run in each candidate frame (no arguments)
      max_depth       - maximum iframe depth (number of indices in a path)

    returns:
      The first truthy value returned by search_function, or the last falsy
      result if nothing matched (same convention as search_in_all_frames).
    """
    result = search_function()
    if result:
        return result

    browser.switch_to_default_frame()
    result = search_function()
    if result:
        return result

    queue = deque()
    frames = browser.execute('return document.querySelectorAll("iframe");')
    for i in range(len(frames)):
        if len((i,)) <= max_depth:
            queue.append((i,))

    while queue:
        path = queue.popleft()
        switch_to_frame_path(browser, path)
        result = search_function()
        if result:
            return result

        inner = browser.execute('return document.querySelectorAll("iframe");')
        for j in range(len(inner)):
            next_path = path + (j,)
            if len(next_path) <= max_depth:
                queue.append(next_path)

    return result


def search_in_all_frames_nested_and_deep(
    browser, selector: str, *, max_depth: int = 15
):
    """
    For each nested frame (BFS, same ordering as search_in_all_frames_nested),
    run deep_query_selector_first in that frame's document.

    Requires a Selenium-backed browser with a ``driver`` attribute.

    Warning: Leaves the browser focused on the frame where the first match
    occurred (or default content if the match was in the light DOM there).

    parameters:
      browser   - Browser with ``.driver`` (cucu Selenium)
      selector  - CSS selector passed to deep_query_selector_first
      max_depth - passed through to the nested iframe walk

    returns:
      On success: ``(element, path)`` where ``path`` is an iframe index tuple
      from default content, ``()`` when the match is in default content after
      switching to it, or ``None`` when the match is in the original browsing
      context before that switch. On failure: ``(None, None)``.
    """
    from cucu.browser.shadow import deep_query_selector_first

    try:
        driver = browser.driver
    except AttributeError as exc:
        raise TypeError(
            "search_in_all_frames_nested_and_deep requires a Selenium browser "
            "with a .driver attribute"
        ) from exc

    element = deep_query_selector_first(driver, selector)
    if element:
        return (element, None)

    browser.switch_to_default_frame()
    element = deep_query_selector_first(driver, selector)
    if element:
        return (element, ())

    queue = deque()
    frames = browser.execute('return document.querySelectorAll("iframe");')
    for i in range(len(frames)):
        if len((i,)) <= max_depth:
            queue.append((i,))

    while queue:
        path = queue.popleft()
        switch_to_frame_path(browser, path)
        element = deep_query_selector_first(driver, selector)
        if element:
            return (element, path)

        inner = browser.execute('return document.querySelectorAll("iframe");')
        for j in range(len(inner)):
            next_path = path + (j,)
            if len(next_path) <= max_depth:
                queue.append(next_path)

    return (None, None)

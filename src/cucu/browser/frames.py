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
        RuntimeError: when the function fails in all frames
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
                    raise RuntimeError(
                        f"{function_to_run.__name__} failed in all frames"
                    )
            return

from cucu import logger


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
        # we might have not been in the default frame so check agai
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

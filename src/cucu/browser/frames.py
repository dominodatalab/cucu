def search_in_all_frames(browser, search_function):
    """
    search all frames on the page for an element

    parameters:
      browser           - the cucu.browser.Browser object
      search_function   - function to search for the element (within a frame)
    returns:
        the WebElement that matches (if found)
    """
    result = search_function()

    if result is None:
        frames = browser.execute('return document.querySelectorAll("iframe");')
        for frame in frames:
            #
            # need to switch back to the default frame before switching into any
            # other inner frame otherwise the context will be wrong and we'd
            # generate a stale element exception
            #
            browser.switch_to_default_frame()
            browser.switch_to_frame(frame)
            result = search_function()

            if result is not None:
                return result

    return result

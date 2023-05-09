from cucu import logger
import pkgutil


def load_jquery_lib():
    """
    load jquery library
    """
    jquery_lib = pkgutil.get_data("cucu", "external/jquery/jquery-3.5.1.min.js")
    return jquery_lib.decode("utf8")


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


def search_text_in_all_frames(browser, search_function, value):

    try:
        search_function(value=value)
    except RuntimeError:
        # we might have not been in the default frame so check again
        browser.switch_to_default_frame()
        text = browser.execute(
            'return jQuery("body").children(":visible").text();'
        )
        try:
            search_function(value=text)
        except RuntimeError:
            frames = browser.execute(
                'return document.querySelectorAll("iframe");'
            )
            for frame in frames:
                # need to be in the default frame in order to switch to a child
                # frame w/o getting a stale element exception
                browser.switch_to_default_frame()
                browser.switch_to_frame(frame)
                browser.execute(load_jquery_lib())
                text = browser.execute(
                    'return jQuery("body").children(":visible").text();'
                )
                try:
                    search_function(value=text)
                except RuntimeError as e:
                    if frames.index(frame) < len(frames) - 1:
                        continue
                    else:
                        raise RuntimeError(e)
                return

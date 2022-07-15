def search_in_all_frames(browser, search_function):
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

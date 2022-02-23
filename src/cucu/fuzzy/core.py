import pkgutil

from enum import Enum


def load_jquery_lib():
    """
    load jquery library
    """
    jquery_lib = pkgutil.get_data('cucu',
                                  'external/jquery/jquery-3.5.1.min.js')
    return jquery_lib.decode('utf8')


def load_fuzzy_lib():
    """
    load the fuzzy javascript library
    """
    return pkgutil.get_data('cucu', 'fuzzy/fuzzy.js').decode('utf8')


def init(browser):
    """
    initializes the fuzzy matching javascript library within the currently open
    browsers execution engine

    parameters:
        browser - ...
    """
    browser.execute(load_jquery_lib())
    script = 'return window.jQuery && jQuery.fn.jquery;'
    jquery_version = browser.execute(script)

    while jquery_version is None or not jquery_version.startswith('3.5.1'):
        jquery_version = browser.execute(script)

    browser.execute(load_fuzzy_lib())


class Direction(Enum):
    """
    simple Direction enum
    """
    LEFT_TO_RIGHT = 1
    RIGHT_TO_LEFT = 2


def find(browser,
         name,
         things,
         index=0,
         direction=Direction.LEFT_TO_RIGHT):
    """
    find an element by applying the fuzzy finding rules when given the name
    that identifies the element on screen and a list of possible `things` that
    are CSS expression fragments like so:

        tag_name[attribute expression]

    That identify the kind of element you're trying to find, such as a button,
    input[type='button'], etc.

    parameters:
      browser   - the cucu.browser.Browser object
      name      - name that identifies the element you are trying to find
      things    - array of CSS fragments that specify the kind of elements you
                  want to match on
      index     - which of the many matches to return
      direction - the text to element direction to apply fuzzy in. Default we
                  apply right to left but for checkboxes or certain languages
                  this direction can be used to find things by prioritizing
                  matching from "left to right"

    returns:
        the WebElement that matches the provided arguments.
    """
    browser.switch_to_default_frame()
    init(browser)
    args = [f'"{name}"', str(things), str(index), str(direction.value)]
    script = f"return cucu.fuzzy_find({','.join(args)});"
    result = browser.execute(script)

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
            init(browser)
            args = [f'"{name}"', str(things), str(index), str(direction.value)]
            script = f"return cucu.fuzzy_find({','.join(args)});"
            result = browser.execute(script)

            if result is not None:
                return result

    return result

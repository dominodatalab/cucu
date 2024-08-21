import pkgutil
from enum import Enum

from cucu import logger
from cucu.browser.frames import search_in_all_frames


def load_jquery_lib():
    """
    load jquery library
    """
    jquery_lib = pkgutil.get_data(
        "cucu", "external/jquery/jquery-3.5.1.min.js"
    )
    return jquery_lib.decode("utf8")


def load_fuzzy_lib():
    """
    load the fuzzy javascript library
    """
    return pkgutil.get_data("cucu", "fuzzy/fuzzy.js").decode("utf8")


def init(browser):
    """
    initializes the fuzzy matching javascript library within the currently open
    browsers execution engine

    parameters:
        browser - ...
    """
    script = "return typeof cucu !== 'undefined' && typeof cucu.fuzzy_find === 'function';"
    cucu_injected = browser.execute(script)
    if cucu_injected:
        # cucu fuzzy find already exists
        return

    logger.debug("inject cucu fuzzy find library to the browser")
    jqCucu_script = "window.jqCucu = jQuery.noConflict(true);"
    browser.execute(load_jquery_lib() + jqCucu_script + load_fuzzy_lib())


class Direction(Enum):
    """
    simple Direction enum
    """

    LEFT_TO_RIGHT = 1
    RIGHT_TO_LEFT = 2


def find(
    browser,
    name,
    things,
    index=0,
    direction=Direction.LEFT_TO_RIGHT,
    name_within_thing=False,
):
    """
    find an element by applying the fuzzy finding rules when given the name
    that identifies the element on screen and a list of possible `things` that
    are CSS expression fragments like so:

        tag_name[attribute expression]

    That identify the kind of element you're trying to find, such as a button,
    input[type='button'], etc.

    parameters:
      browser           - the cucu.browser.Browser object
      name              - name that identifies the element you are trying to find
      things            - array of CSS fragments that specify the kind of elements you
                          want to match on
      index             - which of the many matches to return
      direction         - the text to element direction to apply fuzzy in. Default we
                          apply right to left but for checkboxes or certain languages
                          this direction can be used to find things by prioritizing
                          matching from "left to right"
      name_within_thing - to determine if the name has to be within the web element

    returns:
        the WebElement that matches the provided arguments.
    """
    browser.switch_to_default_frame()

    # always need to protect names in which double quotes are used as below
    # we pass arguments to the fuzzy_find javascript function wrapped in double
    # quotes
    name = name.replace('"', '\\"')
    name_within_thing = "true" if name_within_thing else "false"

    args = [
        f'"{name}"',
        str(things),
        str(index),
        str(direction.value),
        name_within_thing,
    ]

    def execute_fuzzy_find():
        init(browser)
        script = f"return cucu.fuzzy_find({','.join(args)});"
        return browser.execute(script)

    return search_in_all_frames(browser, execute_fuzzy_find)

import pkgutil
from enum import Enum

from cucu import logger
from cucu.browser.frames import search_in_all_frames
from cucu.config import CONFIG


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
    # cucu.loose_rules is part of the check so a frame still holding a
    # pre-upgrade fuzzy.js re-injects, rather than returning the older
    # 2-element result shape that find() below would index past
    script = "return typeof cucu !== 'undefined' && typeof cucu.fuzzy_find === 'function' && typeof cucu.loose_rules !== 'undefined';"
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

    # read once: the value is interpolated into the javascript call below as a
    # bare token, so a non-boolean setting (e.g. "enabled") would reach the
    # browser as an undefined identifier, and the python-side gate on ranking
    # has to agree with what the javascript actually did
    skip_relevance = CONFIG.true("CUCU_SKIP_FUZZY_RELEVANCE")

    args = [
        f'"{name}"',
        str(things),
        str(index),
        str(direction.value),
        name_within_thing,
        "true",
        str(skip_relevance).lower(),
        str(CONFIG.true("CUCU_SHADOW_DOM_SEARCH")).lower(),
        str(CONFIG.bool("CUCU_FUZZY_CASE_AWARE")).lower(),
    ]

    def execute_fuzzy_find():
        init(browser)
        script = f"return cucu.fuzzy_find({','.join(args)});"
        return browser.execute(script)

    fuzzy_return = search_in_all_frames(
        browser,
        execute_fuzzy_find,
        # when relevance is skipped the results come back in discovery order
        # rather than score order, so fuzzy_find's verdict means nothing
        is_conclusive=None if skip_relevance else lambda result: result[3],
    )
    if fuzzy_return is None:
        logger.debug("Fuzzy found no element.")
        return None
    logger.debug(
        f"Fuzzy found element by search term {fuzzy_return[1]} "
        f"(score {fuzzy_return[2]}, conclusive {fuzzy_return[3]})"
    )
    return fuzzy_return[0]

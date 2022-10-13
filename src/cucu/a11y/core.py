"""
accessibility module for finding elements on a given browser page
"""
import pkgutil
import time

from cucu import logger
from cucu.browser.frames import search_in_all_frames
from cucu.config import CONFIG
from selenium.webdriver.common.keys import Keys


def load_jquery_lib():
    """
    load jquery library
    """
    jquery_lib = pkgutil.get_data("cucu", "external/jquery/jquery-3.5.1.min.js")
    return jquery_lib.decode("utf8")


def load_a11y_lib():
    """
    load the a11y javascript library
    """
    return pkgutil.get_data("cucu", "a11y/a11y.js").decode("utf8")


def init(browser):
    """
    initializes the fuzzy matching javascript library within the currently open
    browsers execution engine

    parameters:
        browser - ...
    """
    browser.execute(load_jquery_lib())
    script = "return window.jQuery && jQuery.fn.jquery;"
    jquery_version = browser.execute(script)

    while jquery_version is None or not jquery_version.startswith("3.5.1"):
        jquery_version = browser.execute(script)

    browser.execute(load_a11y_lib())


def find(browser, name, things, attributes, index=0):
    """
    find an element by applying accessibility rules in order to find the element
    the same way a screen reader would.

    parameters:
      browser    - the cucu.browser.Browser object
      name       - name that identifies the element you are trying to find
      things     - array of CSS fragments that specify the kind of elements you
                  want to match on
      attributes - array of attribute names that the a11y find method would match
                   on
      index      - which of the many matches to return

    returns:
        the WebElement that matches the provided arguments.
    """
    # always need to protect names in which double quotes are used as below
    # we pass arguments to the fuzzy_find javascript function wrapped in double
    # quotes
    name = name.replace('"', '\\"')

    args = [
        f'"{name}"',
        str(things),
        str(attributes),
        str(index),
    ]

    def execute_a11y_find():
        init(browser)
        script = f"return cucu.a11y_find({','.join(args)});"
        return browser.execute(script)

    return search_in_all_frames(browser, execute_a11y_find)


def move_to(browser, element):
    """
    accessibility method that can take an element and the current browser
    session and move to the element using tabs only.
    """
    current_element = browser.execute("return document.activeElement;")
    first_element = current_element

    while element != current_element:
        # just the first line is logged so we don't over pollute the screen with
        # inner HTML data and we're truncating at 64 characters
        html = current_element.get_attribute("outerHTML").split("\n")[0]

        if len(html) > 64:
            html = html[0:64] + "..."

        logger.debug(f"a11y at element {html}")
        time.sleep(int(CONFIG["CUCU_INTERACTION_DELAY_S"]))

        current_element.send_keys(Keys.TAB)
        current_element = browser.execute("return document.activeElement;")

        if current_element == first_element:
            raise RuntimeError("unable to tab to the desired element")

    return current_element


def click(browser, element):
    """
    accessibility method that can take an element and the current browser
    session and "click" on that element in the same way an accessible user would
    which involves "tabbing" to the element and hitting the "enter" key on it.
    """
    current_element = move_to(browser, element)
    time.sleep(int(CONFIG["CUCU_INTERACTION_DELAY_S"]))
    html = current_element.get_attribute("outerHTML").split("\n")[0]
    logger.debug(f"a11y click on element {html}")
    current_element.send_keys(Keys.ENTER)


def write(browser, element, text):
    """
    accessibility method that can take an element and the current browser
    session and "click" on that element in the same way an accessible user would
    which involves "tabbing" to the element and hitting the "enter" key on it.
    """
    current_element = move_to(browser, element)
    time.sleep(int(CONFIG["CUCU_INTERACTION_DELAY_S"]))
    html = current_element.get_attribute("outerHTML").split("\n")[0]
    logger.debug(f"a11y write {text} into element {html}")
    current_element.send_keys(text)

import humanize
import os
import re

from cucu import config, logger, fuzzy, step
from cucu.browser.selenium import Selenium

from selenium.webdriver.common.keys import Keys


def open_browser(ctx):
    browser_name = config.CONFIG["CUCU_BROWSER"]
    headless = config.CONFIG["CUCU_BROWSER_HEADLESS"]
    selenium_remote_url = config.CONFIG["CUCU_SELENIUM_REMOTE_URL"]

    browser = Selenium()
    logger.debug(f"opening browser {browser_name}")
    browser.open(
        browser_name, headless=headless, selenium_remote_url=selenium_remote_url
    )

    return browser


@step('I open a browser at the url "{url}"')
def open_a_browser(ctx, url):
    """
    open a browser at the url provided

    example:
        Given I open a browser at the url "https://www.google.com"
    """
    if ctx.browser is None:
        ctx.browser = open_browser(ctx)
        ctx.browsers.append(ctx.browser)
    else:
        logger.debug("browser already open so using existing instance")

    logger.debug(f"navigating to url #{url}")
    ctx.browser.navigate(url)
    fuzzy.init(ctx.browser)


@step('I open a new browser at the url "{url}"')
def open_a_new_browser(ctx, url):
    ctx.browser = open_browser(ctx)
    ctx.browsers.append(ctx.browser)
    logger.debug(f"navigating to url #{url}")
    ctx.browser.navigate(url)
    fuzzy.init(ctx.browser)


@step("I execute in the current browser the following javascript")
def execute_javascript(ctx):
    ctx.browser.execute(ctx.text)


@step(
    'I execute in the current browser the following javascript and save the result to the variable "{variable}"'
)
def execute_javascript_and_save(ctx, variable):
    result = ctx.browser.execute(ctx.text)
    config.CONFIG[variable] = result


@step('I save the current url to the variable "{variable}"')
def save_current_url_to_variable(ctx, variable):
    config.CONFIG[variable] = ctx.browser.get_current_url()


@step("I refresh the browser")
def refresh_browser(ctx):
    ctx.browser.refresh()


@step("I go back on the browser")
def go_back_on_browser(ctx):
    ctx.browser.back()


@step('I save the contents of the clipboard to the variable "{variable}"')
def save_clipboard_value_to_variable(ctx, variable):
    # create the hidden textarea so we can paste clipboard contents in
    ctx.browser.execute(
        """
    var textarea = document.getElementById('cucu-copy-n-paste')
    if (!textarea) {
        textarea = document.createElement('textarea');
        textarea.setAttribute('id', 'cucu-copy-n-paste');
        textarea.style.display = 'hidden';
        textarea.style.height = '0px';
        textarea.style.width = '0px';
        document.body.appendChild(textarea);
    }
    """
    )
    # send ctrl+v or cmd+v to that element
    textarea = ctx.browser.css_find_elements("#cucu-copy-n-paste")[0]

    if "mac" in ctx.browser.execute("return navigator.platform").lower():
        textarea.send_keys(Keys.COMMAND, "v")
    else:
        textarea.send_keys(Keys.CONTROL, "v")

    clipboard_contents = textarea.get_attribute("value")
    config.CONFIG[variable] = clipboard_contents


@step('I should see the browser title is "{title}"')
def should_see_browser_title(ctx, title):
    current_title = ctx.browser.title()

    if current_title != title:
        raise RuntimeError(f'unexpected browser title, got "{current_title}"')


@step("I close the current browser")
def close_browser(ctx):
    browser_index = ctx.browsers.index(ctx.browser)

    if browser_index > 0:
        ctx.browser = ctx.browsers[browser_index - 1]
    else:
        ctx.current_borwser = None

    del ctx.browsers[browser_index]


@step('I navigate to the url "{url}"')
def navigate_to_the_url(ctx, url):
    logger.debug(f"navigating to url #{url}")
    ctx.browser.navigate(url)


@step("I switch to the previous browser")
def switch_to_previous_browser(ctx):
    browser_index = ctx.browsers.index(ctx.browser)

    if browser_index > 0:
        ctx.browser = ctx.browsers[browser_index - 1]
    else:
        raise RuntimeError("no previous browser window available")


@step("I switch to the next browser")
def switch_to_next_browser(ctx):
    browser_index = ctx.browsers.index(ctx.browser)

    if browser_index < len(ctx.browsers) - 1:
        ctx.browser = ctx.browsers[browser_index + 1]
    else:
        raise RuntimeError("no next browser window available")


@step("I close the current browser tab")
def close_browser_tab(ctx):
    ctx.browser.close_window()


@step("I switch to the next browser tab")
def switch_to_next_browser_tab(ctx):
    ctx.browser.switch_to_next_tab()


@step("I switch to the previous browser tab")
def switch_to_previous_browser_tab(ctx):
    ctx.browser.switch_to_previous_tab()


def find_file_input(ctx, name, index=0):
    """

        * <input type="file">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired button on screen
      index(str):  the index of the button if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    input = fuzzy.find(ctx.browser, name, ['input[type="file"]'], index=index)

    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    if input is None:
        raise RuntimeError(f'unable to find the {prefix}file input "{name}"')

    return input


@step('I upload the file "{filepath}" to the file input "{name}"')
def upload_file_to_input(ctx, filepath, name):
    input = find_file_input(ctx, name)
    input.send_keys(os.path.abspath(filepath))

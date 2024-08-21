import base64
import os

from selenium.webdriver.common.keys import Keys

from cucu import config, logger, retry, run_steps, step
from cucu.browser.selenium import Selenium


def open_browser(ctx):
    browser_name = config.CONFIG["CUCU_BROWSER"]
    headless = config.CONFIG["CUCU_BROWSER_HEADLESS"]
    selenium_remote_url = config.CONFIG["CUCU_SELENIUM_REMOTE_URL"]

    browser = Selenium()
    logger.debug(f"opening browser {browser_name}")
    browser.open(
        browser_name,
        headless=headless,
        selenium_remote_url=selenium_remote_url,
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


@step('I open a new browser at the url "{url}"')
def open_a_new_browser(ctx, url):
    ctx.browser = open_browser(ctx)
    ctx.browsers.append(ctx.browser)
    logger.debug(f"navigating to url #{url}")
    ctx.browser.navigate(url)


@step("I execute in the current browser the following javascript")
def execute_javascript(ctx):
    ctx.check_browser_initialized()
    ctx.browser.execute(ctx.text)


@step(
    'I execute in the current browser the following javascript and save the result to the variable "{variable}"'
)
def execute_javascript_and_save(ctx, variable):
    ctx.check_browser_initialized()
    result = ctx.browser.execute(ctx.text)
    config.CONFIG[variable] = result


def assert_url_is(ctx, value):
    ctx.check_browser_initialized()
    url = ctx.browser.get_current_url()
    if value == url:
        raise RuntimeError(f"current url is {url}, not {value}")


@step('I should see the current url is "{value}"')
def should_see_the_current_url_is(ctx, value):
    assert_url_is(ctx, value)


@step('I wait to see the current url is "{value}"')
def wait_to_see_the_current_url_is(ctx, value):
    retry(assert_url_is)(ctx, value)


@step('I save the current url to the variable "{variable}"')
def save_current_url_to_variable(ctx, variable):
    ctx.check_browser_initialized()
    config.CONFIG[variable] = ctx.browser.get_current_url()


@step("I refresh the browser")
def refresh_browser(ctx):
    ctx.check_browser_initialized()
    ctx.browser.refresh()


@step("I go back on the browser")
def go_back_on_browser(ctx):
    ctx.check_browser_initialized()
    ctx.browser.back()


@step('I save the contents of the clipboard to the variable "{variable}"')
def save_clipboard_value_to_variable(ctx, variable):
    ctx.check_browser_initialized()

    # use default frame when adding elements to the document to avoid this errro on access:
    # "selenium.common.exceptions.ElementNotInteractableException: Message: element not interactable"
    ctx.browser.switch_to_default_frame()

    # create the hidden textarea so we can paste clipboard contents in
    textarea = ctx.browser.execute(
        """
    var textarea = document.getElementById('cucu-copy-n-paste')
    if (!textarea) {
        textarea = document.createElement('textarea');
        textarea.setAttribute('id', 'cucu-copy-n-paste');
        textarea.style.display = 'hidden';
        textarea.style.height = '0px';
        textarea.style.width = '0px';
        document.body.insertBefore(textarea, document.body.firstChild);
    }
    return textarea;
    """
    )

    # send ctrl+v or cmd+v to that element
    if "mac" in ctx.browser.execute("return navigator.platform").lower():
        textarea.send_keys(Keys.COMMAND, "v")
    else:
        textarea.send_keys(Keys.CONTROL, "v")

    clipboard_contents = textarea.get_attribute("value")
    config.CONFIG[variable] = clipboard_contents


@step('I should see the browser title is "{title}"')
def should_see_browser_title(ctx, title):
    ctx.check_browser_initialized()
    current_title = ctx.browser.title()

    if current_title != title:
        raise RuntimeError(f'unexpected browser title, got "{current_title}"')


@step("I close the current browser")
def close_browser(ctx):
    ctx.check_browser_initialized()
    browser_index = ctx.browsers.index(ctx.browser)

    if browser_index > 0:
        ctx.browser = ctx.browsers[browser_index - 1]
    else:
        ctx.browser = None

    ctx.browsers[browser_index].quit()
    del ctx.browsers[browser_index]


@step('I navigate to the url "{url}"')
def navigate_to_the_url(ctx, url):
    ctx.check_browser_initialized()
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
    ctx.check_browser_initialized()
    ctx.browser.close_window()


def switch_to_next_tab(ctx):
    ctx.check_browser_initialized()
    ctx.browser.switch_to_next_tab()


@step("I switch to the next browser tab")
def switch_to_next_browser_tab(ctx):
    switch_to_next_tab(ctx)


@step("I wait to switch to the next browser tab")
def wait_to_switch_to_next_browser_tab(ctx):
    retry(switch_to_next_tab)(ctx)


def switch_to_previous_tab(ctx):
    ctx.check_browser_initialized()
    ctx.browser.switch_to_previous_tab()


@step("I switch to the previous browser tab")
def switch_to_previous_browser_tab(ctx):
    switch_to_previous_tab(ctx)


@step("I wait to switch to the previous browser tab")
def wait_to_switch_to_previous_browser_tab(ctx):
    retry(switch_to_previous_tab)(ctx)


def save_downloaded_file(ctx, filename):
    ctx.check_browser_initialized()

    # use default frame when adding elements to the document to avoid this errro on access:
    # "selenium.common.exceptions.ElementNotInteractableException: Message: element not interactable"
    ctx.browser.switch_to_default_frame()

    elem = ctx.browser.execute(
        """
        var input = window.document.createElement('INPUT');
        input.setAttribute('type', 'file');
        input.hidden = true;
        input.onchange = function (e) { e.stopPropagation() };
        return window.document.documentElement.appendChild(input);
        """
    )
    cucu_downloads_dir = config.CONFIG["CUCU_BROWSER_DOWNLOADS_DIR"]
    elem.send_keys(f"{cucu_downloads_dir}/{filename}")
    ctx.browser.execute(
        """
        var input = arguments[0];
        window.__cucu_downloaded_file = null;
        var reader = new FileReader();
        reader.onload = function (ev) {
            window.__cucu_downloaded_file = reader.result;
        };
        reader.onerror = function (ex) {
            window.__cucu_downloaded_file = ex.message;
        };
        reader.readAsDataURL(input.files[0]);
        input.remove();
        """,
        elem,
    )

    def wait_for_file():
        if (
            ctx.browser.execute("return window.__cucu_downloaded_file;")
            is None
        ):
            raise RuntimeError(f"waiting on file {filename}")

    retry(wait_for_file)()

    result = ctx.browser.execute("return window.__cucu_downloaded_file;")
    if not result.startswith("data:"):
        raise Exception("Failed to get file content: %s" % result)

    filedata = base64.b64decode(result[result.find("base64,") + 7 :])
    scenario_downloads_dir = config.CONFIG["SCENARIO_DOWNLOADS_DIR"]
    download_filepath = os.path.join(scenario_downloads_dir, filename)
    open(download_filepath, "wb").write(filedata)


@step('I wait to see the downloaded file "{filename}"')
def wait_to_see_downloaded_file(ctx, filename):
    """
    wait to see the expected downloaded filename appears in the current
    browsers download directory and internally we then copy the contents of
    that file to the SCENARIO_DOWNLOADS_DIR so the test can continue to
    use the file as it deems necessary.
    """
    retry(save_downloaded_file)(ctx, filename)


@step(
    'I wait up to "{seconds}" seconds to see the downloaded file "{filename}"'
)
def wait_up_to_seconds_to_see_downloaded_file(ctx, seconds, filename):
    seconds = float(seconds)
    retry(save_downloaded_file, wait_up_to_s=seconds)(ctx, filename)


@step('I download an mht archive of the current page to "{file_path}"')
def download_mht_archive(ctx, file_path):
    ctx.browser.download_mht(file_path)


@step('I run the following steps if the current browser is "{name}"')
def run_if_browser(ctx, name):
    if config.CONFIG["CUCU_BROWSER"].lower() == name.lower():
        run_steps(ctx, ctx.text)


@step('I do not run the following steps if the current browser is "{name}"')
def run_if_not_browser(ctx, name):
    if config.CONFIG["CUCU_BROWSER"].lower() != name.lower():
        run_steps(ctx, ctx.text)


@step('I skip this scenario if the current browser is "{name}"')
def skip_if_browser(ctx, name):
    if config.CONFIG["CUCU_BROWSER"].lower() == name.lower():
        ctx.scenario.skip(reason=f"skipping scenario since we're on {name}")


@step('I skip this scenario if the current browser is not "{name}"')
def skip_if_not_browser(ctx, name):
    if config.CONFIG["CUCU_BROWSER"].lower() != name.lower():
        ctx.scenario.skip(
            reason=f"skipping scenario since we're not on {name}"
        )


@step('I save the browser cookie "{cookie_name}" to the variable "{variable}"')
def save_browser_cookie(ctx, cookie_name, variable):
    ctx.check_browser_initialized()
    config.CONFIG[variable] = ctx.browser.driver.get_cookie(cookie_name)[
        "value"
    ]


@step('I set the browser cookie "{name}" a value of "{value}"')
def add_browser_cookie(ctx, name, value):
    ctx.check_browser_initialized()
    ctx.browser.driver.add_cookie({"name": name, "value": value})

import parse
import re

from behave import step, register_type
from cucu import config, logger, fuzzy
from cucu.browser.selenium import Selenium

from selenium.webdriver.common.keys import Keys

NTH_REGEX = r'(\d+)(nd|th|rd|st)'


@parse.with_pattern(NTH_REGEX)
def parse_nth(nth):
    matcher = re.match(NTH_REGEX, nth)

    if matcher is None:
        raise Exception(f'nth expression {nth} is invalid')

    number, _ = matcher.groups()
    return int(number) - 1


register_type(nth=parse_nth)


def open_browser(context, url):
    browser_name = config.CONFIG['CUCU_BROWSER']
    headless = config.CONFIG['CUCU_BROWSER_HEADLESS']
    selenium_remote_url = config.CONFIG['CUCU_SELENIUM_REMOTE_URL']

    browser = Selenium()
    logger.debug(f'opening browser {browser_name}')
    browser.open(browser_name,
                 headless=headless,
                 selenium_remote_url=selenium_remote_url)

    return browser


@step('I open a browser at the url "{url}"')
def open_a_browser(context, url):
    if context.browser is None:
        context.browser = open_browser(context, url)
        context.browsers.append(context.browser)
    else:
        logger.debug('browser already open so using existing instance')

    logger.debug(f'navigating to url #{url}')
    context.browser.navigate(url)
    fuzzy.init(context.browser.execute)


@step('I open a new browser at the url "{url}"')
def open_a_new_browser(context, url):
    context.browser = open_browser(context, url)
    context.browsers.append(context.browser)
    logger.debug(f'navigating to url #{url}')
    context.browser.navigate(url)
    fuzzy.init(context.browser.execute)


@step('I refresh the browser')
def refresh_browser(context):
    context.browser.refresh()


@step('I save the contents of the clipboard to the variable "{variable}"')
def save_clipboard_value_to_variable(context, variable):
    # create the hidden textarea so we can paste clipboard contents in
    context.browser.execute("""
    var textarea = document.getElementById('cucu-copy-n-paste')
    if (!textarea) {
        textarea = document.createElement('textarea');
        textarea.setAttribute('id', 'cucu-copy-n-paste');
        textarea.style.display = 'hidden';
        textarea.style.height = '0px';
        textarea.style.width = '0px';
        document.body.appendChild(textarea);
    }
    """)
    # send ctrl+v or cmd+v to that element
    textarea = context.browser.css_find_elements('#cucu-copy-n-paste')[0]
    textarea.send_keys(Keys.CONTROL, 'v')
    textarea.send_keys(Keys.COMMAND, 'v')

    clipboard_contents = textarea.get_attribute('value')
    config.CONFIG[variable] = clipboard_contents


@step('I should see the browser title is "{title}"')
def should_see_browser_title(context, title):
    current_title = context.browser.title()

    if current_title != title:
        raise RuntimeError(f'expected title: {title}, got {current_title}')


@step('I close the current browser')
def close_browser(context):
    browser_index = context.browsers.index(context.browser)

    if browser_index > 0:
        context.browser = context.browsers[browser_index - 1]
    else:
        context.current_borwser = None

    del context.browsers[browser_index]


@step('I navigate to the url "{url}"')
def navigate_to_the_url(context, url):
    logger.debug(f'navigating to url #{url}')
    context.browser.navigate(url)


@step('I switch to the previous browser')
def switch_to_previous_browser(context):
    browser_index = context.browsers.index(context.browser)

    if browser_index > 0:
        context.browser = context.browsers[browser_index - 1]
    else:
        raise RuntimeError('no previous browser window available')


@step('I switch to the next browser')
def switch_to_next_browser(context):
    browser_index = context.browsers.index(context.browser)

    if browser_index < len(context.browsers) - 1:
        context.browser = context.browsers[browser_index + 1]
    else:
        raise RuntimeError('no previous browser window available')


@step('I switch to the next tab')
def switch_to_next_tab(context):
    context.browser.switch_to_next_tab()


@step('I switch to the previous tab')
def switch_to_previous_tab(context):
    context.browser.switch_to_previous_tab()

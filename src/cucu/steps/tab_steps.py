from behave import step

from cucu import fuzzy


def find_tab(context, name, index=0):
    """
    find a tab containing the text provide.

    parameters:
      context - behave context object passed to a behave step
      name    - name that identifies the desired tab
      index   - the index of the element if there are a few with the same name.

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(context.browser,
                      name,
                      ['*[role="tab"]'],
                      index=index)


@step('I should see the tab "{name}"')
def should_see_the_tab(context, name):
    tab = find_tab(context, name)

    if tab is None:
        raise Exception(f'unable to find the tab "{name}"')


@step('I should see the tab "{name}" is selected')
def should_see_the_tab_is_selected(context, name):
    tab = find_tab(context, name)

    if tab is None:
        raise Exception(f'unable to find the tab "{name}"')

    if tab.get_attribute('aria-selected') != 'true':
        raise RuntimeError(f'tab "{name}" not selected')


@step('I should see the tab "{name}" is not selected')
def should_see_the_tab_is_not_selected(context, name):
    tab = find_tab(context, name)

    if tab is None:
        raise Exception(f'unable to find the tab "{name}"')

    if tab.get_attribute('aria-selected') == 'true':
        raise RuntimeError(f'tab "{name}" is selected')


@step('I wait to see the menu item "{name}"', wait_for=True)
def waits_toshould_see_the_menu_item(context, name):
    tab = find_tab(context, name)

    if tab is None:
        raise Exception(f'unable to find the tab "{name}"')


@step('I click the tab "{name}"')
def click_tab(context, name):
    tab = find_tab(context, name)

    if tab is None:
        raise Exception(f'unable to find the tab "{name}"')

    tab.click()


@step('I wait to click the tab "{name}"', wait_for=True)
def wait_to_click_tab(context, name):
    tab = find_tab(context, name)

    if tab is None:
        raise Exception(f'unable to find the tab "{name}"')

    tab.click()

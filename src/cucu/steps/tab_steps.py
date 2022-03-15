from cucu import fuzzy, retry, step


def find_tab(ctx, name, index=0):
    """
    find a tab containing the text provide.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired tab on screen
      index(str):  the index of the tab if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(ctx.browser,
                      name,
                      ['*[role="tab"]'],
                      index=index)


def find_n_assert_tab(ctx, name, index=0):
    """
    find and assert tab is visible

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired tab on screen
      index(str):  the index of the tab if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    tab = find_tab(ctx, name)

    if tab is None:
        raise Exception(f'unable to find the tab "{name}"')

    return tab


def assert_tab_selected(ctx, name, index=0, is_selected=True):
    """
    assert tab is selected

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired tab on screen
      index(str):  the index of the tab if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """

    tab = find_n_assert_tab(ctx, name)

    if is_selected:
        if tab.get_attribute('aria-selected') != 'true':
            raise RuntimeError(f'tab "{name}" is not selected')
    else:
        if tab.get_attribute('aria-selected') == 'true':
            raise RuntimeError(f'tab "{name}" is selected')


def find_n_click_tab(ctx, name):
    tab = find_n_assert_tab(ctx, name)
    tab.click()


@step('I should see the tab "{name}"')
def should_see_the_tab(ctx, name):
    find_n_assert_tab(ctx, name)


@step('I wait to see the tab "{name}"')
def wait_to_see_the_tab(ctx, name):
    retry(find_n_assert_tab)(ctx, name)


@step('I should see the tab "{name}" is selected')
def should_see_the_tab_is_selected(ctx, name):
    assert_tab_selected(ctx, name, is_selected=True)


@step('I wait to see the tab "{name}" is selected')
def wait_to_see_the_tab_is_selected(ctx, name):
    retry(assert_tab_selected)(ctx, name, is_selected=True)


@step('I should see the tab "{name}" is not selected')
def should_see_the_tab_is_not_selected(ctx, name):
    assert_tab_selected(ctx, name, is_selected=False)


@step('I wait to see the tab "{name}" is not selected')
def wait_to_see_the_tab_is_not_selected(ctx, name):
    retry(assert_tab_selected)(ctx, name, is_selected=False)


@step('I click the tab "{name}"')
def click_tab(ctx, name):
    find_n_click_tab(ctx, name)


@step('I wait to click the tab "{name}"')
def wait_to_click_tab(ctx, name):
    retry(find_n_click_tab)(ctx, name)

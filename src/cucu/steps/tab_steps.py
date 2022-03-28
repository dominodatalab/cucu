from cucu import helpers, fuzzy, retry, step


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
    return fuzzy.find(ctx.browser, name, ['*[role="tab"]'], index=index)


def click_tab(tab):
    tab.click()


def is_selected(tab):
    return tab.get_attribute("aria-selected") == "true"


def is_not_selected(tab):
    return not is_selected(tab)


helpers.define_should_see_thing_with_name_steps("tab", find_tab)
helpers.define_action_on_thing_with_name_steps(
    "tab", "click", find_tab, click_tab
)
helpers.define_thing_with_name_in_state_steps(
    "tab", "selected", find_tab, is_selected
)
helpers.define_thing_with_name_in_state_steps(
    "tab", "not selected", find_tab, is_not_selected
)

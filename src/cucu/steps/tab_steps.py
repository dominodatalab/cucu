from cucu import fuzzy, helpers
from cucu.utils import take_saw_element_screenshot

from . import base_steps


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
    ctx.check_browser_initialized()
    element = fuzzy.find(ctx.browser, name, ['*[role="tab"]'], index=index)

    take_saw_element_screenshot(ctx, "tab", name, index, element)

    return element


def click_tab(ctx, tab):
    """
    internal method to click a tab
    """
    ctx.check_browser_initialized()

    if base_steps.is_disabled(tab):
        raise RuntimeError("unable to click the tab, as it is disabled")

    ctx.browser.click(tab)


def is_selected(tab):
    """
    internal method to check if a tab is currently selected
    """
    return tab.get_attribute("aria-selected") == "true"


def is_not_selected(tab):
    """
    internal method to check if a tab is currently not selected
    """
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
helpers.define_thing_with_name_in_state_steps(
    "tab", "disabled", find_tab, base_steps.is_disabled
)
helpers.define_thing_with_name_in_state_steps(
    "tab", "not disabled", find_tab, base_steps.is_not_disabled
)

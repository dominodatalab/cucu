#
# menuitem steps
# https://www.w3.org/TR/wai-aria-1.1/#menuitem
#
from cucu import helpers, fuzzy
from . import base_steps


def find_menuitem(ctx, name, index=0):
    """
    find a menuitem containing the menuitem provide.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired menuitem on screen
      index(str):  the index of the menuitem if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()
    return fuzzy.find(ctx.browser, name, ['*[role="menuitem"]'], index=index)


helpers.define_should_see_thing_with_name_steps("menu item", find_menuitem)
helpers.define_thing_with_name_in_state_steps(
    "menu item", "disabled", find_menuitem, base_steps.is_disabled
)
helpers.define_thing_with_name_in_state_steps(
    "menu item", "not disabled", find_menuitem, base_steps.is_not_disabled
)

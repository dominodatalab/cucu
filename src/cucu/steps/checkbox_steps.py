from cucu import fuzzy, helpers
from cucu.utils import take_saw_element_screenshot

from . import base_steps


def find_checkbox(ctx, name, index=0):
    """
    find a checkbox on screen using name and index provided

        * <input type="checkbox">
        * <* role="checkbox">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired checkbox on screen
      index(str):  the index of the checkbox if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()

    element = fuzzy.find(
        ctx.browser,
        name,
        [
            'input[type="checkbox"]',
            '*[role="checkbox"]',
        ],
        index=index,
        direction=fuzzy.Direction.RIGHT_TO_LEFT,
    )

    take_saw_element_screenshot(ctx, "checkbox", name, index, element)

    return element


def is_checked(checkbox):
    """
    internal method to check a checkbox is checked
    """
    return (
        checkbox.get_attribute("checked")
        or checkbox.get_attribute("aria-checked") == "true"
    )


def is_not_checked(checkbox):
    """
    internal method to check a checkbox is not checked
    """
    return not is_checked(checkbox)


def check_checkbox(ctx, checkbox):
    """
    internal method used to check a checkbox if it is not already checked
    """
    ctx.check_browser_initialized()

    if is_checked(checkbox):
        raise Exception("checkbox already checked")

    if base_steps.is_disabled(checkbox):
        raise RuntimeError("unable to check the checkbox, as it is disabled")

    ctx.browser.click(checkbox)


def uncheck_checkbox(ctx, checkbox):
    """
    internal method used to uncheck a checkbox if it is not already unchecked
    """
    ctx.check_browser_initialized()

    if is_not_checked(checkbox):
        raise Exception("checkbox already unchecked")

    ctx.browser.click(checkbox)


helpers.define_should_see_thing_with_name_steps("checkbox", find_checkbox)
helpers.define_action_on_thing_with_name_steps(
    "checkbox", "check", find_checkbox, check_checkbox
)
helpers.define_action_on_thing_with_name_steps(
    "checkbox", "uncheck", find_checkbox, uncheck_checkbox
)
helpers.define_thing_with_name_in_state_steps(
    "checkbox", "checked", find_checkbox, is_checked
)
helpers.define_thing_with_name_in_state_steps(
    "checkbox", "not checked", find_checkbox, is_not_checked
)
helpers.define_thing_with_name_in_state_steps(
    "checkbox", "disabled", find_checkbox, base_steps.is_disabled
)
helpers.define_thing_with_name_in_state_steps(
    "checkbox", "not disabled", find_checkbox, base_steps.is_not_disabled
)
helpers.define_run_steps_if_I_can_see_element_with_name_steps(
    "checkbox", find_checkbox
)
helpers.define_ensure_state_on_thing_with_name_steps(
    "checkbox", "checked", find_checkbox, is_checked, check_checkbox
)
helpers.define_ensure_state_on_thing_with_name_steps(
    "checkbox", "not checked", find_checkbox, is_not_checked, uncheck_checkbox
)

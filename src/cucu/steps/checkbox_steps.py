import humanize

from cucu import helpers, fuzzy, retry, step


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
    return fuzzy.find(
        ctx.browser,
        name,
        [
            'input[type="checkbox"]',
            '*[role="checkbox"]',
        ],
        index=index,
        direction=fuzzy.Direction.RIGHT_TO_LEFT,
    )


def is_checked(checkbox):
    return checkbox.get_attribute("checked") == "true"


def is_not_checked(checkbox):
    return not (is_checked(checkbox))


def check_checkbox(checkbox):
    """ """
    if is_checked(checkbox):
        raise Exception("checkbox already checked")

    checkbox.click()


def uncheck_checkbox(checkbox):
    """ """
    if is_not_checked(checkbox):
        raise Exception("checkbox already unchecked")

    checkbox.click()


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

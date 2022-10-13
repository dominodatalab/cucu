from cucu import a11y, helpers, fuzzy, logger
from . import base_steps


def find_button(ctx, name, index=0):
    """
    find a button on screen using fuzzy or a11y matching

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired button on screen
      index(str):  the index of the button if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()

    if ctx.a11y_mode:
        button = a11y.find(
            ctx.browser,
            name,
            [
                "button",
                'input[type="button"]',
                'input[type="submit"]',
                "a",
                '*[role="button"]',
                '*[role="link"]',
                '*[role="menuitem"]',
                '*[role="treeitem"]',
                '*[role="option"]',
                '*[role="radio"]',
            ],
            ["aria-label", "title", "value"],
            index=index,
        )

    else:
        button = fuzzy.find(
            ctx.browser,
            name,
            [
                "button",
                'input[type="button"]',
                'input[type="submit"]',
                "a",
                '*[role="button"]',
                '*[role="link"]',
                '*[role="menuitem"]',
                '*[role="treeitem"]',
                '*[role="option"]',
                '*[role="radio"]',
            ],
            index=index,
        )

    return button


def click_button(ctx, button):
    """
    internal method used to simply click a button element
    """
    ctx.check_browser_initialized()

    if base_steps.is_disabled(button):
        raise RuntimeError("unable to click the button, as it is disabled")

    if ctx.a11y_mode:
        a11y.click(ctx.browser, button)

    else:
        ctx.browser.click(button)


helpers.define_should_see_thing_with_name_steps(
    "button", find_button, with_nth=True
)
helpers.define_action_on_thing_with_name_steps(
    "button", "click", find_button, click_button, with_nth=True
)
helpers.define_thing_with_name_in_state_steps(
    "button", "disabled", find_button, base_steps.is_disabled
)
helpers.define_thing_with_name_in_state_steps(
    "button", "not disabled", find_button, base_steps.is_not_disabled
)
helpers.define_run_steps_if_I_can_see_element_with_name_steps(
    "button", find_button
)

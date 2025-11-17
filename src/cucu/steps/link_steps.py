from cucu import fuzzy, helpers
from cucu.utils import take_saw_element_screenshot

from . import base_steps


def find_link(ctx, name, index=0):
    """
    find a link on screen by fuzzy matching on the name provided and the target
    element:

        * <a>
        * <* role="link">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired link on screen
      index(str):  the index of the link if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()
    element = fuzzy.find(
        ctx.browser, name, ["a", '*[role="link"]'], index=index
    )

    take_saw_element_screenshot(ctx, "link", name, index, element)

    return element


def click_link(ctx, link):
    """
    internal method to click a link
    """
    ctx.check_browser_initialized()

    if base_steps.is_disabled(link):
        raise RuntimeError("unable to click the link, as it is disabled")

    ctx.browser.click(link)


helpers.define_should_see_thing_with_name_steps(
    "link", find_link, with_nth=True
)
helpers.define_action_on_thing_with_name_steps(
    "link", "click", find_link, click_link, with_nth=True
)
helpers.define_thing_with_name_in_state_steps(
    "link", "disabled", find_link, base_steps.is_disabled, with_nth=True
)
helpers.define_thing_with_name_in_state_steps(
    "link",
    "not disabled",
    find_link,
    base_steps.is_not_disabled,
    with_nth=True,
)
helpers.define_run_steps_if_I_can_see_element_with_name_steps(
    "link", find_link
)

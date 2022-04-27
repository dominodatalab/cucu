from cucu import helpers, fuzzy
from . import base_steps


def find_button(ctx, name, index=0):
    """
    find a button on screen by fuzzy matching on the name and index provided.

        * <button>
        * <input type="button">
        * <input type="submit">
        * <a>
        * <* role="button">
        * <* role="link">
        * <* role="menuitem">
        * <* role="treetem">
        * <* role="option">
        * <* role="radio">

    note: the reason we're allowing other items such as menuitem, option, etc
          is that on screen they can present themselves like "buttons". When
          searching for more things to include use the following image
          reference:

          https://www.w3.org/TR/2009/WD-wai-aria-20091215/rdf_model.png

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired button on screen
      index(str):  the index of the button if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
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

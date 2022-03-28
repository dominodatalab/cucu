import humanize

from cucu import helpers, fuzzy, retry, step


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
        * <* role="option">
        * <* role="radio">

    note: the reason we're allowing link, menuitem, option and radio buttons
          to be clickable is that on screen they may simply look like a button.

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
            '*[role="option"]',
        ],
        index=index,
    )

    return button


def click_button(button):
    button.click()


helpers.define_should_see_thing_with_name_steps(
    "button", find_button, with_nth=True
)
helpers.define_action_on_thing_with_name_steps(
    "button", "click", find_button, click_button, with_nth=True
)

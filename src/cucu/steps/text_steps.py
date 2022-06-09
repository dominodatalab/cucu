from cucu import helpers, fuzzy, retry, step


def find_text(ctx, name, index=0):
    """
    find any element containing the text provide.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired radio text on screen
      index(str):  the index of the radio text if there are duplicates

    returns:
        the WebElement that matches the provided arguments or None if none found
    """
    return fuzzy.find(
        ctx.browser,
        name,
        ["*"],
        index=index,
        direction=fuzzy.Direction.LEFT_TO_RIGHT,
    )


helpers.define_should_see_thing_with_name_steps("text", find_text)
helpers.define_run_steps_if_I_can_see_element_with_name_steps("text", find_text)

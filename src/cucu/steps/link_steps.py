from cucu import helpers, fuzzy, retry, step


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
    return fuzzy.find(ctx.browser, name, ["a", '*[role="link"]'], index=index)


helpers.define_should_see_thing_with_name_steps("link", find_link)
helpers.define_action_on_thing_with_name_steps(
    "link", "click", find_link, lambda link: link.click()
)

from cucu import helpers, retry, step, fuzzy


def find_image(ctx, name, index=0):
    """
    find an input on screen by fuzzy matching on the name provided and the
    target element:

        * <img>

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired image on screen
      index(str):  the index of the image if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(
        ctx.browser,
        name,
        ["img"],
        index=index,
        attributes=["alt"]
    )


helpers.define_should_see_thing_with_name_steps(
    "image with the alt text", find_image
)

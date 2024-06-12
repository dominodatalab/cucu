from cucu import helpers
from cucu.utils import take_saw_element_screenshot


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
    ctx.check_browser_initialized()

    name = name.replace('"', '\\"')
    images = ctx.browser.css_find_elements(f'img[alt="{name}"')

    if index >= len(images):
        return None

    element = images[index]

    take_saw_element_screenshot(ctx, "image", name, index, element)

    return element


helpers.define_should_see_thing_with_name_steps(
    "image with the alt text", find_image
)

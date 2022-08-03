from cucu import helpers, retry, step, fuzzy
from cucu.browser.frames import search_in_all_frames


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

    def find_image_in_current_frame():
        image = None
        images = ctx.browser.css_find_elements(f'img[alt="{name}"')

        if len(images) > index:
            image = images[index]

        return image

    return search_in_all_frames(ctx.browser, find_image_in_current_frame)


helpers.define_should_see_thing_with_name_steps(
    "image with the alt text", find_image
)

from cucu import retry, step


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
    image = None
    imgs = ctx.browser.css_find_elements(f'img[alt="{name}"')

    if len(imgs) > index:
        image = imgs[index]

    return image


def assert_image(ctx, name, index=0, is_visible=True):
    """
    assert image is visible

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired image on screen
      index(str):  the index of the image if there are duplicates
    """

    image = find_image(ctx, name, index=index)

    if is_visible:
        if image is None:
            raise RuntimeError(f'unable to find image with alt text "{name}"')
    else:
        if image is not None:
            raise RuntimeError(f'able to find image with alt text "{name}"')


@step('I should see the image with the alt text "{text}"')
def should_see_image(ctx, text):
    assert_image(ctx, text, is_visible=True)


@step('I should not see the image with the alt text "{text}"')
def should_not_see_image(ctx, text):
    assert_image(ctx, text, is_visible=False)


@step('I wait to see the image with the alt text "{text}"')
def wait_to_see_image(ctx, text):
    retry(assert_image)(ctx, text)

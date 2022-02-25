from behave import step


def find_image(ctx, name, index=0):
    """
    find an input on screen by fuzzy matching on the name provided and the
    target element:

        * <img>

    parameters:
      ctx - behave ctx object passed to a behave step
      name    - name that identifies the desired element on screen
      index   - the index of the element if there are a few with the same name.

    returns:
        the WebElement that matches the provided arguments.
    """
    imgs = ctx.browser.css_find_elements(f'img[alt="{name}"')

    if len(imgs) <= index:
        return None
    else:
        return imgs[index]


@step('I should see the image with the alt text "{text}"')
def should_see_image(ctx, text):
    image = find_image(ctx, text)

    if image is None:
        raise RuntimeError(f'unable to find image with alt text "{text}"')


@step('I should not see the image with the alt text "{text}"')
def should_not_see_image(ctx, text):
    image = find_image(ctx, text)

    if image is not None:
        raise RuntimeError(f'able to find image with alt text "{text}"')


@step('I wait to see the image with the alt text "{text}"', wait_for=True)
def wait_to_see_image(ctx, text):
    image = find_image(ctx, text)

    if image is None:
        raise RuntimeError(f'unable to find image with alt text "{text}"')

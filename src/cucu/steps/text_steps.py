from cucu import fuzzy, retry, step


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
    return fuzzy.find(ctx.browser,
                      name,
                      ['*'],
                      index=index,
                      direction=fuzzy.Direction.LEFT_TO_RIGHT)


def find_n_assert_text(ctx, name, index=0, is_visible=True):
    """
    find and assert text is visible

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired radio text on screen
      index(str):  the index of the radio text if there are duplicates

    returns:
        the WebElement that matches the provided arguments or None if none found
    """
    text = find_text(ctx, name)

    if is_visible:
        if text is None:
            raise Exception(f'unable to find the text "{name}"')
    else:
        if text is not None:
            raise Exception(f'able to find the text "{name}"')


@step('I should see the text "{name}"')
def should_see_the_text(ctx, name):
    find_n_assert_text(ctx, name)


@step('I wait to see the text "{name}"')
def wait_see_the_text(ctx, name):
    retry(find_n_assert_text)(ctx, name)


@step('I wait up to "{seconds}" seconds to see the text "{name}"')
def wait_up_to_seconds_to_see_the_text(ctx, seconds, name):
    retry(find_n_assert_text,
          wait_up_to_s=float(seconds))(ctx, name)


@step('I should not see the text "{name}"')
def should_not_see_the_text(ctx, name):
    find_n_assert_text(ctx, name, is_visible=False)

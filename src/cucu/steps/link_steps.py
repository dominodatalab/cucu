from cucu import fuzzy, retry, step


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


def find_n_assert_link(ctx, name, index=0, is_visible=True):
    """
    find the link with the name and index provided

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired link on screen
      index(str):  the index of the link if there are duplicates

    raises:
        an error if the desired link is not found
    """
    link = find_link(ctx, name, index=index)

    if is_visible:
        if link is None:
            raise Exception(f'unable to find a link with the text "{name}"')
    else:
        if link is not None:
            raise Exception(f'able to find a link with the text "{name}"')

    return link


def find_n_click_link(ctx, name, index=0):
    """
    find the link with the name and index provided and click it

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired link on screen
      index(str):  the index of the link if there are duplicates

    raises:
        an error if the desired link is not found
    """
    link = find_n_assert_link(ctx, name, index=index)
    link.click()


@step('I click the link "{name}"')
def clicks_the_link(ctx, name):
    find_n_click_link(ctx, name)


@step('I wait to click the link "{name}"')
def waits_to_click_the_link(ctx, name):
    retry(find_n_click_link)(ctx, name)


@step('I should see the link "{name}"')
def should_see_the_link(ctx, name):
    find_n_assert_link(ctx, name, is_visible=True)


@step('I wait to see the link "{name}"')
def waits_to_see_the_link(ctx, name):
    retry(find_n_assert_link)(ctx, name, is_visible=True)


@step('I should not see the link "{name}"')
def should_not_see_the_link(ctx, name):
    find_n_assert_link(ctx, name, is_visible=False)


@step('I wait to not see the link "{name}"')
def waits_to_not_see_the_link(ctx, name):
    retry(find_n_assert_link)(ctx, name, is_visible=False)

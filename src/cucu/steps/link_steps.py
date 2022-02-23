from behave import step

from cucu import fuzzy


def find_link(context, name, index=0):
    """
    find a link on screen by fuzzy matching on the name provided and the target
    element:

        * <a>
        * <* role="link">

    parameters:
      context - behave context object passed to a behave step
      name    - name that identifies the desired element on screen
      index   - the index of the element if there are a few with the same name.

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(context.browser,
                      name,
                      [
                          'a',
                          '*[role="link"]'
                      ],
                      index=index)


@step('I click the link "{name}"')
def clicks_the_link(context, name):
    link = find_link(context, name)
    link.click()


@step('I wait to click the link "{name}"', wait_for=True)
def waits_to_click_the_link(context, name):
    link = find_link(context, name)
    link.click()


@step('I should see the link "{name}"')
def should_see_the_link(context, name):
    link = find_link(context, name)

    if link is None:
        raise Exception(f'unable to find a link with the text "{name}"')


@step('I wait to see the link "{name}"', wait_for=True)
def waits_to_see_the_link(context, name):
    link = find_link(context, name)

    if link is None:
        raise Exception(f'unable to find a link with the text "{name}"')

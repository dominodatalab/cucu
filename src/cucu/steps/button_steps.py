from behave import step

from cucu import fuzzy


def find_button(context, name, index=0):
    """
    find a button on screen by fuzzy matching on the name provided and the
    target element:

        * <button>
        * <input type="button">
        * <input type="submit">
        * <a>
        * <* role="button">
        * <* role="link">
        * <* role="menuitem">
        * <* role="option">

    arguments:
      context - behave context object passed to a behave step
      name    - name that identifies the desired element on screen
      index   - the index of the element if there are a few with the same name.

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(context.browser.execute,
                      name,
                      [
                          'button',
                          'input[type="button"]',
                          'input[type="submit"]',
                          'a',
                          '*[role="button"]',
                          '*[role="link"]',
                          '*[role="menuitem"]',
                          '*[role="option"]',
                      ],
                      index=index)


@step('I click the button "{name}"')
def clicks_the_button(context, name):
    button = find_button(context, name)
    button.click()


@step('I wait to click the button "{name}"', wait_for=True)
def waits_to_clicks_the_button(context, name):
    button = find_button(context, name)
    button.click()


@step('I click the "{nth:nth}" button "{name}"')
def clicks_the_nth_button(context, nth, name):
    button = find_button(context, name, index=nth)
    button.click()


@step('I wait to click the "{nth:nth}" button "{name}"', wait_for=True)
def waits_to_clicks_the_nth_button(context, nth, name):
    button = find_button(context, name, index=nth)
    button.click()


@step('I should see the button "{name}"')
def we_should_see_the_button(context, name):
    button = find_button(context, name)

    if button is None:
        raise Exception(f'unable to find button "{name}"')


@step('I wait to see the button "{name}"', wait_for=True)
def waits_to_see_the_button(context, name):
    button = find_button(context, name)

    if button is None:
        raise Exception(f'unable to find button "{name}"')


@step('I should see the "{nth:nth}" button "{name}"')
def should_see_the_nth_button(context, nth, name):
    button = find_button(context, name, index=nth)

    if button is None:
        raise Exception(f'unable to find button "{name}"')


@step('I wait to see the "{nth:nth}" button "{name}"', wait_for=True)
def waits_to_see_the_nth_button(context, nth, name):
    button = find_button(context, name, index=nth)

    if button is None:
        raise Exception(f'unable to find button "{name}"')

from behave import step

from cucu import fuzzy


def find_checkbox(context, name, index=0):
    """
    find a checkbox on screen by fuzzy matching on the name provided and the
    target element:

        * <input type="checkbox">
        * <* role="checkbox">

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
                          'input[type="checkbox"]',
                          '*[role="checkbox"]',
                      ],
                      index=index,
                      direction=fuzzy.Direction.RIGHT_TO_LEFT)


@step('I check the checkbox "{name}"')
def checks_the_checkbox(context, name):
    checkbox = find_checkbox(context, name)

    if checkbox is None:
        raise Exception(f'Unable to find checkbox "{name}"')

    checked = checkbox.get_attribute('checked') == 'true'

    if checked:
        raise Exception(f'checkbox "{name}" already checked')

    checkbox.click()


@step('I wait to check the checkbox "{name}"', wait_for=True)
def waits_to_check_the_checkbox(context, name):
    checkbox = find_checkbox(context, name)

    if checkbox is None:
        raise Exception(f'Unable to find checkbox "{name}"')

    checked = bool(checkbox.get_attribute('checked'))

    if checked:
        raise Exception(f'checkbox "{name}" already checked')
    else:
        checkbox.click()


@step('I should see the checkbox "{name}" is checked')
def should_see_checkbox_is_checked(context, name):
    checkbox = find_checkbox(context, name)
    if checkbox is None:
        raise Exception(f'Unable to find checkbox "{name}"')
    checked = bool(checkbox.get_attribute('checked'))

    if not(checked):
        raise Exception(f'checkbox "{name}" is not checked')


@step('I wait to see the checkbox "{name}" is checked', wait_for=True)
def waits_to_see_checkbox_is_checked(context, name):
    checkbox = find_checkbox(context, name)
    if checkbox is None:
        raise Exception(f'Unable to find checkbox "{name}"')
    checked = bool(checkbox.get_attribute('checked'))

    if not(checked):
        raise Exception(f'checkbox "{name}" is not checked')


@step('I should see the checkbox "{name}" is not checked')
def should_see_checkbox_is_not_checked(context, name):
    checkbox = find_checkbox(context, name)
    if checkbox is None:
        raise Exception(f'Unable to find checkbox "{name}"')
    checked = bool(checkbox.get_attribute('checked'))

    if checked:
        raise Exception(f'checkbox "{name}" is checked')


@step('I wait to see the checkbox "{name}" is not checked')
def waits_to_see_checkbox_is_not_checked(context, name):
    checkbox = find_checkbox(context, name)
    if checkbox is None:
        raise Exception(f'Unable to find checkbox "{name}"')
    checked = bool(checkbox.get_attribute('checked'))

    if checked:
        raise Exception(f'checkbox "{name}" is checked')

from behave import step

from cucu import fuzzy


def find_radio_button(context, name, index=0):
    """
    find a radio button on screen by fuzzy matching on the name provided and
    the target element:

        * <input type="radio">
        * <* role="radio">

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
                          'input[type="radio"]',
                          '*[role="radio"]',
                      ],
                      index=index,
                      direction=fuzzy.Direction.RIGHT_TO_LEFT)


def select_radio_button(context, name, ignore_if_selected=False):
    radio = find_radio_button(context, name)

    if radio is None:
        raise Exception(f'unable to find radio button "{name}"')

    selected = radio.get_attribute('checked') == 'true'

    if selected:
        if ignore_if_selected:
            return

        raise Exception(f'radio button "{name}" already selected')

    radio.click()


@step('I select the radio button "{name}"')
def select_the_radio_button(context, name):
    select_radio_button(context, name, ignore_if_selected=False)


@step('I wait to select the radio button "{name}"', wait_for=True)
def wait_to_select_the_radio_button(context, name):
    select_radio_button(context, name, ignore_if_selected=False)


@step('I select the radio button "{name}" if it is not selected')
def select_the_radio_button_if_not_selected(context, name):
    select_radio_button(context, name, ignore_if_selected=True)


@step('I wait to select the radio button "{name}" if it is not selected',
      wait_for=True)
def wait_to_select_the_radio_button_if_not_selected(context, name):
    select_radio_button(context, name, ignore_if_selected=True)


def assert_radio_button_selected(context, name):
    radio = find_radio_button(context, name)

    if radio is None:
        raise Exception(f'unable to find radio button "{name}"')

    selected = bool(radio.get_attribute('checked'))

    if not(selected):
        raise Exception(f'radio button "{name}" is not selected')


@step('I should see the radio button "{name}" is selected')
def should_see_radio_button_is_checked(context, name):
    assert_radio_button_selected(context, name)


@step('I wait to see the radio button "{name}" is selected',
      wait_for=True)
def wait_to_see_radio_button_is_checked(context, name):
    assert_radio_button_selected(context, name)


def assert_radio_button_not_selected(context, name):
    radio = find_radio_button(context, name)

    if radio is None:
        raise Exception(f'unable to find radio button "{name}"')

    selected = bool(radio.get_attribute('checked'))

    if selected:
        raise Exception(f'radio button "{name}" is selected')


@step('I should see the radio button "{name}" is not selected')
def should_see_radio_button_is_not_checked(context, name):
    assert_radio_button_not_selected(context, name)


@step('I wait to see the radio button "{name}" is not selected')
def wait_to_see_radio_button_is_not_checked(context, name):
    assert_radio_button_not_selected(context, name)

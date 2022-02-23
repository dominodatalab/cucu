from behave import step

from cucu import fuzzy


def find_input(context, name, index=0):
    """
    find an input on screen by fuzzy matching on the name provided and the
    target element:

        * <input>
        * <textarea>

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
                          'input',
                          'textarea',
                      ],
                      index=index)


@step('I write "{value}" into the input "{name}"')
def writes_into_input(context, value, name):
    input_ = find_input(context, name)
    input_.send_keys(value)


@step('I wait to write "{value}" into the input "{name}"',
      wait_for=True)
def wait_to_write_into_input(context, value, name):
    input_ = find_input(context, name)
    input_.send_keys(value)


@step('I wait to see the input "{name}"', wait_for=True)
def wait_to_see_the_input(context, name):
    input_ = find_input(context, name)

    if input_ is None:
        raise Exception(f'unable to see the input {name}')


@step('I should see "{value}" in the input "{name}"')
def should_see_the_input_with_value(context, value, name):
    input_ = find_input(context, name)

    if input_ is None:
        raise Exception(f'unable to see the input "{name}"')

    actual = input_.get_attribute('value')
    if actual != value:
        raise Exception(f'the input "{name}" has value "{actual}"')


@step('I wait to see the value "{value}" in the input "{name}"',
      wait_for=True)
def wait_to_see_the_input_with_value(context, value, name):
    input_ = find_input(context, name)

    if input_ is None:
        raise Exception(f'unable to see the input "{name}"')

    if input_.get_attribute('value') != value:
        raise Exception(f'unable to see the input "{name}"')


@step('I should see no value in the input "{name}"')
def wait_to_see_the_input_with_no_value(context, name):
    input_ = find_input(context, name)

    if input_ is None:
        raise Exception(f'unable to see the input "{name}"')

    value = input_.get_attribute('value')
    if value != '':
        raise Exception(f'the input "{name}" has value "{value}"')


@step('I write "{value}" into the "{nth:nth}" input "{name}"')
def write_into_the_nth_input(context, value, nth, name):
    input_ = find_input(context, name, index=nth)
    input_.send_keys(value)


@step('I wait to write "{value}" into the "{nth:nth}" input "{name}"',
      wait_for=True)
def wait_to_write_into_the_nth_input(context, value, nth, name):
    input_ = find_input(context, name, index=nth)
    input_.send_keys(value)


@step('I wait to see the "{nth:nth}" input "{name}"', wait_for=True)
def wait_to_see_the_nth_input(context, nth, name):
    input_ = find_input(context, name, index=nth)

    if input_ is None:
        raise Exception(f'unable to see the input {name}')


@step('I should see "{value}" in the "{nth:nth}" input "{name}"')
def should_see_the_nth_input_with_value(context, value, nth, name):
    input_ = find_input(context, name, index=nth)

    if input_ is None:
        raise Exception(f'unable to see the "{nth}" input "{name}"')

    actual = input_.get_attribute('value')
    if actual != value:
        raise Exception(f'the "{nth}" input "{name}" has value "{actual}"')


@step('I wait to see the value "{value}" in the "{nth:nth}" input "{name}"',
      wait_for=True)
def wait_to_see_the_nth_input_with_value(context, value, nth, name):
    input_ = find_input(context, name, index=nth)

    if input_ is None:
        raise Exception(f'unable to see the "{nth}" input "{name}"')

    if input_.get_attribute('value') != value:
        raise Exception(f'unable to see the "{nth}" input "{name}"')


@step('I should see no value in the "{nth:nth}: input "{name}"')
def wait_to_see_the_nth_input_with_no_value(context, nth, name):
    input_ = find_input(context, name, index=nth)

    if input_ is None:
        raise Exception(f'unable to see the "{nth}" input "{name}"')

    value = input_.get_attribute('value')
    if value != '':
        raise Exception(f'the "{nth}" input "{name}" has value "{value}"')

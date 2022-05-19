import humanize

from cucu import helpers, fuzzy, retry, step

# XXX: this would have to be generalized to other browser abstraactions
from selenium.webdriver.common.keys import Keys
from . import base_steps


def find_input(ctx, name, index=0):
    """
    find an input on screen by fuzzy matching on the name and index provided.

        * <input>
        * <textarea>

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired input on screen
      index(str):  the index of the input if there are a few with the same name.

    returns:
        the WebElement that matches the provided arguments.

    raises:
        a RuntimeError if the input isn't found
    """
    input_ = fuzzy.find(
        ctx.browser,
        name,
        [
            "input",
            "textarea",
        ],
        index=index,
    )

    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    if input_ is None:
        raise RuntimeError(f'unable to find the {prefix}input "{name}"')

    return input_


def find_n_write(ctx, name, value, index=0):
    """
    find the input with the name provided and write the value provided into it.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired input on screen
      index(str):  the index of the input if there are a few with the same name.

    raises:
        an error if the desired input is not found
    """
    input_ = find_input(ctx, name, index=index)
    input_.send_keys(value)


def find_n_clear(ctx, name, index=0):
    """
    find the input with the name provided and clear whatever value it has.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired input on screen
      index(str):  the index of the input if there are a few with the same name.

    raises:
        an error if the desired input is not found
    """
    input_ = find_input(ctx, name, index=index)
    input_.clear()


def assert_input_value(ctx, name, value, index=0):
    """
    assert the input with the name provided has the value specified, unless the
    value is None which then means to verify there is not value set.

    Params:
        ctx(object):   behave context used to share information between steps
        name(string):  name of the input to find and assert is visible
        value(string): value to assert the input has, when set to None we verify
                       the input currently has no value.
        index(int):    index of the input to assert when there are multiple
                       inputs have the same name.
    """
    input_ = find_input(ctx, name, index=index)
    actual = input_.get_attribute("value")
    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    if value is None:
        if actual != "":
            raise RuntimeError(
                f'the {prefix}input "{name}" has value "{actual}"'
            )

    elif actual != value:
        raise RuntimeError(f'the {prefix}input "{name}" has value "{actual}"')


helpers.define_should_see_thing_with_name_steps("input", find_input)
helpers.define_thing_with_name_in_state_steps(
    "input", "disabled", find_input, base_steps.is_disabled
)
helpers.define_thing_with_name_in_state_steps(
    "input", "not disabled", find_input, base_steps.is_not_disabled
)


@step('I write "{value}" into the input "{name}"')
def writes_into_input(ctx, value, name):
    find_n_write(ctx, name, value)


@step('I wait to write "{value}" into the input "{name}"')
def wait_to_write_into_input(ctx, value, name):
    retry(find_n_write)(ctx, name, value)


@step(
    'I wait up to "{seconds}" seconds to write "{value}" into the input "{name}"'
)
def wait_up_to_write_into_input(ctx, seconds, value, name):
    retry(find_n_write, wait_up_to_s=float(seconds))(ctx, name, value)


@step(
    'I write into the input "{name}" the following'
)
def writes_multi_lines_into_input(ctx, name):
    value = ctx.text.replace('\n', Keys.RETURN)
    find_n_write(ctx, name, value)


@step(
    'I wait to write into the input "{name}" the following'
)
def wait_to_write_multi_lines_into_input(ctx, name):
    value = ctx.text.replace('\n', Keys.RETURN)
    retry(find_n_write)(ctx, name, value)
    

@step(
    'I wait up to "{seconds}" to write into the input "{name}" the following'
)
def wait_up_to_write_multi_lines_into_input(ctx, seconds, name):
    value = ctx.text.replace('\n', Keys.RETURN)
    retry(find_n_write, wait_up_to_s=float(seconds))(ctx, name, value)
    

@step('I send the "{key}" key to the input "{name}"')
def send_keys_to_input(ctx, key, name):
    find_n_write(ctx, name, Keys.__dict__[key.upper()])


@step('I clear the input "{name}"')
def clear_input(ctx, name):
    find_n_clear(ctx, name)


@step('I wait to clear the input "{name}"')
def wait_to_clear_input(ctx, name):
    retry(find_n_clear)(ctx, name)


@step('I wait up to "{seconds}" seconds to clear the input "{name}"')
def wait_up_to_clear_input(ctx, seconds, value, name):
    retry(find_n_clear, wait_up_to_s=float(seconds))(ctx, name)


@step('I should see "{value}" in the input "{name}"')
def should_see_the_input_with_value(ctx, value, name):
    assert_input_value(ctx, name, value)


@step('I wait to see the value "{value}" in the input "{name}"')
def wait_to_see_the_input_with_value(ctx, value, name):
    retry(assert_input_value)(ctx, name, value)


@step('I should see no value in the input "{name}"')
def should_to_see_the_input_with_no_value(ctx, name):
    assert_input_value(ctx, name, None)


@step('I write "{value}" into the "{nth:nth}" input "{name}"')
def write_into_the_nth_input(ctx, value, nth, name):
    find_n_write(ctx, name, value, index=nth)


@step('I wait to write "{value}" into the "{nth:nth}" input "{name}"')
def wait_to_write_into_the_nth_input(ctx, value, nth, name):
    retry(find_n_write)(ctx, name, value, index=nth)


@step('I wait to see the "{nth:nth}" input "{name}"')
def wait_to_see_the_nth_input(ctx, nth, name):
    retry(find_input)(ctx, name, index=nth)


@step('I should see "{value}" in the "{nth:nth}" input "{name}"')
def should_see_the_nth_input_with_value(ctx, value, nth, name):
    find_input(ctx, name, value, index=nth)


@step('I wait to see the value "{value}" in the "{nth:nth}" input "{name}"')
def wait_to_see_the_nth_input_with_value(ctx, value, nth, name):
    retry(assert_input_value)(ctx, name, value, index=nth)


@step('I should see no value in the "{nth:nth}: input "{name}"')
def should_see_the_nth_input_with_no_value(ctx, nth, name):
    assert_input_value(ctx, name, None, index=nth)

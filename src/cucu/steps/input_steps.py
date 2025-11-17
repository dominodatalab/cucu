import sys

import humanize

# XXX: this would have to be generalized to other browser abstractions
from selenium.webdriver.common.keys import Keys

from cucu import fuzzy, helpers, retry, step
from cucu.utils import take_saw_element_screenshot

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
    ctx.check_browser_initialized()

    element = fuzzy.find(
        ctx.browser,
        name,
        [
            # we can only write into things that do not have the type:
            # button, checkbox, radio, color, hidden, range, reset
            "input[type!=button][type!=checkbox][type!=radio][button!=color][button!=hidden][button!=range][button!=reset]",
            "textarea",
        ],
        index=index,
    )

    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    take_saw_element_screenshot(ctx, "input", name, index, element)

    if element is None:
        raise RuntimeError(f'unable to find the {prefix}input "{name}"')

    return element


def click_input(ctx, input_):
    """
    internal method used to simply click a input element
    """
    ctx.check_browser_initialized()

    if base_steps.is_disabled(input_):
        raise RuntimeError("unable to click the input, as it is disabled")

    ctx.browser.click(input_)


def clear_input(input_):
    """
    internal method used to clear inputs and make sure they clear correctly
    """
    # Keys.CONTROL works on the Selenium grid (when running in CI)
    #  - it stopped working on laptop after the upgrade in antd version (Feb 2023)
    # Keys.COMMAND works on laptop, but not on Selenium grid,
    # and actually causes an active session on the grid to hang.
    if "darwin" in sys.platform:
        input_.send_keys(Keys.COMMAND, "a")
    else:
        input_.send_keys(Keys.CONTROL, "a")
    input_.send_keys(Keys.BACKSPACE)


def find_n_write(ctx, name, value, index=0, clear_existing=True):
    """
    find the input with the name provided and write the value provided into it.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired input on screen
      index(str):  the index of the input if there are a few with the same name.
      clear_existing(bool): if clearing the existing content before writing

    raises:
        an error if the desired input is not found
    """
    ctx.check_browser_initialized()

    input_ = find_input(ctx, name, index=index)

    if base_steps.is_disabled(input_):
        raise RuntimeError("unable to write into the input, as it is disabled")

    if clear_existing:
        clear_input(input_)

    if len(value) > 512:
        #
        # to avoid various bugs with writing large chunks of text into
        # inputs/textareas using send_keys we can just put the text into the
        # @value attribute and simulate a keystroke so other UI related events
        # fire, list of some bugs:
        #
        #  * https://github.com/seleniumhq/selenium-google-code-issue-archive/issues/4469
        #  * various stackoverflow articles on this matter
        #
        ctx.browser.execute(
            "arguments[0].value = arguments[1];", input_, value
        )
        input_.send_keys(" ")
        input_.send_keys(Keys.BACKSPACE)

    else:
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
    ctx.check_browser_initialized()

    input_ = find_input(ctx, name, index=index)

    if base_steps.is_disabled(input_):
        raise RuntimeError("unable to clear the input, as it is disabled")

    clear_input(input_)


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
helpers.define_run_steps_if_I_can_see_element_with_name_steps(
    "input", find_input
)
helpers.define_action_on_thing_with_name_steps(
    "input", "click", find_input, click_input, with_nth=True
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


@step('I write the following into the input "{name}"')
def writes_multi_lines_into_input(ctx, name):
    find_n_write(ctx, name, ctx.text)


@step('I wait to write the following into the input "{name}"')
def wait_to_write_multi_lines_into_input(ctx, name):
    retry(find_n_write)(ctx, name, ctx.text)


@step(
    'I wait up to "{seconds}" to write the following into the input "{name}"'
)
def wait_up_to_write_multi_lines_into_input(ctx, seconds, name):
    retry(find_n_write, wait_up_to_s=float(seconds))(ctx, name, ctx.text)


@step('I send the "{key}" key to the input "{name}"')
def send_keys_to_input(ctx, key, name):
    find_n_write(ctx, name, Keys.__dict__[key.upper()], clear_existing=False)


@step('I clear the input "{name}"')
def clear_the_input(ctx, name):
    find_n_clear(ctx, name)


@step('I wait to clear the input "{name}"')
def wait_to_clear_input(ctx, name):
    retry(find_n_clear)(ctx, name)


@step('I wait up to "{seconds}" seconds to clear the input "{name}"')
def wait_up_to_clear_input(ctx, seconds, name):
    retry(find_n_clear, wait_up_to_s=float(seconds))(ctx, name)


@step('I should see the input "{name}" is empty')
def should_see_the_input_is_empty(ctx, name):
    assert_input_value(ctx, name, None)


@step('I should see "{value}" in the input "{name}"')
def should_see_the_input_with_value(ctx, value, name):
    assert_input_value(ctx, name, value)


@step('I wait to see the value "{value}" in the input "{name}"')
def wait_to_see_the_input_with_value(ctx, value, name):
    retry(assert_input_value)(ctx, name, value)


@step('I should see the following in the input "{name}"')
def should_see_the_following_input_with_value(ctx, name):
    assert_input_value(ctx, name, ctx.text)


@step('I wait to see the following in the input "{name}"')
def wait_to_see_the_following_input_with_value(ctx, name):
    retry(assert_input_value)(ctx, name, ctx.text)


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
    assert_input_value(ctx, name, value, index=nth)


@step('I wait to see the value "{value}" in the "{nth:nth}" input "{name}"')
def wait_to_see_the_nth_input_with_value(ctx, value, nth, name):
    retry(assert_input_value)(ctx, name, value, index=nth)


@step('I should see no value in the "{nth:nth}: input "{name}"')
def should_see_the_nth_input_with_no_value(ctx, nth, name):
    assert_input_value(ctx, name, None, index=nth)

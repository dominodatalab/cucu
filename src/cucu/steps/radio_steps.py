from cucu import fuzzy, helpers, retry, step
from cucu.config import CONFIG
from cucu.utils import take_saw_element_screenshot

from . import base_steps


def find_radio_button(ctx, name, index=0):
    """
    find a radio button on screen by fuzzy matching on the name provided and
    the target element:

        * <input type="radio">
        * <* role="radio">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired radio button on screen
      index(str):  the index of the radio button if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()
    element = fuzzy.find(
        ctx.browser,
        name,
        [
            'input[type="radio"]',
            '*[role="radio"]',
        ],
        index=index,
        direction=fuzzy.Direction.RIGHT_TO_LEFT,
    )

    take_saw_element_screenshot(ctx, "radio button", name, index, element)

    return element


def find_n_assert_radio_button(ctx, name, index=0, is_visible=True):
    """
    find and assert a radio button is visible

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired radio button on screen
      index(str):  the index of the radio button if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    radio = find_radio_button(ctx, name, index=index)

    if is_visible:
        if radio is None:
            raise Exception(f'unable to find radio button "{name}"')
    else:
        if radio is not None:
            raise Exception(f'able to find radio button "{name}"')

    return radio


def find_n_select_radio_button(ctx, name, index=0, ignore_if_selected=False):
    """
    find and select a radio button

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired radio button on screen
      index(str):  the index of the radio button if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()
    radio = find_n_assert_radio_button(ctx, name, index=index)

    if base_steps.is_disabled(radio):
        raise RuntimeError(
            "unable to select the radio button, as it is disabled"
        )

    selected = radio.get_attribute("checked") == "true"

    if selected:
        if ignore_if_selected:
            return

        raise Exception(f'radio button "{name}" already selected')

    ctx.browser.click(radio)


def is_selected(radio):
    """
    internal method to check if radiobox is selected
    """
    return bool(radio.get_attribute("checked"))


def is_not_selected(radio):
    """
    internal method to check if a radiobox is not selected
    """
    return not is_selected(radio)


def select_radio_button(ctx, radiobox):
    """
    internal method to select a radio button that isn't already selected
    """
    ctx.check_browser_initialized()

    if base_steps.is_disabled(radiobox):
        raise RuntimeError(
            "unable to select the radio button, as it is disabled"
        )

    selected = bool(radiobox.get_attribute("checked"))

    if selected:
        raise Exception("radiobox already selected")

    ctx.browser.click(radiobox)


helpers.define_should_see_thing_with_name_steps(
    "radio button", find_radio_button
)
helpers.define_action_on_thing_with_name_steps(
    "radio button", "select", find_radio_button, select_radio_button
)
helpers.define_thing_with_name_in_state_steps(
    "radio button", "selected", find_radio_button, is_selected, with_nth=True
)
helpers.define_thing_with_name_in_state_steps(
    "radio button", "not selected", find_radio_button, is_not_selected
)
helpers.define_thing_with_name_in_state_steps(
    "radio button", "disabled", find_radio_button, base_steps.is_disabled
)
helpers.define_thing_with_name_in_state_steps(
    "radio button",
    "not disabled",
    find_radio_button,
    base_steps.is_not_disabled,
)
helpers.define_run_steps_if_I_can_see_element_with_name_steps(
    "radio", find_radio_button
)


@step('I immediately select the radio button "{name}" if it is not selected')
def immediately_select_the_radio_button_if_not_selected(ctx, name):
    find_n_select_radio_button(ctx, name, ignore_if_selected=True)


@step('I select the radio button "{name}" if it is not selected')
def select_the_radio_button_if_not_selected(ctx, name):
    retry(
        find_n_select_radio_button,
        retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
        wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
    )(ctx, name, ignore_if_selected=True)


@step('I wait to select the radio button "{name}" if it is not selected')
def wait_to_select_the_radio_button_if_not_selected(ctx, name):
    retry(find_n_select_radio_button)(ctx, name, ignore_if_selected=True)


@step(
    'I immediately select the "{nth:nth}" radio button "{name}" if it is not selected'
)
def immediately_select_nth_radio_button_if_not_selected(ctx, nth, name):
    find_n_select_radio_button(ctx, name, nth, ignore_if_selected=True)


@step('I select the "{nth:nth}" radio button "{name}" if it is not selected')
def select_nth_radio_button(ctx, nth, name):
    retry(
        find_n_select_radio_button,
        retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
        wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
    )(ctx, name, nth, ignore_if_selected=True)

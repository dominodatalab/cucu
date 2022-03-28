from cucu import helpers, fuzzy, retry, step


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
    return fuzzy.find(
        ctx.browser,
        name,
        [
            'input[type="radio"]',
            '*[role="radio"]',
        ],
        index=index,
        direction=fuzzy.Direction.RIGHT_TO_LEFT,
    )


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
    radio = find_n_assert_radio_button(ctx, name, index=index)

    selected = radio.get_attribute("checked") == "true"

    if selected:
        if ignore_if_selected:
            return

        raise Exception(f'radio button "{name}" already selected')

    radio.click()


def is_selected(radio):
    return bool(radio.get_attribute("checked"))


def is_not_selected(checkbox):
    return not (is_selected(checkbox))


def select_radio_button(radiobox):
    """ """
    selected = bool(radiobox.get_attribute("checked"))

    if selected:
        raise Exception("radiobox already selected")

    radiobox.click()


helpers.define_should_see_thing_with_name_steps(
    "radio button", find_radio_button
)
helpers.define_action_on_thing_with_name_steps(
    "radio button", "select", find_radio_button, select_radio_button
)
helpers.define_thing_with_name_in_state_steps(
    "radio button", "selected", find_radio_button, is_selected
)
helpers.define_thing_with_name_in_state_steps(
    "radio button", "not selected", find_radio_button, is_not_selected
)


@step('I select the radio button "{name}" if it is not selected')
def select_the_radio_button_if_not_selected(ctx, name):
    find_n_select_radio_button(ctx, name, ignore_if_selected=True)


@step('I wait to select the radio button "{name}" if it is not selected')
def wait_to_select_the_radio_button_if_not_selected(ctx, name):
    retry(find_n_select_radio_button)(ctx, name, ignore_if_selected=True)

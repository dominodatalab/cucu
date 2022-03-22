from cucu import fuzzy, retry, step


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


def assert_radio_button_selected(ctx, name, is_selected=True):
    """
    assert radio button selected

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired radio button on screen
      index(str):  the index of the radio button if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    radio = find_n_assert_radio_button(ctx, name)

    selected = bool(radio.get_attribute("checked"))

    if is_selected:
        if not (selected):
            raise Exception(f'radio button "{name}" is not selected')
    else:
        if not (is_selected) and selected:
            raise Exception(f'radio button "{name}" is selected')


@step('I select the radio button "{name}"')
def select_the_radio_button(ctx, name):
    find_n_select_radio_button(ctx, name, ignore_if_selected=False)


@step('I wait to select the radio button "{name}"')
def wait_to_select_the_radio_button(ctx, name):
    find_n_select_radio_button(ctx, name, ignore_if_selected=False)


@step('I select the radio button "{name}" if it is not selected')
def select_the_radio_button_if_not_selected(ctx, name):
    find_n_select_radio_button(ctx, name, ignore_if_selected=True)


@step('I wait to select the radio button "{name}" if it is not selected')
def wait_to_select_the_radio_button_if_not_selected(ctx, name):
    retry(find_n_select_radio_button)(ctx, name, ignore_if_selected=True)


@step('I should see the radio button "{name}" is selected')
def should_see_radio_button_is_checked(ctx, name):
    assert_radio_button_selected(ctx, name, is_selected=True)


@step('I wait to see the radio button "{name}" is selected')
def wait_to_see_radio_button_is_checked(ctx, name):
    retry(assert_radio_button_selected)(ctx, name, is_selected=True)


@step('I should see the radio button "{name}" is not selected')
def should_see_radio_button_is_not_checked(ctx, name):
    assert_radio_button_selected(ctx, name, is_selected=False)


@step('I wait to see the radio button "{name}" is not selected')
def wait_to_see_radio_button_is_not_checked(ctx, name):
    retry(assert_radio_button_selected)(ctx, name, is_selected=False)

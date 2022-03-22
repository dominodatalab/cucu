import humanize

from cucu import fuzzy, retry, step


def find_checkbox(ctx, name, index=0):
    """
    find a checkbox on screen using name and index provided

        * <input type="checkbox">
        * <* role="checkbox">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired checkbox on screen
      index(str):  the index of the checkbox if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(
        ctx.browser,
        name,
        [
            'input[type="checkbox"]',
            '*[role="checkbox"]',
        ],
        index=index,
        direction=fuzzy.Direction.RIGHT_TO_LEFT,
    )


def find_n_assert_checkbox(ctx, name, index=0):
    """
    find the checkbox with the name and index provided and click it

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired link on screen
      index(str):  the index of the checkbox if there are duplicates

    raises:
        an error if the desired checkbox is not found
    """
    checkbox = find_checkbox(ctx, name, index=index)
    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    if checkbox is None:
        raise RuntimeError(f"unable to find the {prefix}checkbox {name}")

    return checkbox


def find_n_check_checkbox(ctx, name, index=0):
    """
    find the checkbox with the name and index provided and checks it

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired checkbox on screen
      index(str):  the index of the checkbox if there are a few with the same name

    raises:
        an error if the desired checkbox is not found
    """

    checkbox = find_checkbox(ctx, name)
    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "
    checked = checkbox.get_attribute("checked") == "true"

    if checked:
        raise Exception(f'{prefix}checkbox "{name}" already checked')

    checkbox.click()


def assert_checkbox_checked_state(ctx, name, state, index=0):
    """
    assert the checkbox with name and index provided is checked or not.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired checkbox on screen
      state(bool): state the checkbox should be in
      index(str):  the index of the checkbox if there are duplicates

    raises:
        an error if the desired checkbox is not found
    """
    checkbox = find_checkbox(ctx, name)
    checked = bool(checkbox.get_attribute("checked"))

    if state:
        op = "is"
    else:
        op = "is not"

    if state != checked:
        raise Exception(f'checkbox "{name}" {op} checked')


@step('I check the checkbox "{name}"')
def checks_the_checkbox(ctx, name):
    find_n_check_checkbox(ctx, name)


@step('I wait to check the checkbox "{name}"')
def waits_to_check_the_checkbox(ctx, name):
    retry(find_n_check_checkbox)(ctx, name)


@step('I should see the checkbox "{name}" is checked')
def should_see_checkbox_is_checked(ctx, name):
    assert_checkbox_checked_state(ctx, name, True)


@step('I wait to see the checkbox "{name}" is checked')
def waits_to_see_checkbox_is_checked(ctx, name):
    retry(assert_checkbox_checked_state)(ctx, name, True)


@step('I should see the checkbox "{name}" is not checked')
def should_see_checkbox_is_not_checked(ctx, name):
    assert_checkbox_checked_state(ctx, name, False)


@step('I wait to see the checkbox "{name}" is not checked')
def waits_to_see_checkbox_is_not_checked(ctx, name):
    retry(assert_checkbox_checked_state)(ctx, name, False)

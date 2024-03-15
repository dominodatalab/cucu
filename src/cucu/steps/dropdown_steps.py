import logging

import humanize
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from tenacity import (
    before_sleep_log,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_fixed,
)
from tenacity import retry as retrying

from cucu import fuzzy, helpers, logger, retry, step
from cucu.steps.input_steps import find_input
from cucu.utils import take_saw_element_screenshot

from . import base_steps


def find_dropdown(ctx, name, index=0):
    """
    find a dropdown on screen by fuzzy matching on the name provided and the
    target element:

        * <select>
        * <* role="combobox">
        * <* role="listbox">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired dropdown on screen
      index(str):  the index of the dropdown if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()

    dropdown = fuzzy.find(
        ctx.browser,
        name,
        [
            "select",
            '*[role="combobox"]',
            '*[role="listbox"]',
        ],
        index=index,
        direction=fuzzy.Direction.LEFT_TO_RIGHT,
    )
    if not dropdown:
        # In case the name is on the top of the dropdown element,
        # the name is after the ting in DOM. Try the other direction.
        dropdown = fuzzy.find(
            ctx.browser,
            name,
            [
                "select",
                '*[role="combobox"]',
                '*[role="listbox"]',
            ],
            index=index,
            direction=fuzzy.Direction.RIGHT_TO_LEFT,
        )

    take_saw_element_screenshot(ctx, "dropdown", name, index, dropdown)

    if dropdown:
        outer_html = dropdown.get_attribute("outerHTML")
        logger.debug(f'looked for dropdown "{name}", and found "{outer_html}"')
    else:
        logger.debug(f'looked for dropdown "{name}" but found none')

    return dropdown


@retrying(
    retry=retry_if_result(lambda result: result is None),
    stop=stop_after_attempt(10),
    wait=wait_fixed(0.1),
    before_sleep=before_sleep_log(logger, logging.DEBUG),
    reraise=True,
    retry_error_callback=lambda retry_state: retry_state.outcome.result(),
)
def find_dropdown_option(ctx, name, index=0):
    """
    find a dropdown option with the provided name. It only considers
    the web element with the name inside the element.

        * <option>
        * <* role="option">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired dropdown on screen
      index(str):  the index of the dropdown if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()

    option = fuzzy.find(
        ctx.browser,
        name,
        [
            "option",
            '*[role="option"]',
            '*[role="treeitem"]',
            "*[aria-selected]",
        ],
        index=index,
        direction=fuzzy.Direction.LEFT_TO_RIGHT,
        name_within_thing=True,
    )
    if option:
        outer_html = option.get_attribute("outerHTML")
        logger.debug(
            f'looked for dropdown option "{name}", and found "{outer_html}"'
        )
    else:
        logger.debug(f'looked for dropdown option "{name}" but found none')

    return option


def click_dropdown(ctx, dropdown):
    """
    Internal method used to simply click a dropdown element

    Args:
        ctx(object): behave context object used to share data between steps
        dropdown(WebElement): the dropdown element
    """
    ctx.check_browser_initialized()

    if base_steps.is_disabled(dropdown):
        raise RuntimeError("unable to click the button, as it is disabled")

    logger.debug("clicking dropdown")
    try:
        ctx.browser.click(dropdown)
    except ElementClickInterceptedException:
        clickable = dropdown
        while True:
            # In some cases, the dropdown is blocked by the selected item.
            # It finds the ancestors of the dropdown that is clickable and click.
            clickable = clickable.find_element(By.XPATH, "..")
            try:
                ctx.browser.click(clickable)
            except ElementClickInterceptedException:
                continue
            break


@retrying(
    retry=retry_if_exception_type(ElementNotInteractableException),
    stop=stop_after_attempt(10),
    wait=wait_fixed(0.1),
    before_sleep=before_sleep_log(logger, logging.DEBUG),
    reraise=True,
)
def click_dynamic_dropdown_option(ctx, option_element):
    ctx.browser.execute("arguments[0].scrollIntoView();", option_element)
    ctx.browser.click(option_element)


def find_n_select_dropdown_option(ctx, dropdown, option, index=0):
    """
    find and select dropdown option

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired dropdown on screen
      option(str): name of the option to select
      index(str):  the index of the dropdown if there are duplicates
    """
    ctx.check_browser_initialized()

    dropdown_element = find_dropdown(ctx, dropdown, index)

    if dropdown_element is None:
        prefix = "" if index == 0 else f"{humanize.ordinal(index)} "
        raise RuntimeError(f"unable to find the {prefix}dropdown {dropdown}")

    if base_steps.is_disabled(dropdown_element):
        raise RuntimeError(
            "unable to select from the dropdown, as it is disabled"
        )

    if dropdown_element.tag_name == "select":
        select_element = Select(dropdown_element)
        select_element.select_by_visible_text(option)

    else:
        if dropdown_element.get_attribute("aria-expanded") != "true":
            # open the dropdown
            click_dropdown(ctx, dropdown_element)

        option_element = find_dropdown_option(ctx, option)

        if option_element is None:
            raise RuntimeError(
                f'unable to find option "{option}" in dropdown "{dropdown}"'
            )

        logger.debug("clicking dropdown option")
        ctx.browser.execute("arguments[0].scrollIntoView();", option_element)
        ctx.browser.click(option_element)


def find_n_select_dynamic_dropdown_option(ctx, dropdown, option, index=0):
    """
    find and select dynamic dropdown option

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired dropdown on screen
      option(str): name of the option to select
      index(str):  the index of the dropdown if there are duplicates
    """
    ctx.check_browser_initialized()

    dropdown_element = find_dropdown(ctx, dropdown, index)

    if dropdown_element is None:
        prefix = "" if index == 0 else f"{humanize.ordinal(index)} "
        raise RuntimeError(f"unable to find the {prefix}dropdown {dropdown}")

    if base_steps.is_disabled(dropdown_element):
        raise RuntimeError(
            "unable to select from the dropdown, as it is disabled"
        )

    if dropdown_element.get_attribute("aria-expanded") != "true":
        # open the dropdown
        click_dropdown(ctx, dropdown_element)

    option_element = find_dropdown_option(ctx, option)

    # Use the search feature to make the option visible so cucu can pick it up
    if option_element is None:
        dropdown_input = find_input(ctx, dropdown, index)
        logger.debug(
            f'option "{option}" is not found, trying to send keys "{option}".'
        )
        dropdown_value = dropdown_input.get_attribute("value")
        if dropdown_value:
            logger.debug(f"clear dropdown value: {dropdown_value}")
            dropdown_input.send_keys(
                Keys.ARROW_RIGHT * len(dropdown_value)
            )  # make sure the cursor is at the end
            dropdown_input.send_keys(Keys.BACKSPACE * len(dropdown_value))
        # After each key stroke there is a request and an update of the option list. To prevent stale element,
        # we send keys one by one here and try to find the option after each key.
        for key in option:
            try:
                dropdown_input = find_input(ctx, dropdown, index)
                logger.debug(f'sending key "{key}"')
                dropdown_input.send_keys(key)
                ctx.browser.wait_for_page_to_load()
                option_element = find_dropdown_option(ctx, option)
                if option_element:
                    break
            except Exception:
                option_element = None

    if option_element is None:
        raise RuntimeError(
            f'unable to find option "{option}" in dropdown "{dropdown}"'
        )

    logger.debug("clicking dropdown option")
    click_dynamic_dropdown_option(ctx, option_element)


def assert_dropdown_option_selected(
    ctx, dropdown, option, index=0, is_selected=True
):
    """
    assert dropdown option is selected

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired dropdown on screen
      option(str): name of the option to select
      index(str):  the index of the dropdown if there are duplicates
    """
    ctx.check_browser_initialized()

    dropdown_element = find_dropdown(ctx, dropdown, index)
    if dropdown_element is None:
        raise RuntimeError(f'unable to find dropdown "{dropdown}"')

    selected_option = None
    if dropdown_element.tag_name == "select":
        select_element = Select(dropdown_element)
        selected_option = select_element.first_selected_option

        if selected_option is None:
            raise RuntimeError(
                f"unable to find selected option in dropdown {dropdown}"
            )

        selected_name = selected_option.get_attribute("textContent")

        # XXX: we're doing contains because a lot of our existing dropdowns
        #      do not use aria-label/aria-describedby to make them accessible
        #      and easier to find for automation by their name
        if is_selected:
            if selected_name.find(option) == -1:
                raise RuntimeError(f"{option} is not selected")
        else:
            if selected_name.find(option) != -1:
                raise RuntimeError(f"{option} is selected")

    else:
        if dropdown_element.get_attribute("aria-expanded") != "true":
            # open the dropdown to see its options
            click_dropdown(ctx, dropdown_element)

        selected_option = find_dropdown_option(ctx, option)

        if selected_option is None:
            raise RuntimeError(
                f'unable to find option "{option}" in dropdown "{dropdown}"'
            )

        if is_selected:
            if selected_option.get_attribute("aria-selected") != "true":
                raise RuntimeError(f"{option} is not selected")
        else:
            if selected_option.get_attribute("aria-selected") == "true":
                raise RuntimeError(f"{option} is selected")

        # close the dropdown
        click_dropdown(ctx, dropdown_element)


helpers.define_should_see_thing_with_name_steps("dropdown", find_dropdown)
helpers.define_thing_with_name_in_state_steps(
    "dropdown", "disabled", find_dropdown, base_steps.is_disabled
)
helpers.define_thing_with_name_in_state_steps(
    "dropdown", "not disabled", find_dropdown, base_steps.is_not_disabled
)
helpers.define_run_steps_if_I_can_see_element_with_name_steps(
    "dropdown", find_dropdown
)
helpers.define_action_on_thing_with_name_steps(
    "dropdown", "click", find_dropdown, click_dropdown, with_nth=True
)
helpers.define_thing_with_name_in_state_steps(
    "dropdown option", "disabled", find_dropdown_option, base_steps.is_disabled
)


@step('I select the option "{option}" from the dropdown "{dropdown}"')
def select_option_from_dropdown(ctx, option, dropdown):
    find_n_select_dropdown_option(ctx, dropdown, option)


@step(
    'I select the option "{option}" from the "{index:nth}" dropdown "{dropdown}"'
)
def select_option_from_nth_dropdown(ctx, option, dropdown, index):
    find_n_select_dropdown_option(ctx, dropdown, option, index)


@step(
    'I wait to select the option "{option}" from the "{index:nth}" dropdown "{dropdown}"'
)
def wait_to_select_option_from_nth_dropdown(ctx, option, dropdown, index):
    retry(find_n_select_dropdown_option)(ctx, dropdown, option, index)


@step('I wait to select the option "{option}" from the dropdown "{dropdown}"')
def wait_to_select_option_from_dropdown(ctx, option, dropdown):
    retry(find_n_select_dropdown_option)(ctx, dropdown, option)


@step('I select the option "{option}" from the dynamic dropdown "{dropdown}"')
def select_option_from_dynamic_dropdown(ctx, option, dropdown):
    find_n_select_dynamic_dropdown_option(ctx, dropdown, option)


@step(
    'I select the option "{option}" from the "{index:nth}" dynamic dropdown "{dropdown}"'
)
def select_option_from_nth_dynamic_dropdown(ctx, option, dropdown, index):
    find_n_select_dynamic_dropdown_option(ctx, dropdown, option, index)


@step(
    'I wait to select the option "{option}" from the "{index:nth}" dynamic dropdown "{dropdown}"'
)
def wait_to_select_option_from_nth_dynamic_dropdown(
    ctx, option, dropdown, index
):
    retry(find_n_select_dynamic_dropdown_option)(ctx, dropdown, option, index)


@step(
    'I wait to select the option "{option}" from the dynamic dropdown "{dropdown}"'
)
def wait_to_select_option_from_dynamic_dropdown(ctx, option, dropdown):
    retry(find_n_select_dynamic_dropdown_option)(ctx, dropdown, option)


@step(
    'I should see the option "{option}" is selected on the dropdown "{dropdown}"'
)
def should_see_option_is_selected_from_dropdown(ctx, option, dropdown):
    assert_dropdown_option_selected(ctx, dropdown, option, is_selected=True)


@step(
    'I should see the option "{option}" is selected on the "{index:nth}" dropdown "{dropdown}"'
)
def should_see_option_is_selected_from_nth_dropdown(
    ctx, option, dropdown, index
):
    assert_dropdown_option_selected(
        ctx, dropdown, option, index, is_selected=True
    )


@step(
    'I wait to see the option "{option}" is selected on the dropdown "{dropdown}"'
)
def wait_to_see_option_is_selected_from_dropdown(ctx, option, dropdown):
    retry(assert_dropdown_option_selected)(
        ctx, dropdown, option, is_selected=True
    )


@step(
    'I should see the option "{option}" is not selected on the "{index:nth}" dropdown "{dropdown}"'
)
def should_see_option_is_not_selected_from_nth_dropdown(
    ctx, option, dropdown, index
):
    assert_dropdown_option_selected(
        ctx, dropdown, option, index, is_selected=False
    )


@step(
    'I should see the option "{option}" is not selected on the dropdown "{dropdown}"'
)
def should_see_option_is_not_selected_from_dropdown(ctx, option, dropdown):
    assert_dropdown_option_selected(ctx, dropdown, option, is_selected=False)


@step(
    'I wait to see the option "{option}" is not selected on the dropdown "{dropdown}"'
)
def wait_to_see_option_is_not_selected_from_dropdown(
    ctx, option, dropdown, is_selected=False
):
    retry(assert_dropdown_option_selected)(ctx, dropdown, option)

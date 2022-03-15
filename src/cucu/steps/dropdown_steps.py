import humanize 

from cucu import fuzzy, retry, step
from selenium.webdriver.support.ui import Select


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
    dropdown = fuzzy.find(ctx.browser,
                          name,
                          [
                              'select',
                              '*[role="combobox"]',
                              '*[role="listbox"]',
                          ],
                          index=index,
                          direction=fuzzy.Direction.LEFT_TO_RIGHT)

    prefix = '' if index == 0 else f'{humanize.ordinal(index)} '

    if dropdown is None:
        raise RuntimeError(f'unable to find the {prefix}dropdown {name}')

    return dropdown


def find_dropdown_option(ctx, name, index=0):
    """
    find a dropdown option with the provided name

        * <option>
        * <* role="option">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired dropdown on screen
      index(str):  the index of the dropdown if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    option = fuzzy.find(ctx.browser,
                        name,
                        [
                            'option',
                            '*[role="option"]',
                        ],
                        index=index,
                        direction=fuzzy.Direction.LEFT_TO_RIGHT)

    prefix = '' if index == 0 else f'{humanize.ordinal(index)} '

    if option is None:
        raise RuntimeError(f'unable to find the {prefix}option {name}')

    return option


def find_n_select_dropdown_option(ctx, dropdown, option):
    """
    find and select dropdown option

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired dropdown on screen
      option(str): name of the option to select
    """

    dropdown_element = find_dropdown(ctx, dropdown)

    if dropdown_element.tag_name == 'select':
        select_element = Select(dropdown_element)
        select_element.select_by_visible_text(option)

    else:
        if dropdown_element.get_attribute('aria-expanded') != 'true':
            # open the dropdown
            dropdown_element.click()

        option_element = find_dropdown_option(ctx, option)

        if option_element is None:
            raise RuntimeError(f'unable to find option "{option}" in dropdown "{dropdown}"')

        option_element.click()


def assert_dropdown_option_selected(ctx, dropdown, option, is_selected=True):
    """
    assert dropdown option is selected

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired dropdown on screen
      option(str): name of the option to select
    """
    dropdown_element = find_dropdown(ctx, dropdown)
    selected_option = None

    if dropdown_element.tag_name == 'select':
        select_element = Select(dropdown_element)
        selected_option = select_element.first_selected_option
    else:
        if dropdown_element.get_attribute('aria-expanded') != 'true':
            # open the dropdown to see its options
            dropdown_element.click()

        selected_option = find_dropdown_option(ctx, option)
        # close the dropdown
        selected_option.click()

    if selected_option is None:
        raise RuntimeError(f'unable to find selected option in dropdown {dropdown}')

    selected_name = selected_option.get_attribute('textContent')

    # XXX: we're doing contains because a lot of our existing dropdown/comboboxes
    #      are messy and do not use things like aria-label/aria-describedby to
    #      make them accessible and easier to find for automation by their name

    if is_selected:
        if selected_name.find(option) == -1:
            raise RuntimeError(f'{option} is not selected')
    else:
        if selected_name.find(option) != -1:
            raise RuntimeError(f'{option} is selected')


@step('I should see the dropdown "{dropdown}"')
def should_see_the_dropdown(ctx, dropdown):
    find_dropdown(ctx, dropdown)


@step('I wait to see the dropdown "{dropdown}"')
def wait_to_see_the_dropdown(ctx, dropdown):
    retry(find_dropdown)(ctx, dropdown)


@step('I select the option "{option}" from the dropdown "{dropdown}"')
def select_option_from_dropdown(ctx, option, dropdown):
    find_n_select_dropdown_option(ctx, dropdown, option)


@step('I wait to select the option "{option}" from the dropdown "{dropdown}"')
def wait_to_select_option_from_dropdown(ctx, option, dropdown):
    retry(find_n_select_dropdown_option)(ctx, dropdown, option)


@step('I should see the option "{option}" is selected on the dropdown "{dropdown}"')
def should_see_option_is_selected(ctx, option, dropdown):
    assert_dropdown_option_selected(ctx, dropdown, option, is_selected=True)


@step('I wait to see the option "{option}" is selected on the dropdown "{dropdown}"')
def wait_to_see_option_is_selected(ctx, option, dropdown):
    retry(assert_dropdown_option_selected)(ctx, dropdown, option, is_selected=True)


@step('I should see the option "{option}" is not selected on the dropdown "{dropdown}"')
def should_see_option_is_not_selected(ctx, option, dropdown):
    assert_dropdown_option_selected(ctx, dropdown, option, is_selected=False)


@step('I wait to see the option "{option}" is not selected on the dropdown "{dropdown}"')
def wait_to_see_option_is_not_selected(ctx, option, dropdown, is_selected=False):
    retry(assert_dropdown_option_selected)(ctx, dropdown, option)

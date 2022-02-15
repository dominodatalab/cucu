from behave import step
from cucu import fuzzy
from selenium.webdriver.support.ui import Select


def find_dropdown(ctx, name, index=0):
    """
    find a dropdown on screen by fuzzy matching on the name provided and the
    target element:

        * <select>
        * <* role="combobox">
        * <* role="listbox">

    parameters:
      ctx   - behave context object passed to a behave step
      name  - name that identifies the desired element on screen
      index - the index of the element if there are a few with the same name.

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(ctx.browser.execute,
                      name,
                      [
                          'select',
                          '*[role="combobox"]',
                          '*[role="listbox"]',
                      ],
                      index=index,
                      direction=fuzzy.Direction.RIGHT_TO_LEFT)


def find_dropdown_option(ctx, name, index=0):
    """
    find a dropdown option with the provided name

        * <option>
        * <* role="option">

    parameters:
      ctx   - behave context object passed to a behave step
      name  - name that identifies the desired element on screen
      index - the index of the element if there are a few with the same name.

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(ctx.browser.execute,
                      name,
                      [
                          'option',
                          '*[role="option"]',
                      ],
                      index=index,
                      direction=fuzzy.Direction.RIGHT_TO_LEFT)


def select_dropdown_option(ctx, dropdown, option):
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


@step('I select the option "{option}" from the dropdown "{dropdown}"')
def select_option_from_dropdown(ctx, option, dropdown):
    select_dropdown_option(ctx, dropdown, option)


@step('I wait to select the option "{option}" from the dropdown "{dropdown}"', wait_for=True)
def wait_to_select_option_from_dropdown(ctx, option, dropdown):
    select_dropdown_option(ctx, dropdown, option)

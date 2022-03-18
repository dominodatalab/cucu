import humanize

from cucu import fuzzy, retry, step


def find_button(ctx, name, index=0):
    """
    find a button on screen by fuzzy matching on the name and index provided.

        * <button>
        * <input type="button">
        * <input type="submit">
        * <a>
        * <* role="button">
        * <* role="link">
        * <* role="menuitem">
        * <* role="option">
        * <* role="radio">

    note: the reason we're allowing link, menuitem, option and radio buttons
          to be clickable is that on screen they may simply look like a button.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired button on screen
      index(str):  the index of the button if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    button = fuzzy.find(ctx.browser,
                        name,
                        [
                            'button',
                            'input[type="button"]',
                            'input[type="submit"]',
                            'a',
                            '*[role="button"]',
                            '*[role="link"]',
                            '*[role="menuitem"]',
                            '*[role="option"]',
                        ],
                        index=index)

    prefix = '' if index == 0 else f'{humanize.ordinal(index)} '

    if button is None:
        raise RuntimeError(f'unable to find the {prefix}button "{name}"')

    return button


def find_n_click_button(ctx, name, index=0):
    """
    find the button with the name and index provided and click it

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired button on screen
      index(str):  the index of the button if there are duplicates

    raises:
        an error if the desired button is not found
    """

    button = find_button(ctx, name, index=index)
    button.click()


@step('I click the button "{name}"')
def clicks_the_button(ctx, name):
    find_n_click_button(ctx, name)


@step('I wait to click the button "{name}"')
def waits_to_clicks_the_button(ctx, name):
    retry(find_n_click_button)(ctx, name)


@step('I click the "{nth:nth}" button "{name}"')
def clicks_the_nth_button(ctx, nth, name):
    find_n_click_button(ctx, name, index=nth)


@step('I wait to click the "{nth:nth}" button "{name}"')
def waits_to_clicks_the_nth_button(ctx, nth, name):
    retry(find_n_click_button)(ctx, name, index=nth)


@step('I should see the button "{name}"')
def we_should_see_the_button(ctx, name):
    find_button(ctx, name)


@step('I wait to see the button "{name}"')
def waits_to_see_the_button(ctx, name):
    retry(find_button)(ctx, name)


@step('I should see the "{nth:nth}" button "{name}"')
def should_see_the_nth_button(ctx, nth, name):
    find_button(ctx, name, index=nth)


@step('I wait to see the "{nth:nth}" button "{name}"')
def waits_to_see_the_nth_button(ctx, nth, name):
    retry(find_button)(ctx, name, index=nth)

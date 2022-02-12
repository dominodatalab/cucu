# XXX: experimental
#
# menuitem steps
# https://www.w3.org/TR/wai-aria-1.1/#menuitem
#

from behave import step

from cucu import fuzzy


def find_menuitem(context, name, index=0):
    """
    find a menuitem containing the text provide.

    parameters:
      context - behave context object passed to a behave step
      name    - name that identifies the desired menuitem
      index   - the index of the element if there are a few with the same name.

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(context.browser.execute,
                      name,
                      ['*[role="menuitem"]'],
                      index=index)


@step('I should see the menu item "{name}"')
def should_see_the_menu_item(context, name):
    text = find_menuitem(context, name)

    if text is None:
        raise Exception(f'unable to find the menu item "{name}"')


@step('I wait to see the menu item "{name}"', wait_for=True)
def waits_toshould_see_the_menu_item(context, name):
    text = find_menuitem(context, name)

    if text is None:
        raise Exception(f'unable to find the menu item "{name}"')

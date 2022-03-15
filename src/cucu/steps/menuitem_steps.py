# XXX: experimental
#
# menuitem steps
# https://www.w3.org/TR/wai-aria-1.1/#menuitem
#
from cucu import fuzzy, retry, step


def find_menuitem(ctx, name, index=0):
    """
    find a menuitem containing the menuitem provide.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired menuitem on screen
      index(str):  the index of the menuitem if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    return fuzzy.find(ctx.browser,
                      name,
                      ['*[role="menuitem"]'],
                      index=index)


def find_n_assert_menuitem(ctx, name, index=0):
    """
    find a menuitem and assert its present

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired menuitem on screen
      index(str):  the index of the menuitem if there are duplicates

    returns:
        the WebElement that matches the provided arguments.

    """
    menuitem = find_menuitem(ctx, name, index=index)

    if menuitem is None:
        raise Exception(f'unable to find the menu item "{name}"')


@step('I should see the menu item "{name}"')
def should_see_the_menu_item(ctx, name):
    find_n_assert_menuitem(ctx, name)


@step('I wait to see the menu item "{name}"')
def waits_toshould_see_the_menu_item(ctx, name):
    retry(find_n_assert_menuitem)(ctx, name)

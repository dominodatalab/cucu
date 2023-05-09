from cucu import config, helpers, fuzzy, retry, step
from cucu.fuzzy.core import load_jquery_lib
from cucu.steps import step_utils
from functools import partial
from cucu.browser.frames import search_text_in_all_frames


def find_text(ctx, name, index=0):
    """
    find any element containing the text provide.

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired radio text on screen
      index(str):  the index of the radio text if there are duplicates

    returns:
        the WebElement that matches the provided arguments or None if none found
    """
    ctx.check_browser_initialized()
    return fuzzy.find(
        ctx.browser,
        name,
        ["*"],
        index=index,
        direction=fuzzy.Direction.LEFT_TO_RIGHT,
    )


# Also update the line number in the  scenario: `User gets the right stacktrace for steps using step helpers` when changing the code below.
helpers.define_should_see_thing_with_name_steps("text", find_text)
helpers.define_run_steps_if_I_can_see_element_with_name_steps("text", find_text)


@step(
    'I search for the regex "{regex}" on the current page and save the group "{name}" to the variable "{variable}"'
)
def search_for_regex_to_page_and_save(ctx, regex, name, variable):
    ctx.check_browser_initialized()
    ctx.browser.execute(load_jquery_lib())
    text = ctx.browser.execute(
        'return jQuery("body").children(":visible").text();'
    )
    search_function = partial(
        step_utils.search_and_save, regex=regex, name=name, variable=variable
    )
    search_text_in_all_frames(ctx.browser, search_function, value=text)


@step(
    'I match the regex "{regex}" on the current page and save the group "{name}" to the variable "{variable}"'
)
def match_for_regex_to_page_and_save(ctx, regex, name, variable):
    ctx.check_browser_initialized()
    ctx.browser.execute(load_jquery_lib())
    text = ctx.browser.execute(
        'return jQuery("body").children(":visible").text();'
    )
    search_function = partial(
        step_utils.match_and_save, regex=regex, name=name, variable=variable
    )
    search_text_in_all_frames(ctx.browser, search_function, value=text)


@step('I should see text matching the regex "{regex}" on the current page')
def search_for_regex_on_page(ctx, regex):
    ctx.check_browser_initialized()
    ctx.browser.execute(load_jquery_lib())
    text = ctx.browser.execute(
        'return jQuery("body").children(":visible").text();'
    )
    search_function = partial(step_utils.search, regex=regex)
    search_text_in_all_frames(ctx.browser, search_function, value=text)

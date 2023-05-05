from cucu import config, helpers, fuzzy, retry, step
from cucu.fuzzy.core import load_jquery_lib
from cucu.steps import step_utils


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


# https://github.com/cerebrotech/cucu/blob/fccae47d06abcc2e6528ef698c478ab52a97c754/features/cli/internals.feature#L5
# Above scenario depends on the line number of below statement. Adjust the above scenario accordingly if any changes to the  line number of the below statement.
helpers.define_should_see_thing_with_name_steps("text", find_text)
helpers.define_run_steps_if_I_can_see_element_with_name_steps("text", find_text)


@step(
    'I search for the regex "{regex}" on the current page and save the group "{name}" to the variable "{variable}"'
)
def search_for_regex_to_page_and_save(ctx, regex, name, variable):
    ctx.check_browser_initialized()
    ctx.browser.switch_to_default_frame()
    ctx.browser.execute(load_jquery_lib())
    text = ctx.browser.execute(
        'return jQuery("body").children(":visible").text();'
    )
    try:
        step_utils.search_and_save(regex, text, name, variable)
    except RuntimeError:
        frames = ctx.browser.execute(
            'return document.querySelectorAll("iframe");'
        )
        for frame in frames:
            # need to be in the default frame in order to switch to a child
            # frame w/o getting a stale element exception
            ctx.browser.switch_to_default_frame()
            ctx.browser.switch_to_frame(frame)
            ctx.browser.execute(load_jquery_lib())
            text = ctx.browser.execute(
                'return jQuery("body").children(":visible").text();'
            )
            try:
                step_utils.search_and_save(regex, text, name, variable)
            except RuntimeError:
                continue

            return


@step(
    'I match the regex "{regex}" on the current page and save the group "{name}" to the variable "{variable}"'
)
def match_for_regex_to_page_and_save(ctx, regex, name, variable):
    ctx.check_browser_initialized()
    ctx.browser.execute(load_jquery_lib())
    text = ctx.browser.execute(
        'return jQuery("body").children(":visible").text();'
    )
    step_utils.match_and_save(regex, text, name, variable)


@step('I should see text matching the regex "{regex}" on the current page')
def search_for_regex_on_page(ctx, regex):
    ctx.check_browser_initialized()
    ctx.browser.execute(load_jquery_lib())
    text = ctx.browser.execute(
        'return jQuery("body").children(":visible").text();'
    )
    step_utils.search(regex, text)

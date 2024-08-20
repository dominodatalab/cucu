from cucu import fuzzy, helpers, step
from cucu.browser.frames import try_in_frames_until_success
from cucu.steps import step_utils
from cucu.utils import take_saw_element_screenshot, text_in_current_frame


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
    element = fuzzy.find(
        ctx.browser,
        name,
        ["*"],
        index=index,
        direction=fuzzy.Direction.LEFT_TO_RIGHT,
    )

    take_saw_element_screenshot(ctx, "text", name, index, element)

    return element


# Also update the line number in the  scenario: `User gets the right stacktrace for steps using step helpers` when changing the code below.
helpers.define_should_see_thing_with_name_steps("text", find_text)
helpers.define_run_steps_if_I_can_see_element_with_name_steps(
    "text", find_text
)


@step(
    'I search for the regex "{regex}" on the current page and save the group "{name}" to the variable "{variable}"'
)
def search_for_regex_to_page_and_save(ctx, regex, name, variable):
    ctx.check_browser_initialized()

    def search_for_regex_in_frame():
        text = text_in_current_frame(ctx.browser)
        step_utils.search_and_save(
            regex=regex, value=text, name=name, variable=variable
        )

    try_in_frames_until_success(ctx.browser, search_for_regex_in_frame)


@step(
    'I match the regex "{regex}" on the current page and save the group "{name}" to the variable "{variable}"'
)
def match_for_regex_to_page_and_save(ctx, regex, name, variable):
    ctx.check_browser_initialized()

    def match_for_regex_in_frame():
        text = text_in_current_frame(ctx.browser)
        step_utils.match_and_save(
            regex=regex, value=text, name=name, variable=variable
        )

    try_in_frames_until_success(ctx.browser, match_for_regex_in_frame)


@step('I should see text matching the regex "{regex}" on the current page')
def search_for_regex_on_page(ctx, regex):
    ctx.check_browser_initialized()

    def search_for_regex_in_frame():
        text = text_in_current_frame(ctx.browser)
        step_utils.search(regex=regex, value=text)

    try_in_frames_until_success(ctx.browser, search_for_regex_in_frame)

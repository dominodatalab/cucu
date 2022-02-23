import tenacity

from behave import step
from cucu import fuzzy


def find_text(context, name, index=0):
    """
    find any element containing the text provide.

    parameters:
      context - behave context object passed to a behave step
      name    - name that identifies the desired element on screen
      index   - the index of the element if there are a few with the same name.

    returns:
        the WebElement that matches the provided arguments or None if none found
    """
    return fuzzy.find(context.browser.execute,
                      name,
                      ['*'],
                      index=index,
                      direction=fuzzy.Direction.LEFT_TO_RIGHT)


def assert_text_found(context, name, index=0):
    text = find_text(context, name)

    if text is None:
        raise Exception(f'unable to find the text "{name}"')


@step('I should see the text "{name}"')
def should_see_the_text(context, name):
    assert_text_found(context, name)


@step('I wait to see the text "{name}"', wait_for=True)
def wait_see_the_text(context, name):
    assert_text_found(context, name)


# XXX: the way we do wait for steps needs to be generalized
@step('I wait up to "{seconds}" seconds to see the text "{name}"')
def wait_up_to_seconds_to_see_the_text(context, seconds, name):
    assert_func = tenacity.retry(stop=tenacity.stop_after_delay(int(seconds)),
                                 wait=tenacity.wait_fixed(0.250))(assert_text_found)

    assert_func(context, name)


@step('I should not see the text "{name}"')
def should_not_see_the_text(context, name):
    text = find_text(context, name)

    if text is not None:
        raise Exception(f'able to find the text "{name}"')

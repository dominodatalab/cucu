import parse
import operator
import re
import sys
import time

from behave import register_type
from behave.model_describe import ModelPrinter
from cucu import logger, run_steps, step
from cucu.config import CONFIG
from strip_ansi import strip_ansi

NTH_REGEX = r"(\d+)(nd|th|rd|st)"


@parse.with_pattern(NTH_REGEX)
def parse_nth(nth):
    matcher = re.match(NTH_REGEX, nth)

    if matcher is None:
        raise Exception(f"nth expression {nth} is invalid")

    number, _ = matcher.groups()
    return int(number) - 1


register_type(nth=parse_nth)


def is_disabled(element):
    """
    internal method to check an element is disabled
    """
    return element.get_attribute("disabled")


def is_not_disabled(element):
    """
    internal method to check an element is not disabled
    """
    return not is_disabled(element)


@step("I run a step that fails")
def this_step_fails(_):
    raise Exception("failing on purpose")


@step('I sleep for "{value}" seconds')
def sleep(ctx, value):
    time.sleep(int(value))


@step('I echo "{value}"')
def i_echo(ctx, value):
    print(f"{value}\n")


@step("I echo the following")
def i_echo_the_following(ctx):
    if ctx.text is not None:
        print(f"{ctx.text}\n")

    elif ctx.table is not None:
        printer = ModelPrinter(sys.stdout)
        printer.print_table(ctx.table)
        print("")


@step('I log "{message}" at level "{level}"')
def i_log(_, message, level):
    operator.methodcaller(level.lower(), message)(logger)


@step('I log the following at level "{level}"')
def i_log_following(ctx, level):
    operator.methodcaller(level.lower(), ctx.text)(logger)


@step('I strip ansi codes from "{value}" and save to the variable "{variable}"')
def strip_ansi_codes_and_save(ctx, value, variable):
    CONFIG[variable] = strip_ansi(value)


@step('I expect the following step to fail with "{message}"')
def expect_the_following_step_to_fail(ctx, message):
    try:
        run_steps(ctx, ctx.text)
    except Exception as exception:
        if str(exception).find(message) == -1:
            raise RuntimeError(
                f'expected failure message was "{str(exception)}" not "{message}"'
            )
        return

    raise RuntimeError("previous steps did not fail!")


@step('I should see the previous step took less than "{seconds}" seconds')
def should_see_previous_step_took_less_than(ctx, seconds):
    if ctx.previous_step_duration > float(seconds):
        raise RuntimeError(
            f"previous step took {ctx.previous_step_duration}, which is more than {seconds}"
        )


@step('I should see the previous step took more than "{seconds}" seconds')
def should_see_previous_step_took_more_than(ctx, seconds):
    if ctx.previous_step_duration < float(seconds):
        raise RuntimeError(
            f"previous step took {ctx.previous_step_duration}, which is less than {seconds}"
        )

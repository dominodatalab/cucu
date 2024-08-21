import operator
import re
import sys
import time

import parse
from behave import register_type
from behave.model_describe import ModelPrinter

from cucu import logger, step
from cucu.ansi_parser import remove_ansi
from cucu.config import CONFIG

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
    return (
        element.get_attribute("disabled")
        or element.get_attribute("aria-disabled") == "true"
    )


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


@step(
    'I strip ansi codes from "{value}" and save to the variable "{variable}"'
)
def strip_ansi_codes_and_save(ctx, value, variable):
    CONFIG[variable] = remove_ansi(value)

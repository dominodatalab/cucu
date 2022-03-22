import sys
import time

from cucu import run_steps, step
from behave.model_describe import ModelPrinter
from cucu.config import CONFIG
from strip_ansi import strip_ansi


@step("I run a step that fails")
def this_step_fails(_):
    raise Exception("failing on purpose")


@step('I sleep for "{value}" seconds')
def sleep(context, value):
    time.sleep(int(value))


@step('I echo "{value}"')
def i_echo(context, value):
    print(f"{value}\n")


@step("I echo the following")
def i_echo_the_following(context):
    if context.text is not None:
        print(f"{context.text}\n")

    elif context.table is not None:
        printer = ModelPrinter(sys.stdout)
        # indentation is 2 spaces for Scenario 2 spaces for the start of keyword
        # "Given" and the length of "Given" minus one so we align with the last
        # character.
        printer.print_table(context.table, " " * 8)


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

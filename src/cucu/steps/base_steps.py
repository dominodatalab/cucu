import sys
import time

from behave import step
from behave.model_describe import ModelPrinter
from cucu.config import CONFIG
from strip_ansi import strip_ansi


@step('I run a step that fails')
def this_step_fails(_):
    raise Exception('failing on purpose')


@step('I sleep for "{value}" seconds')
def sleep(context, value):
    time.sleep(int(value))


@step('I echo "{value}"')
def i_echo(context, value):
    print(f'{value}\n')


@step('I echo the following')
def i_echo_the_following(context):
    if context.text is not None:
        print(f'{context.text}\n')

    elif context.table is not None:
        printer = ModelPrinter(sys.stdout)
        # indentation is 2 spaces for Scenario 2 spaces for the start of keyword
        # "Given" and the length of "Given" minus one so we align with the last
        # character.
        printer.print_table(context.table, ' ' * 8)


@step('I strip ansi codes from "{value}" and save to the variable "{variable}"')
def strip_ansi_codes_and_save(ctx, value, variable):
    CONFIG[variable] = strip_ansi(value)

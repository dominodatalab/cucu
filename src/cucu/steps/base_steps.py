import time

from behave import step
from behave.model_describe import ModelPrinter


@step('I run a step that fails')
def this_step_fails(_):
    raise Exception('failing on purpose')


@step('I sleep for "{value}" seconds')
def sleep(context, value):
    time.sleep(int(value))


@step('I echo "{value}"')
def i_echo(context, value):
    context.print(value)


@step('I echo the following')
def i_echo_the_following(context):
    if context.text is not None:
        context.print(context.text)
    elif context.table is not None:
        printer = ModelPrinter(context.stdout)
        # indentation is 2 spaces for Scenario 2 spaces for the start of keyword
        # "Given" and the length of "Given" minus one so we align with the last
        # character.
        printer.print_table(context.table, ' ' * 8)

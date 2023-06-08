"""
various cucu utilities can be placed here and then exposed publicly through
the src/cucu/__init__.py
"""
import logging

from tabulate import DataRow, TableFormat, tabulate
from tenacity import (
    before_sleep_log,
    retry_if_not_exception_type,
    stop_after_delay,
    wait_fixed,
)
from tenacity import (
    retry as retrying,
)

from cucu import logger
from cucu.config import CONFIG

GHERKIN_TABLEFORMAT = TableFormat(
    lineabove=None,
    linebelowheader=None,
    linebetweenrows=None,
    linebelow=None,
    headerrow=DataRow("|", "|", "|"),
    datarow=DataRow("|", "|", "|"),
    padding=1,
    with_header_hide=["lineabove"],
)


class StopRetryException(Exception):
    pass


def format_gherkin_table(table, headings=[], prefix=""):
    formatted = tabulate(table, headings, tablefmt=GHERKIN_TABLEFORMAT)
    if prefix == "":
        return formatted

    return prefix + formatted.replace("\n", f"\n{prefix}")


#
# code below adapted from:
# https://github.com/behave/behave/blob/994dbfe30e2a372182ea613333e06f069ab97d4b/behave/runner.py#L385
# so we can have the sub steps printed in the console logs
#
def run_steps(ctx, steps_text):
    """
    run sub steps within an existing step definition but also log their output
    so that its easy to see what is happening.
    """

    # -- PREPARE: Save original ctx data for current step.
    # Needed if step definition that called this method uses .table/.text
    original_table = getattr(ctx, "table", None)
    original_text = getattr(ctx, "text", None)

    # first time a given step calls substeps we want to move the step_index
    # so it starts the followings steps the right point.
    if not ctx.current_step.has_substeps:
        ctx.step_index += 1

    ctx.current_step.has_substeps = True

    ctx.feature.parser.variant = "steps"
    steps = ctx.feature.parser.parse_steps(steps_text)

    current_step = ctx.current_step
    current_step_start_time = ctx.start_time

    # XXX: I want to get back to this and find a slightly better way to handle
    #      these substeps without mucking around with so much state in behave
    #      but for now this works correctly and existing tests work as expected.
    try:
        with ctx._use_with_behave_mode():
            for step in steps:
                for formatter in ctx._runner.formatters:
                    step.is_substep = True
                    formatter.insert_step(step, index=ctx.step_index)

                passed = step.run(ctx._runner, quiet=False, capture=False)

                if not passed:
                    raise RuntimeError(step.error_message)

            # -- FINALLY: Restore original ctx data for current step.
            ctx.table = original_table
            ctx.text = original_text
    finally:
        ctx.current_step = current_step
        ctx.start_time = current_step_start_time

    return True


def retry(func, wait_up_to_s=None, retry_after_s=None):
    """
    utility retry function that can retry the provided `func` for the maximum
    amount of seconds specified by `wait_up_to_s` and wait the number of seconds
    specified in `retry_after_s`
    """
    if wait_up_to_s is None:
        wait_up_to_s = float(CONFIG["CUCU_STEP_WAIT_TIMEOUT_S"])

    if retry_after_s is None:
        retry_after_s = float(CONFIG["CUCU_STEP_RETRY_AFTER_S"])

    @retrying(
        stop=stop_after_delay(wait_up_to_s),
        wait=wait_fixed(retry_after_s),
        retry=retry_if_not_exception_type(StopRetryException),
        before_sleep=before_sleep_log(logger, logging.DEBUG),
    )
    def new_decorator(*args, **kwargs):
        ctx = CONFIG["__CUCU_CTX"]

        for hook in CONFIG["__CUCU_BEFORE_RETRY_HOOKS"]:
            hook(ctx)

        return func(*args, **kwargs)

    return new_decorator

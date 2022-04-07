"""
various cucu utilities can be placed here and then exposed publicly through
the src/cucu/__init__.py
"""

from cucu.config import CONFIG
from tenacity import retry as retrying
from tenacity import stop_after_delay, wait_fixed


#
# code below adapted from:
# https://github.com/behave/behave/blob/994dbfe30e2a372182ea613333e06f069ab97d4b/behave/runner.py#L385
# so we can have the sub steps printed in the console logs
#
def run_steps(context, steps_text):
    """
    run sub steps within an existing step definition but also log their output
    so that its easy to see what is happening.
    """

    # -- PREPARE: Save original context data for current step.
    # Needed if step definition that called this method uses .table/.text
    original_table = getattr(context, "table", None)
    original_text = getattr(context, "text", None)

    context.feature.parser.variant = "steps"
    steps = context.feature.parser.parse_steps(steps_text)

    current_step = context.current_step
    current_step_index = context.step_index

    # XXX: I want to get back to this and find a slightly better way to handle
    #      these substeps without mucking around with so much state in behave
    #      but for now this works correctly and existing tests work as expected.
    try:
        with context._use_with_behave_mode():
            index = 1

            context.step_index += 1
            for step in steps:
                for formatter in context._runner.formatters:
                    step_index = formatter.steps.index(current_step)
                    step.substep = True
                    formatter.insert_step(step, index=step_index + index)
                index += 1

                passed = step.run(context._runner, quiet=False, capture=False)

                if not passed:
                    raise RuntimeError(step.error_message)

            # -- FINALLY: Restore original context data for current step.
            context.table = original_table
            context.text = original_text

    finally:
        context.step_index = current_step_index
        # XXX: icky relationships between this and the after_step hooks in
        #      the environment.py which handles screenshots
        context.substep_increment = len(steps)

    CONFIG["CUCU_WROTE_TO_STDOUT"] = True

    return True


def retry(
    func,
    wait_up_to_s=float(CONFIG["CUCU_STEP_WAIT_TIMEOUT_S"]),
    retry_after_s=float(CONFIG["CUCU_STEP_RETRY_AFTER_S"]),
):
    @retrying(
        stop=stop_after_delay(wait_up_to_s), wait=wait_fixed(retry_after_s)
    )
    def new_decorator(*args, **kwargs):
        return func(*args, **kwargs)

    return new_decorator

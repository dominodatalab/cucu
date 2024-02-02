from cucu import (
    StopRetryException,
    register_after_this_scenario_hook,
    retry,
    run_steps,
    step,
)


@step("I use a step with substeps that log")
def step_with_substeps_that_log(context):
    run_steps(
        context,
        """
    When I echo "hello"
     And I echo "cruel"
     And I echo "world"
    """,
    )


@step("I use a step with substeps")
def step_with_substeps(context):
    run_steps(
        context,
        """
    When I do nothing
     And I do nothing
     And I do nothing
    """,
    )


@step("I use a step with substeps that fail")
def step_with_substeps_that_fail(context):
    run_steps(
        context,
        """
    When I fail
    """,
    )


@step("I use a step with substeps that waits to fail")
def step_with_substeps_that_waits_to_fail(context):
    run_steps(
        context,
        """
    When I wait to fail
    """,
    )


@step("I do nothing")
def do_nothing(_):
    pass


@step("I fail")
def i_fail(_):
    raise RuntimeError("step fails on purpose")


@step("I wait to fail")
def i_wait_to_fail(_):
    def fail():
        raise RuntimeError("step fails on purpose after a while")

    retry(fail)()


@step("I error after-scenario hook")
def i_error_after_hook(_):
    def after_hook_fail(_):
        raise RuntimeError("after-hook errors on purpose")

    register_after_this_scenario_hook(after_hook_fail)


@step('I use a step with "{nth:nth}" usage')
def uses_nth_step(ctx, nth):
    print("just a step that nth behave argument type")


def stop_retry(ctx):
    raise StopRetryException("Just cause I wanted to stop early")


@step("I use retry but stop immediately")
def use_retry_but_stop_immediately(ctx):
    retry(stop_retry)(ctx)

from cucu import (
    CucuPassThroughError,
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


@step("I use a step with substeps that sleep")
def step_with_substeps_that_sleep(context):
    run_steps(
        context,
        """
    When I sleep for "1" seconds
     And I sleep for "1" seconds
     And I sleep for "1" seconds
    """,
    )


@step("I use a step with substeps and a heading")
def step_with_substeps_and_heading(context):
    run_steps(
        context,
        """
    Given I do nothing
     When I do nothing
        * ## Spec as H2 with two #'s but demoted under parent step
      And I do nothing
     Then I do nothing
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
    raise AssertionError("step fails on purpose")


@step("I wait to fail")
def i_wait_to_fail(_):
    def fail():
        raise AssertionError("step fails on purpose after a while")

    retry(fail)()


@step("I register two near-instant after-scenario hooks")
def register_two_instant_hooks(_):
    def instant_hook_one(_ctx):
        pass

    def instant_hook_two(_ctx):
        pass

    register_after_this_scenario_hook(instant_hook_one)
    register_after_this_scenario_hook(instant_hook_two)


@step("I error after-scenario hook")
def i_error_after_hook(_):
    def after_hook_fail(_):
        raise AssertionError("after-hook errors on purpose")

    register_after_this_scenario_hook(after_hook_fail)


@step('I use a step with "{nth:nth}" usage')
def uses_nth_step(ctx, nth):
    print("just a step that nth behave argument type")


def stop_retry(ctx):
    raise StopRetryException("Just cause I wanted to stop early")


@step(
    "I use retry but stop immediately", exception_passthru=StopRetryException
)
def use_retry_but_stop_immediately(ctx):
    retry(stop_retry)(ctx)


@step('I raise AssertionError with message "{msg}"')
def raise_assertion_error(_, msg):
    raise AssertionError(msg)


@step('I raise CucuPassThroughError with message "{msg}"')
def raise_cucu_passthrough_error(_, msg):
    raise CucuPassThroughError(msg)


@step('I raise CucuPassThroughError wrapping ValueError "{msg}"')
def raise_cucu_passthrough_wrapping_value_error(_, msg):
    raise CucuPassThroughError() from ValueError(msg)


@step('I raise ValueError with message "{msg}"')
def raise_value_error(_, msg):
    raise ValueError(msg)


@step(
    'I raise ValueError with exception_passthru with message "{msg}"',
    exception_passthru=ValueError,
)
def raise_value_error_passthrough(_, msg):
    raise ValueError(msg)


@step(
    'I raise ValueError with exception_passthru tuple with message "{msg}"',
    exception_passthru=(ValueError, TypeError),
)
def raise_value_error_passthrough_tuple(_, msg):
    raise ValueError(msg)


@step(
    'I raise TypeError with exception_passthru tuple with message "{msg}"',
    exception_passthru=(ValueError, TypeError),
)
def raise_type_error_passthrough_tuple(_, msg):
    raise TypeError(msg)


@step(
    'I raise RuntimeError with exception_passthru tuple with message "{msg}"',
    exception_passthru=(ValueError, TypeError),
)
def raise_runtime_error_with_tuple_passthrough(_, msg):
    raise RuntimeError(msg)

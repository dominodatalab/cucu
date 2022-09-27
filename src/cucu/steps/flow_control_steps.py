import os
import subprocess
import time

from cucu import logger, retry, run_steps, step
from cucu.hooks import (
    register_after_this_scenario_hook,
    register_before_step_hook,
    register_after_step_hook,
    register_before_retry_hook,
)
from cucu.config import CONFIG
from cucu.cli.run import behave


@step('I skip this scenario if the file at "{filepath}" exists')
def skip_scenario_if_file_exists(ctx, filepath):
    if os.path.exists(filepath):
        ctx.scenario.skip(
            reason='skipping scenario since file at "{filepath}" exists'
        )


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


@step("I wait to see the following steps succeed")
def wait_to_see_the_following_steps_suceed(ctx):
    retry(run_steps)(ctx, ctx.text)


@step('I wait up to "{seconds}" seconds to see the following steps succeed')
def wait_up_to_seconds_to_see_the_following_steps_suceed(ctx, seconds):
    retry(run_steps, wait_up_to_s=float(seconds))(ctx, ctx.text)


def wait_for_steps_to_fail(ctx, steps, timeout=None):
    def steps_should_fail():
        try:
            run_steps(ctx, steps)
        except:
            return

        raise RuntimeError("underlying steps did not fail")

    retry(steps_should_fail, wait_up_to_s=timeout)()


@step("I wait to see the following steps fail")
def wait_to_see_the_following_steps_fail(ctx):
    wait_for_steps_to_fail(ctx, ctx.text)


@step('I wait up to "{seconds}" seconds to see the following steps fail')
def wait_up_to_seconds_to_see_the_following_steps_fail(ctx, seconds):
    wait_for_steps_to_fail(ctx, ctx.text, timeout=float(seconds))


def repeat_steps(ctx, steps, repeat, variable=None):
    for index in range(0, repeat):
        if variable is not None:
            CONFIG[variable] = index + 1

        run_steps(ctx, steps)


@step('I repeat "{repeat}" times the following steps')
def repeat_n_times_the_following_steps(ctx, repeat):
    repeat_steps(ctx, ctx.text, int(repeat))


@step(
    'I repeat "{repeat}" times the following steps with iteration variable "{variable}"'
)
def repeat_n_times_the_following_steps_with_variable(ctx, repeat, variable):
    repeat_steps(ctx, ctx.text, int(repeat), variable=variable)


@step('I run the following steps if the file at "{filepath}" does not exist')
def run_steps_if_file_does_not_exist(ctx, filepath):
    if not os.path.exists(filepath):
        run_steps(ctx, ctx.text)


@step('I run the following steps if the file at "{filepath}" exists')
def run_steps_if_file_exists(ctx, filepath):
    if os.path.exists(filepath):
        run_steps(ctx, ctx.text)


@step('I run the following timed steps as "{name}"')
def run_and_measure_the_following_steps(ctx, name):
    start = time.time()
    run_steps(ctx, ctx.text)
    duration = round(time.time() - start, 3)
    logger.info(f'"{name}" timer took {duration}s')


@step('I start the timer "{name}"')
def start_the_timer(ctx, name):
    ctx.step_timers[name] = time.time()


@step('I stop the timer "{name}"')
def stop_the_timer(ctx, name):
    if name not in ctx.step_timers:
        raise RuntimeError(f'no previously started timer with name "{name}"')
    start = ctx.step_timers[name]
    del ctx.step_timers[name]

    duration = round(time.time() - start, 3)
    logger.info(f'"{name}" timer took {duration}s')


def run_feature(ctx, filepath, results):
    command = f"cucu run {filepath} --results {results}"
    process = subprocess.run(command, shell=True)

    return_code = process.returncode
    if return_code != 0:
        raise RuntimeError(
            f'"{command}" exited with {return_code}, see above for details'
        )


@step(
    'I run the feature at "{feature_filepath}" with results at "{results_filepath}"'
)
def run_feature_at(ctx, feature_filepath, results_filepath):
    run_feature(ctx, feature_filepath, results_filepath)


@step(
    'I run the feature at "{feature_filepath}" with results at "{results_filepath}" if the file at "{filepath}" does not exist'
)
def run_feature_if_file_does_not_exist(
    ctx, feature_filepath, results_filepath, filepath
):
    if not os.path.exists(filepath):
        run_feature(ctx, feature_filepath, results_filepath)


@step(
    'I run the feature at "{feature_filepath}" with results at "{results_filepath}" if the file at "{filepath}" exists'
)
def run_feature_if_file_exists(
    ctx, feature_filepath, results_filepath, filepath
):
    if os.path.exists(filepath):
        run_feature(ctx, feature_filepath, results_filepath)


@step("I run the following steps at the end of the current scenario")
def run_the_following_steps_at_end_of_scenario(ctx):
    steps = ctx.text

    def run_final_steps(ctx):
        run_steps(ctx, steps)

    register_after_this_scenario_hook(run_final_steps)


def run_steps_silently(ctx, steps_text):
    """
    internal method used to run steps without producing any output about them
    and also making sure that we do not trigger other after/before step calls
    """
    steps = ctx.feature.parser.parse_steps(steps_text)
    with ctx._use_with_behave_mode():
        CONFIG["__CUCU_BEFORE_STEP_HOOKS_DISABLED"] = True
        CONFIG["__CUCU_AFTER_STEP_HOOKS_DISABLED"] = True
        try:
            for step in steps:
                result = step.run(ctx._runner, quiet=True, capture=False)
                if not result:
                    raise RuntimeError(f"previous step failed")
        finally:
            CONFIG["__CUCU_BEFORE_STEP_HOOKS_DISABLED"] = False
            CONFIG["__CUCU_AFTER_STEP_HOOKS_DISABLED"] = False


@step('I create the before step handler "{name}" with the following steps')
def create_before_step_handler(ctx, name):
    steps_text = ctx.text

    def before_step(ctx):
        logger.debug(f'running before step handler "{name}"')
        try:
            run_steps_silently(ctx, steps_text)
            logger.info(f'before step handler "{name}" ran successfully')
        except Exception as exc:
            # log the failure in info as a step handler isn't suppose to fail
            # the test run but just handle some before step situations
            logger.debug(f'before step handler "{name}" failed with "{exc}"')

    register_before_step_hook(before_step)


@step('I create the after step handler "{name}" with the following steps')
def create_after_step_handler(ctx, name):
    steps_text = ctx.text

    def after_step(ctx):
        logger.debug(f'running after step handler "{name}"')
        try:
            run_steps_silently(ctx, steps_text)
            logger.info(f'after step handler "{name}" ran successfully')
        except Exception as exc:
            # log the failure in info as a step handler isn't suppose to fail
            # the test run but just handle some after step situations
            logger.debug(f'after step handler "{name}" failed with "{exc}"')

    register_after_step_hook(after_step)


@step('I create the before retry handler "{name}" with the following steps')
def create_before_retry_handler(ctx, name):
    steps_text = ctx.text

    def before_retry(ctx):
        logger.debug(f'running before retry handler "{name}"')
        try:
            run_steps_silently(ctx, steps_text)
            logger.info(f'before retry handler "{name}" ran successfully')
        except Exception as exc:
            # log the failure in info as a step handler isn't suppose to fail
            # the test run but just handle some after step situations
            logger.debug(f'before retry handler "{name}" failed with "{exc}"')

    register_before_retry_hook(before_retry)

import glob
import json
import os
import shutil
import sys
import time
import uuid

from cucu import config, logger
from cucu.config import CONFIG
from cucu import init_hook_variables
from cucu.page_checks import init_page_checks


def escape_filename(string):
    """
    escape string so it can be used as a filename safely.
    """
    return string.replace("/", "_")


def before_all(context):
    context.substep_increment = 0
    CONFIG.snapshot()


def before_feature(context, feature):
    if config.CONFIG["CUCU_RESULTS_DIR"] is not None:
        feature_dir = os.path.join(
            config.CONFIG["CUCU_RESULTS_DIR"], feature.name
        )
        CONFIG["FEATURE_RESULTS_DIR"] = feature_dir


def after_feature(context, feature):
    pass


def before_scenario(context, scenario):
    # we want every scenario to start with the exact same reinitialized config
    # values and not really bleed values between scenario runs
    CONFIG.restore()
    init_hook_variables()
    init_page_checks()

    if config.CONFIG["CUCU_RESULTS_DIR"] is not None:
        feature_path = (config.CONFIG["FEATURE_RESULTS_DIR"],)
        scenario_dir = os.path.join(
            config.CONFIG["CUCU_RESULTS_DIR"],
            scenario.feature.name,
            scenario.name,
        )

        CONFIG["SCENARIO_RESULTS_DIR"] = scenario_dir
        os.makedirs(scenario_dir, exist_ok=True)
        context.scenario_dir = scenario_dir

    context.scenario = scenario
    context.step_index = 0
    context.browsers = []
    context.browser = None

    # internal cucu config variables
    CONFIG["SCENARIO_RUN_ID"] = uuid.uuid1().hex


def after_scenario(context, scenario):
    # copy any files in the CUCU_BROWSER_DOWNLOADS_DIR to the results
    # directory for that scenario
    downloads_dir = CONFIG["SCENARIO_DOWNLOADS_DIR"]

    if downloads_dir:
        scenario_downloads_dir = os.path.join(
            CONFIG["SCENARIO_RESULTS_DIR"], "downloads"
        )
        os.makedirs(scenario_downloads_dir, exist_ok=True)
        filepaths = glob.iglob(os.path.join(downloads_dir, "*.*"))
        for filepath in filepaths:
            shutil.copy(filepath, scenario_downloads_dir)

    if CONFIG.true("CUCU_KEEP_BROWSER_ALIVE"):
        logger.debug("keeping browser alive between sessions")

    else:
        if len(context.browsers) != 0:
            logger.debug("quitting browser between sessions")

        # close the browser unless someone has set the keep browser alive
        # environment variable which allows tests to reuse the same browser
        # session
        for browser in context.browsers:
            # save the browser logs to the current scenarios results directory
            scenario_dir = os.path.join(
                config.CONFIG["CUCU_RESULTS_DIR"],
                scenario.feature.name,
                scenario.name,
            )
            browser_log_filepath = os.path.join(
                scenario_dir, "logs", "browser_console.log"
            )

            os.makedirs(os.path.dirname(browser_log_filepath), exist_ok=True)
            with open(browser_log_filepath, "w") as output:
                for log in browser.get_log():
                    output.write(f"{json.dumps(log)}\n")

            browser.quit()

        context.browsers = []

    # run after all scenario hooks
    for hook in CONFIG["__CUCU_AFTER_SCENARIO_HOOKS"]:
        hook(context)

    # run after this scenario hooks
    for hook in CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"]:
        hook(context)

    CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"] = []


def before_step(context, step):
    step.stdout = []
    step.stderr = []
    context.current_step = step
    context.start_time = time.monotonic()


def after_step(context, step):
    context.end_time = time.monotonic()
    context.previous_step_duration = context.end_time - context.start_time

    # grab the captured output during the step run and reset the wrappers
    step.stdout = sys.stdout.captured()
    step.stderr = sys.stderr.captured()

    if context.browser is not None and not context.substep_increment:
        step_name = escape_filename(step.name)
        filepath = os.path.join(
            context.scenario_dir, f"{context.step_index} - {step_name}.png"
        )

        context.browser.screenshot(filepath)

    if context.substep_increment != 0:
        context.step_index += context.substep_increment
        context.substep_increment = 0

    context.step_index += 1

    if CONFIG.bool("CUCU_IPDB_ON_FAILURE") and step.status == "failed":
        context._runner.stop_capture()
        import ipdb

        ipdb.post_mortem(step.exc_traceback)

    # run before all scenario hooks
    for hook in CONFIG["__CUCU_BEFORE_SCENARIO_HOOKS"]:
        hook(context)

    # run before this scenario hooks
    for hook in CONFIG["__CUCU_BEFORE_THIS_SCENARIO_HOOKS"]:
        hook(context)

    CONFIG["__CUCU_BEFORE_THIS_SCENARIO_HOOKS"] = []

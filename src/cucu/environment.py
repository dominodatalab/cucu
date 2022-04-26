import glob
import json
import os
import shutil
import sys
import time
import uuid

from cucu import config, logger
from cucu.config import CONFIG
from cucu import init_global_hook_variables, init_scenario_hook_variables
from cucu.page_checks import init_page_checks


init_global_hook_variables()

CONFIG.define(
    "FEATURE_RESULTS_DIR",
    "the results directory for the currently executing feature",
    default=None,
)
CONFIG.define(
    "SCENARIO_RESULTS_DIR",
    "the results directory for the currently executing scenario",
    default=None,
)
CONFIG.define(
    "SCENARIO_DOWNLOADS_DIR",
    "the browser downloads directory for the currently " "executing scenario",
    default=None,
)


def escape_filename(string):
    """
    escape string so it can be used as a filename safely.
    """
    return string.replace("/", "_")


def before_all(ctx):
    ctx.substep_increment = 0
    CONFIG.snapshot()


def before_feature(ctx, feature):
    if config.CONFIG["CUCU_RESULTS_DIR"] is not None:
        results_dir = config.CONFIG["CUCU_RESULTS_DIR"]
        ctx.feature_dir = os.path.join(results_dir, feature.name)
        CONFIG["FEATURE_RESULTS_DIR"] = ctx.feature_dir


def after_feature(ctx, feature):
    pass


def before_scenario(ctx, scenario):
    # we want every scenario to start with the exact same reinitialized config
    # values and not really bleed values between scenario runs
    CONFIG.restore()
    init_scenario_hook_variables()
    init_page_checks()

    if config.CONFIG["CUCU_RESULTS_DIR"] is not None:
        ctx.scenario_dir = os.path.join(ctx.feature_dir, scenario.name)
        CONFIG["SCENARIO_RESULTS_DIR"] = ctx.scenario_dir
        os.makedirs(ctx.scenario_dir, exist_ok=True)

        ctx.scenario_downloads_dir = os.path.join(ctx.scenario_dir, "downloads")
        CONFIG["SCENARIO_DOWNLOADS_DIR"] = ctx.scenario_downloads_dir

    ctx.scenario = scenario
    ctx.step_index = 0
    ctx.browsers = []
    ctx.browser = None

    # internal cucu config variables
    CONFIG["SCENARIO_RUN_ID"] = uuid.uuid1().hex

    # run before all scenario hooks
    for hook in CONFIG["__CUCU_BEFORE_SCENARIO_HOOKS"]:
        hook(ctx)


def after_scenario(ctx, scenario):
    # copy any files in the CUCU_BROWSER_DOWNLOADS_DIR to the results
    # directory for that scenario
    downloads_dir = CONFIG["SCENARIO_DOWNLOADS_DIR"]

    if downloads_dir:
        os.makedirs(ctx.scenario_downloads_dir, exist_ok=True)
        filepaths = glob.iglob(os.path.join(downloads_dir, "*.*"))
        for filepath in filepaths:
            shutil.copy(filepath, ctx.scenario_downloads_dir)

    if CONFIG.true("CUCU_KEEP_BROWSER_ALIVE"):
        logger.debug("keeping browser alive between sessions")

    else:
        if len(ctx.browsers) != 0:
            logger.debug("quitting browser between sessions")

        # close the browser unless someone has set the keep browser alive
        # environment variable which allows tests to reuse the same browser
        # session
        for browser in ctx.browsers:
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

        ctx.browsers = []

    # run after all scenario hooks
    for hook in CONFIG["__CUCU_AFTER_SCENARIO_HOOKS"]:
        hook(ctx)

    # run after this scenario hooks
    for hook in CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"]:
        hook(ctx)

    CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"] = []


def before_step(ctx, step):
    step.stdout = []
    step.stderr = []
    ctx.current_step = step
    ctx.start_time = time.monotonic()

    # run before all step hooks
    for hook in CONFIG["__CUCU_BEFORE_STEP_HOOKS"]:
        hook(ctx)


def after_step(ctx, step):
    ctx.end_time = time.monotonic()
    ctx.previous_step_duration = ctx.end_time - ctx.start_time

    # grab the captured output during the step run and reset the wrappers
    step.stdout = sys.stdout.captured()
    step.stderr = sys.stderr.captured()

    if ctx.browser is not None and not ctx.substep_increment:
        step_name = escape_filename(step.name)
        filepath = os.path.join(
            ctx.scenario_dir, f"{ctx.step_index} - {step_name}.png"
        )

        ctx.browser.screenshot(filepath)

        if CONFIG["CUCU_MONITOR_PNG"] is not None:
            shutil.copyfile(filepath, CONFIG["CUCU_MONITOR_PNG"])

    if ctx.substep_increment != 0:
        ctx.step_index += ctx.substep_increment
        ctx.substep_increment = 0

    ctx.step_index += 1

    if CONFIG.bool("CUCU_IPDB_ON_FAILURE") and step.status == "failed":
        ctx._runner.stop_capture()
        import ipdb

        ipdb.post_mortem(step.exc_traceback)

    CONFIG["__CUCU_BEFORE_THIS_SCENARIO_HOOKS"] = []

    # run after all step hooks
    for hook in CONFIG["__CUCU_AFTER_STEP_HOOKS"]:
        hook(ctx)

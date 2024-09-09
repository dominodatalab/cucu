import datetime
import hashlib
import json
import os
import sys
import time
import traceback
from functools import partial

from cucu import config, init_scenario_hook_variables, logger
from cucu.config import CONFIG
from cucu.page_checks import init_page_checks
from cucu.utils import ellipsize_filename, take_screenshot

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


init_page_checks()


def check_browser_initialized(ctx):
    """
    check browser session initialized otherwise throw an exception indicating
    such to be used consistently by all steps in this module.
    """

    if ctx.browser is None:
        raise RuntimeError("browser not currently open")


def before_all(ctx):
    CONFIG["__CUCU_CTX"] = ctx
    CONFIG.snapshot()
    ctx.check_browser_initialized = partial(check_browser_initialized, ctx)
    for hook in CONFIG["__CUCU_BEFORE_ALL_HOOKS"]:
        hook(ctx)


def after_all(ctx):
    # run the after all hooks
    for hook in CONFIG["__CUCU_AFTER_ALL_HOOKS"]:
        hook(ctx)


def before_feature(ctx, feature):
    if config.CONFIG["CUCU_RESULTS_DIR"] is not None:
        results_dir = config.CONFIG["CUCU_RESULTS_DIR"]
        ctx.feature_dir = os.path.join(
            results_dir, ellipsize_filename(feature.name)
        )
        CONFIG["FEATURE_RESULTS_DIR"] = ctx.feature_dir


def after_feature(ctx, feature):
    pass


def before_scenario(ctx, scenario):
    # we want every scenario to start with the exact same reinitialized config
    # values and not really bleed values between scenario runs
    CONFIG.restore()

    # we should load any cucurc.yml files in the path to the feature file
    # we are about to run so that the config values set for this feature are
    # correctly loaded.
    CONFIG.load_cucurc_files(ctx.feature.filename)

    init_scenario_hook_variables()

    ctx.scenario = scenario
    ctx.step_index = 0
    ctx.browsers = []
    ctx.browser = None

    # reset the step timer dictionary
    ctx.step_timers = {}

    if config.CONFIG["CUCU_RESULTS_DIR"] is not None:
        ctx.scenario_dir = os.path.join(
            ctx.feature_dir, ellipsize_filename(scenario.name)
        )
        CONFIG["SCENARIO_RESULTS_DIR"] = ctx.scenario_dir
        os.makedirs(ctx.scenario_dir, exist_ok=True)

        ctx.scenario_downloads_dir = os.path.join(
            ctx.scenario_dir, "downloads"
        )
        CONFIG["SCENARIO_DOWNLOADS_DIR"] = ctx.scenario_downloads_dir
        os.makedirs(ctx.scenario_downloads_dir, exist_ok=True)

        ctx.scenario_logs_dir = os.path.join(ctx.scenario_dir, "logs")
        CONFIG["SCENARIO_LOGS_DIR"] = ctx.scenario_logs_dir
        os.makedirs(ctx.scenario_logs_dir, exist_ok=True)

        cucu_debug_filepath = os.path.join(
            ctx.scenario_logs_dir, "cucu.debug.console.log"
        )
        ctx.scenario_debug_log_file = open(
            cucu_debug_filepath, "w", encoding=sys.stdout.encoding
        )

        # redirect stdout, stderr and setup a logger at debug level to fill
        # the scenario cucu.debug.log file which makes it possible to have
        # debug logging for every single scenario run without polluting the
        # console logs at runtime.
        sys.stdout.set_other_stream(ctx.scenario_debug_log_file)
        sys.stderr.set_other_stream(ctx.scenario_debug_log_file)
        logger.init_debug_logger(ctx.scenario_debug_log_file)

    # internal cucu config variables
    CONFIG["SCENARIO_RUN_ID"] = hashlib.sha256(
        str(time.perf_counter()).encode("utf-8")
    ).hexdigest()[:7]

    # run before all scenario hooks
    for hook in CONFIG["__CUCU_BEFORE_SCENARIO_HOOKS"]:
        try:
            hook(ctx)
            logger.debug(f"HOOK {hook.__name__}: passed ✅")
        except Exception as e:
            error_message = (
                f"HOOK-ERROR in {hook.__name__}: {e.__class__.__name__}: {e}\n"
            )
            error_message += traceback.format_exc()
            logger.error(error_message)
            ctx.scenario.mark_skipped()
            # Set 'hook_failed' status to 'True' so that the test gets marked
            # as 'errored', even though no steps ran
            ctx.scenario.hook_failed = True


def run_after_scenario_hook(ctx, scenario, hook):
    try:
        hook(ctx)
        logger.debug(f"HOOK {hook.__name__}: passed ✅")
    except Exception as e:
        # For any after scenario hooks,'hook_failed' status will be 'False'
        # but will attach the error message to scenario.
        error_message = (
            f"HOOK-ERROR in {hook.__name__}: {e.__class__.__name__}: {e}\n"
        )
        error_message += traceback.format_exc()
        logger.error(error_message)


def after_scenario(ctx, scenario):
    for timer_name in ctx.step_timers:
        logger.warn(f'timer "{timer_name}" was never stopped/recorded')

    run_after_scenario_hook(ctx, scenario, download_mht_data)

    # run after all scenario hooks in 'lifo' order.
    for hook in CONFIG["__CUCU_AFTER_SCENARIO_HOOKS"][::-1]:
        run_after_scenario_hook(ctx, scenario, hook)

    # run after this scenario hooks in 'lifo' order.
    for hook in CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"][::-1]:
        run_after_scenario_hook(ctx, scenario, hook)

    CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"] = []

    if CONFIG.true("CUCU_KEEP_BROWSER_ALIVE"):
        logger.debug("keeping browser alive between sessions")
    else:
        if len(ctx.browsers) != 0:
            logger.debug("quitting browser between sessions")

        run_after_scenario_hook(ctx, scenario, download_browser_logs)

    cucu_config_filepath = os.path.join(
        ctx.scenario_logs_dir, "cucu.config.yaml.txt"
    )
    with open(cucu_config_filepath, "w") as config_file:
        config_file.write(CONFIG.to_yaml_without_secrets())


def download_mht_data(ctx):
    if not ctx.browsers:
        logger.debug("No browsers - skipping MHT webpage snapshot")
    elif config.CONFIG["CUCU_BROWSER"].lower() != "chrome":
        logger.debug("Browser not Chrome - skipping MHT webpage snapshot")
    else:
        for index, browser in enumerate(ctx.browsers):
            mht_filename = (
                f"browser{index if len(ctx.browsers) > 1 else ''}_snapshot.mht"
            )
            mht_pathname = os.path.join(
                CONFIG["SCENARIO_LOGS_DIR"],
                mht_filename,
            )
            logger.debug(f"Saving MHT webpage snapshot: {mht_filename}")
            browser.download_mht(mht_pathname)


def download_browser_logs(ctx):
    # close the browser unless someone has set the keep browser alive
    # environment variable which allows tests to reuse the same browser
    # session

    for browser in ctx.browsers:
        # save the browser logs to the current scenarios results directory
        browser_log_filepath = os.path.join(
            ctx.scenario_logs_dir, "browser_console.log.txt"
        )

        os.makedirs(os.path.dirname(browser_log_filepath), exist_ok=True)
        with open(browser_log_filepath, "w") as output:
            for log in browser.get_log():
                output.write(f"{json.dumps(log)}\n")

        browser.quit()

    ctx.browsers = []


def before_step(ctx, step):
    # trims the last 3 digits of the microseconds
    step.start_timestamp = datetime.datetime.now().isoformat()[:-3]

    sys.stdout.captured()
    sys.stderr.captured()

    ctx.current_step = step
    ctx.current_step.has_substeps = False
    ctx.start_time = time.monotonic()

    CONFIG["__STEP_SCREENSHOT_COUNT"] = 0

    # run before all step hooks
    for hook in CONFIG["__CUCU_BEFORE_STEP_HOOKS"]:
        hook(ctx)


def after_step(ctx, step):
    step.stdout = sys.stdout.captured()
    step.stderr = sys.stderr.captured()

    ctx.end_time = time.monotonic()
    ctx.previous_step_duration = ctx.end_time - ctx.start_time

    # when set this means we're running in parallel mode using --workers and
    # we want to see progress reported using simply dots
    if CONFIG["__CUCU_PARENT_STDOUT"]:
        CONFIG["__CUCU_PARENT_STDOUT"].write(".")
        CONFIG["__CUCU_PARENT_STDOUT"].flush()

    # we only take screenshots of steps where there's a browser currently open
    # and this step has no substeps as in the reporting the substeps that
    # may actually do something on the browser take their own screenshots
    if ctx.browser is not None and ctx.current_step.has_substeps is False:
        take_screenshot(ctx, step.name, label=f"After {step.name}")

    # if the step has substeps from using `run_steps` then we already moved
    # the step index in the run_steps method and shouldn't do it here
    if not step.has_substeps:
        ctx.step_index += 1
        CONFIG["__STEP_SCREENSHOT_COUNT"] = 0

    if CONFIG.bool("CUCU_IPDB_ON_FAILURE") and step.status == "failed":
        ctx._runner.stop_capture()
        import ipdb

        ipdb.post_mortem(step.exc_traceback)

    CONFIG["__CUCU_BEFORE_THIS_SCENARIO_HOOKS"] = []

    # run after all step hooks
    for hook in CONFIG["__CUCU_AFTER_STEP_HOOKS"]:
        hook(ctx)

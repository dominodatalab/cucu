import datetime
import json
import os
import sys
import time
import traceback
from functools import partial
from pathlib import Path

import yaml

from cucu import config, init_scenario_hook_variables, logger
from cucu.config import CONFIG
from cucu.db import (
    create_database_file,
    finish_cucu_run_record,
    finish_feature_record,
    finish_scenario_record,
    finish_step_record,
    finish_worker_record,
    record_cucu_run,
    record_feature,
    record_scenario,
    start_step_record,
)
from cucu.page_checks import init_page_checks
from cucu.utils import (
    TeeStream,
    ellipsize_filename,
    generate_short_id,
    take_screenshot,
)

CONFIG.define(
    "SCENARIO_RESULTS_DIR",
    "the results directory for the currently executing scenario",
    default=None,
)
CONFIG.define(
    "SCENARIO_DOWNLOADS_DIR",
    "the browser downloads directory for the currently executing scenario",
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
    ctx.check_browser_initialized = partial(check_browser_initialized, ctx)
    ctx.worker_custom_data = {}

    if CONFIG["WORKER_RUN_ID"] != CONFIG["WORKER_PARENT_ID"]:
        logger.debug(
            "Create a new worker db since this isn't the parent process"
        )
        # use seed unique enough for multiple cucu_runs to be combined but predictable within the same run
        worker_id_seed = f"{CONFIG['WORKER_PARENT_ID']}_{os.getpid()}"
        CONFIG["WORKER_RUN_ID"] = generate_short_id(worker_id_seed)

        results_path = Path(CONFIG["CUCU_RESULTS_DIR"])
        worker_run_id = CONFIG["WORKER_RUN_ID"]
        cucu_run_id = CONFIG["CUCU_RUN_ID"]
        CONFIG["RUN_DB_PATH"] = run_db_path = (
            results_path / f"run_{cucu_run_id}_{worker_run_id}.db"
        )
        if not run_db_path.exists():
            logger.debug(
                f"Creating new run database file: {run_db_path} for {worker_id_seed}"
            )
            create_database_file(run_db_path)
            record_cucu_run()

    CONFIG.snapshot("before_all")

    for hook in CONFIG["__CUCU_BEFORE_ALL_HOOKS"]:
        hook(ctx)


def after_all(ctx):
    # run the after all hooks
    for hook in CONFIG["__CUCU_AFTER_ALL_HOOKS"]:
        hook(ctx)

    finish_worker_record(ctx.worker_custom_data)
    finish_cucu_run_record()
    CONFIG.restore(with_pop=True)


def before_feature(ctx, feature):
    feature_run_id_seed = f"{CONFIG['WORKER_RUN_ID']}_{time.perf_counter()}"
    feature.feature_run_id = generate_short_id(feature_run_id_seed)
    feature.custom_data = {}
    record_feature(feature)

    if config.CONFIG["CUCU_RESULTS_DIR"] is not None:
        results_dir = Path(config.CONFIG["CUCU_RESULTS_DIR"])
        ctx.feature_dir = results_dir / ellipsize_filename(feature.name)


def after_feature(ctx, feature):
    finish_feature_record(feature)


def before_scenario(ctx, scenario):
    # we want every scenario to start with the exact same reinitialized config
    # values and not really bleed values between scenario runs
    CONFIG.restore()

    # we should load any cucurc.yml files in the path to the feature file
    # we are about to run so that the config values set for this feature are
    # correctly loaded.
    CONFIG.load_cucurc_files(ctx.feature.filename)

    init_scenario_hook_variables()

    scenario.custom_data = {}
    ctx.scenario = scenario
    ctx.step_index = 0
    ctx.scenario_index = ctx.feature.scenarios.index(scenario) + 1
    ctx.browsers = []
    ctx.browser = None
    ctx.section_step_stack = []

    # reset the step timer dictionary
    ctx.step_timers = {}
    scenario.start_at = datetime.datetime.now().isoformat()[:-3]

    if config.CONFIG["CUCU_RESULTS_DIR"] is not None:
        ctx.scenario_dir = ctx.feature_dir / ellipsize_filename(scenario.name)
        CONFIG["SCENARIO_RESULTS_DIR"] = ctx.scenario_dir
        ctx.scenario_dir.mkdir(parents=True, exist_ok=True)

        ctx.scenario_downloads_dir = ctx.scenario_dir / "downloads"
        CONFIG["SCENARIO_DOWNLOADS_DIR"] = ctx.scenario_downloads_dir
        ctx.scenario_downloads_dir.mkdir(parents=True, exist_ok=True)

        ctx.scenario_logs_dir = ctx.scenario_dir / "logs"
        CONFIG["SCENARIO_LOGS_DIR"] = ctx.scenario_logs_dir
        ctx.scenario_logs_dir.mkdir(parents=True, exist_ok=True)

        cucu_debug_log_path = ctx.scenario_logs_dir / "cucu.debug.console.log"
        ctx.scenario_debug_log_file = open(
            cucu_debug_log_path, "w", encoding=sys.stdout.encoding
        )
        ctx.scenario_debug_log_tee = TeeStream(ctx.scenario_debug_log_file)

        # redirect stdout, stderr and setup a logger at debug level to fill
        # the scenario cucu.debug.log file which makes it possible to have
        # debug logging for every single scenario run without polluting the
        # console logs at runtime.
        sys.stdout.set_other_stream(ctx.scenario_debug_log_tee)
        sys.stderr.set_other_stream(ctx.scenario_debug_log_tee)
        logger.init_debug_logger(ctx.scenario_debug_log_tee)

        # capture browser logs using TeeStream since each call clears the log
        ctx.browser_log_file = open(
            ctx.scenario_logs_dir / "browser_console.log.txt",
            "w",
            encoding="utf-8",
        )
        ctx.browser_log_tee = TeeStream(ctx.browser_log_file)

    scenario_run_id_seed = (
        f"{ctx.feature.feature_run_id}_{time.perf_counter()}"
    )
    CONFIG["SCENARIO_RUN_ID"] = scenario.scenario_run_id = generate_short_id(
        scenario_run_id_seed
    )
    record_scenario(ctx)

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
        logger.warning(f'timer "{timer_name}" was never stopped/recorded')

    browser_info = {"has_browser": False}

    if len(ctx.browsers) != 0:
        try:
            tab_info = ctx.browser.get_tab_info()
            all_tabs = ctx.browser.get_all_tabs_info()
            browser_info = {
                "has_browser": True,
                "current_tab_index": tab_info["index"],
                "all_tabs": all_tabs,
                "browser_type": ctx.browser.driver.name,
            }
        except Exception as e:
            logger.error(f"Error getting browser info: {e}")

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
    elif len(ctx.browsers) != 0:
        logger.debug("quitting browser between sessions")
        run_after_scenario_hook(ctx, scenario, cleanup_browsers)

    scenario.browser_info = browser_info

    cucu_config_path = ctx.scenario_logs_dir / "cucu.config.yaml.txt"
    with open(cucu_config_path, "w") as config_file:
        config_file.write(CONFIG.to_yaml_without_secrets())

    scenario.cucu_config_json = yaml.safe_load(
        CONFIG.to_yaml_without_secrets()
    )

    scenario.end_at = datetime.datetime.now().isoformat()[:-3]
    finish_scenario_record(scenario)


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
            mht_pathname = CONFIG["SCENARIO_LOGS_DIR"] / mht_filename
            logger.debug(f"Saving MHT webpage snapshot: {mht_filename}")
            browser.download_mht(mht_pathname)


def cleanup_browsers(ctx):
    # close the browser unless someone has set the keep browser alive
    # environment variable which allows tests to reuse the same browser
    # session

    for browser in ctx.browsers:
        browser.quit()

    ctx.browser_log_file.close()

    ctx.browsers = []


def before_step(ctx, step):
    step_run_id_seed = f"{ctx.scenario.scenario_run_id}_{ctx.step_index}_{time.perf_counter()}"
    step.step_run_id = generate_short_id(
        step_run_id_seed, length=10
    )  # up to 10 characters to give two orders of magnitude less chance of collision
    step.start_at = datetime.datetime.now().isoformat()[:-3]

    sys.stdout.captured()
    sys.stderr.captured()

    # Reset the debug log buffer for this step
    if hasattr(ctx, "scenario_debug_log_tee"):
        ctx.scenario_debug_log_tee.clear()

    ctx.current_step = step
    ctx.current_step.has_substeps = False
    ctx.section_level = None
    step.seq = ctx.step_index + 1
    step.parent_seq = (
        ctx.section_step_stack[-1].seq if ctx.section_step_stack else 0
    )

    CONFIG["__STEP_SCREENSHOT_COUNT"] = 0

    start_step_record(ctx, step)

    # run before all step hooks
    for hook in CONFIG["__CUCU_BEFORE_STEP_HOOKS"]:
        hook(ctx)


def after_step(ctx, step):
    step.stdout = sys.stdout.captured()
    step.stderr = sys.stderr.captured()

    # Capture debug output from the TeeStream for this step
    if hasattr(ctx, "scenario_debug_log_tee"):
        step.debug_output = ctx.scenario_debug_log_tee.getvalue()
    else:
        step.debug_output = ""

    step.end_at = datetime.datetime.now().isoformat()[:-3]

    # calculate duration from ISO timestamps
    start_at = datetime.datetime.fromisoformat(step.start_at)
    end_at = datetime.datetime.fromisoformat(step.end_at)
    ctx.previous_step_duration = (end_at - start_at).total_seconds()

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

        tab_info = ctx.browser.get_tab_info()
        total_tabs = tab_info["tab_count"]
        current_tab = tab_info["index"] + 1
        title = tab_info["title"]
        url = tab_info["url"]
        log_message = (
            f"\ntab({current_tab} of {total_tabs}): {title}\nurl: {url}\n"
        )
        logger.debug(log_message)

        # Add tab info to step.stdout so it shows up in the HTML report
        step.stdout += (
            f"\ntab({current_tab} of {total_tabs}): {title}\nurl: {url}\n"
        )

    # if the step has substeps from using `run_steps` then we already moved
    # the step index in the run_steps method and shouldn't do it here
    if not step.has_substeps:
        ctx.step_index += 1
        CONFIG["__STEP_SCREENSHOT_COUNT"] = 0

    if CONFIG.bool("CUCU_DEBUG_ON_FAILURE") and step.status == "failed":
        ctx._runner.stop_capture()
        import pdb

        pdb.post_mortem(step.exc_traceback)

    CONFIG["__CUCU_BEFORE_THIS_SCENARIO_HOOKS"] = []

    # run after all step hooks
    for hook in CONFIG["__CUCU_AFTER_STEP_HOOKS"]:
        hook(ctx)

    # Capture browser logs and info for this step
    step.browser_logs = ""

    browser_info = {"has_browser": False}
    if ctx.browser:
        browser_logs = []
        for log in ctx.browser.get_log():
            log_entry = json.dumps(log)
            browser_logs.append(log_entry)
            ctx.browser_log_tee.write(f"{log_entry}\n")
        step.browser_logs = "\n".join(browser_logs)

        tab_info = ctx.browser.get_tab_info()

        browser_info = {
            "tab_count": tab_info["tab_count"],
            "tab_number": tab_info["index"] + 1,
            "tab_title": tab_info["title"],
            "tab_url": tab_info["url"],
            "browser_type": ctx.browser.driver.name,
        }

    step.browser_info = browser_info

    finish_step_record(step, ctx.previous_step_duration)

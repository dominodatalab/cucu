import contextlib
import json
import os
import socket
import sys
from datetime import datetime
from pathlib import Path

from cucu import (
    behave_tweaks,
    init_global_hook_variables,
    register_before_retry_hook,
)
from cucu.browser import selenium
from cucu.config import CONFIG
from cucu.db import create_run_database
from cucu.page_checks import init_page_checks
from cucu.utils import generate_short_id


def get_feature_name(file_path):
    text = Path(file_path).read_text(encoding="utf8")
    lines = text.split("\n")
    for line in lines:
        if "Feature:" in line:
            feature_name = line.replace("Feature:", "").strip()
            return feature_name


def behave_init(filepath="features"):
    """
    behave internal init method used to load the various parts of set of
    feature files and supporting code without executing any of it.

    parameters:
        filepath(string): the file system path of the features directory to load
    """
    behave_tweaks.behave_main(
        ["--dry-run", "--format=null", "--no-summary", filepath]
    )


def behave(
    filepath,
    color_output,
    dry_run,
    env,
    fail_fast,
    headless,
    name,
    debug_on_failure,
    junit,
    results,
    secrets,
    show_skips,
    tags,
    verbose,
    redirect_output=False,
    skip_init_global_hook_variables=False,
):
    # load all them configs
    CONFIG.load_cucurc_files(filepath)

    if CONFIG["CUCU_SELENIUM_REMOTE_URL"] is None:
        selenium.init()

    # general socket timeout instead of letting the framework ever get stuck on a
    # socket connect/read call
    timeout = float(CONFIG["CUCU_SOCKET_DEFAULT_TIMEOUT_S"])
    socket.setdefaulttimeout(timeout)

    if not skip_init_global_hook_variables:
        init_global_hook_variables()

    init_page_checks()

    os.environ["CUCU_COLOR_OUTPUT"] = str(color_output).lower()

    if headless:
        os.environ["CUCU_BROWSER_HEADLESS"] = "True"

    for variable in list(env):
        key, value = variable.split("=")
        os.environ[key] = value

    if debug_on_failure:
        os.environ["CUCU_DEBUG_ON_FAILURE"] = "true"

    os.environ["CUCU_RESULTS_DIR"] = results
    os.environ["CUCU_JUNIT_DIR"] = junit

    if secrets:
        os.environ["CUCU_SECRETS"] = secrets

    args = [
        # don't run disabled tests
        "--tags",
        "~@disabled",
        # always print the skipped steps and scenarios
        "--show-skipped",
    ]

    if verbose:
        args.append("--verbose")

    run_json_filename = "run.json"
    if redirect_output:
        feature_name = get_feature_name(filepath)
        run_json_filename = f"{feature_name}-run.json"

    if dry_run:
        args += [
            "--dry-run",
            # console formater
            "--format=cucu.formatter.cucu:CucuFormatter",
        ]

    else:
        args += [
            "--no-capture",
            "--no-capture-stderr",
            "--no-logcapture",
            # generate a JSON file containing the exact details of the whole run
            "--format=cucu.formatter.json:CucuJSONFormatter",
            f"--outfile={Path(results) / run_json_filename}",
            # console formatter
            "--format=cucu.formatter.cucu:CucuFormatter",
            f"--logging-level={os.environ['CUCU_LOGGING_LEVEL'].upper()}",
            # disable behave's junit output in favor of our own formatter
            "--no-junit",
            "--format=cucu.formatter.junit:CucuJUnitFormatter",
        ]

    for tag in tags:
        args.append("--tags")
        args.append(tag)

    if name is not None:
        args += ["--name", name]

    if fail_fast:
        args.append("--stop")

    if not show_skips:
        args.append("--no-skipped")

    args.append(filepath)

    result = 0
    try:
        if redirect_output:
            feature_name = get_feature_name(filepath)
            log_filename = f"{feature_name}.log"
            log_filepath = Path(results) / log_filename

            CONFIG["__CUCU_PARENT_STDOUT"] = sys.stdout

            def retry_progress(ctx):
                CONFIG["__CUCU_PARENT_STDOUT"].write(".")
                CONFIG["__CUCU_PARENT_STDOUT"].flush()

            # this allows steps that are stuck in a retry to loop to still
            # provide progress feedback on screen
            register_before_retry_hook(retry_progress)

            with log_filepath.open("w", encoding="utf8") as output:
                with contextlib.redirect_stderr(output):
                    with contextlib.redirect_stdout(output):
                        # intercept the stdout/stderr so we can do things such
                        # as hiding secrets in logs
                        behave_tweaks.init_outputs(sys.stdout, sys.stderr)
                        result = behave_tweaks.behave_main(args)
        else:
            # intercept the stdout/stderr so we can do things such
            # as hiding secrets in logs
            behave_tweaks.init_outputs(sys.stdout, sys.stderr)
            result = behave_tweaks.behave_main(args)
    except:
        result = -1
        raise

    return result


def create_run(results, filepath):
    results_path = Path(results)
    run_json_filepath = results_path / "run.json"

    if run_json_filepath.exists():
        return

    CONFIG["CUCU_RUN_ID"] = cucu_run_id = generate_short_id()

    env_values = (
        dict(os.environ)
        if CONFIG["CUCU_RECORD_ENV_VARS"]
        else "To enable use the --record-env-vars flag"
    )

    run_details = {
        "cucu_run_id": cucu_run_id,
        "full_arguments": sys.argv,
        "env": env_values,
        "date": datetime.now().isoformat(),
    }

    run_json_filepath.write_text(
        json.dumps(run_details, indent=2, sort_keys=True), encoding="utf8"
    )

    db_filepath = create_run_database(results)
    CONFIG["RUN_DB_FILEPATH"] = db_filepath

import contextlib
import json
import os
import sys

from cucu import behave_tweaks
from cucu import init_global_hook_variables
from behave.__main__ import main as behave_main
from datetime import datetime


def behave_init(filepath="features"):
    """
    behave internal init method used to load the various parts of set of
    feature files and supporting code without executing any of it.

    parameters:
        filepath(string): the file system path of the features directory to load
    """
    behave_main(["--dry-run", "--format=null", "--no-summary", filepath])


def behave(
    filepath,
    color_output,
    dry_run,
    env,
    fail_fast,
    headless,
    name,
    ipdb_on_failure,
    junit,
    results,
    secrets,
    tags,
    verbose,
    log_start_n_stop=False,
    redirect_output=False,
):
    init_global_hook_variables()

    if not dry_run:
        write_run_details(results, filepath)

    if color_output:
        os.environ["CUCU_COLOR_OUTPUT"] = str(color_output).lower()

    if headless:
        os.environ["CUCU_BROWSER_HEADLESS"] = "True"

    for variable in list(env):
        key, value = variable.split("=")
        os.environ[key] = value

    if ipdb_on_failure:
        os.environ["CUCU_IPDB_ON_FAILURE"] = "true"

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
        feature_filename = os.path.basename(filepath).replace(
            ".feature", "-run"
        )
        run_json_filename = f"{feature_filename}.json"

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
            f"--outfile={results}/{run_json_filename}",
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

    args.append(filepath)

    result = 0
    try:
        if log_start_n_stop:
            print(f"{filepath} is running")

        if redirect_output:
            log_filename = os.path.basename(filepath)
            log_filename = log_filename.replace(".feature", ".log")
            log_filepath = os.path.join(results, log_filename)
            with open(log_filepath, "w", encoding="utf8") as output:
                with contextlib.redirect_stderr(output):
                    with contextlib.redirect_stdout(output):
                        # intercept the stdout/stderr so we can do things such
                        # as hiding secrets in logs
                        behave_tweaks.init_outputs(sys.stdout, sys.stderr)
                        result = behave_main(args)
        else:
            # intercept the stdout/stderr so we can do things such
            # as hiding secrets in logs
            behave_tweaks.init_outputs(sys.stdout, sys.stderr)
            result = behave_main(args)
    except:
        result = -1
        raise

    finally:
        if log_start_n_stop:
            if result != 0:
                print(f"{filepath} has failed")
            else:
                print(f"{filepath} has passed")

    return result


def write_run_details(results, filepath):
    """
    writes a JSON file with run details to the results directory which can be
    used to figure out any runtime details that would otherwise be lost and
    difficult to figure out.
    """
    run_details_filepath = os.path.join(results, "run_details.json")

    if os.path.exists(run_details_filepath):
        return

    run_details = {
        "filepath": filepath,
        "full_arguments": sys.argv,
        "env": dict(os.environ),
        "date": datetime.now().isoformat(),
    }

    with open(run_details_filepath, "w", encoding="utf8") as output:
        output.write(json.dumps(run_details, indent=2, sort_keys=True))

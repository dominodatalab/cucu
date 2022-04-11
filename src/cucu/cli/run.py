import contextlib
import os

from behave.__main__ import main as behave_main
from cucu.config import CONFIG


def behave(
    filepath,
    browser,
    color_output,
    dry_run,
    env,
    fail_fast,
    headless,
    name,
    ipdb_on_failure,
    results,
    secrets,
    tags,
    selenium_remote_url,
    log_start_n_stop=False,
    redirect_output=False,
):
    if color_output:
        CONFIG["CUCU_COLOR_OUTPUT"] = str(color_output).lower()

    if headless:
        CONFIG["CUCU_BROWSER_HEADLESS"] = "True"

    for variable in list(env):
        key, value = variable.split("=")
        CONFIG[key] = value

    CONFIG["CUCU_BROWSER"] = browser

    if ipdb_on_failure:
        CONFIG["CUCU_IPDB_ON_FAILURE"] = "true"

    CONFIG["CUCU_RESULTS_DIR"] = results

    if secrets:
        CONFIG["CUCU_SECRETS"] = secrets

    if selenium_remote_url is not None:
        CONFIG["CUCU_SELENIUM_REMOTE_URL"] = selenium_remote_url

    # only install chromedriver if we're not running rmeotely
    if CONFIG["CUCU_SELENIUM_REMOTE_URL"] is None:
        selenium.init()

    args = [
        # don't run disabled tests
        "--tags",
        "~@disabled",
        # always print the skipped steps and scenarios
        "--show-skipped",
    ]

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
            # JUnit xml file generated per feature file executed
            "--junit",
            f"--junit-directory={results}",
            # generate a JSON file containing the exact details of the whole run
            "--format=cucu.formatter.json:CucuJSONFormatter",
            f"--outfile={results}/{run_json_filename}",
            # console formatter
            "--format=cucu.formatter.cucu:CucuFormatter",
            f"--logging-level={CONFIG['CUCU_LOGGING_LEVEL'].upper()}",
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
                        result = behave_main(args)
        else:
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

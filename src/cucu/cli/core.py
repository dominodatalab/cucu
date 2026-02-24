# -*- coding: utf-8 -*-
import os
import shutil
import signal
import sqlite3
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from importlib.metadata import version
from pathlib import Path
from threading import Timer

import click
import coverage
import psutil
from click import ClickException
from mpire import WorkerPool
from tabulate import tabulate

from cucu import (
    fuzzy,
    init_global_hook_variables,
    language_server,
    logger,
    register_after_all_hook,
    reporter,
)
from cucu.cli import thread_dumper
from cucu.cli.run import behave, behave_init, create_run
from cucu.cli.steps import print_human_readable_steps, print_json_steps
from cucu.config import CONFIG
from cucu.db import (
    consolidate_database_files,
    finish_worker_record,
)
from cucu.lint import linter
from cucu.utils import generate_short_id

# set env var BEHAVE_STRIP_STEPS_WITH_TRAILING_COLON=yes before importing behave
os.environ["BEHAVE_STRIP_STEPS_WITH_TRAILING_COLON"] = "yes"

# will start coverage tracking once COVERAGE_PROCESS_START is set
coverage.process_startup()


@click.group()
@click.version_option(version("cucu"), message="%(version)s")
def main():
    """
    cucu e2e testing framework
    """
    pass


@main.command()
@click.argument(
    "filepath", default="features", type=click.Path(path_type=Path)
)
@click.option(
    "-b",
    "--browser",
    default=os.environ.get("CUCU_BROWSER") or "chrome",
    help="browser name to use default: chrome",
)
@click.option(
    "-c",
    "--color-output/--no-color-output",
    default=True,
    help="produce output with colors or not",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=False,
    help="invokes output formatters without running the steps",
)
@click.option(
    "-e",
    "--env",
    default=[],
    multiple=True,
    help="set environment variable which can be referenced with",
)
@click.option(
    "-g",
    "--generate-report/--no-generate-report",
    default=False,
    help="automatically generate a report at the end of the test run",
)
@click.option(
    "-x",
    "--fail-fast/--no-fail-fast",
    default=False,
    help="stop running tests on the first failure",
)
@click.option(
    "-h",
    "--headless/--no-headless",
    default=True,
    help="controls if the browser is run in headless mode",
)
@click.option("-n", "--name", help="used to specify the exact scenario to run")
@click.option(
    "-d",
    "--debug-on-failure/--no-debug-on-failure",
    default=False,
    help="on failure drop into the debug shell",
)
@click.option(
    "-j",
    "--junit",
    default=None,
    help="specify the output directory for JUnit XML files, default is "
    "the same location as --results",
    type=click.Path(path_type=Path),
)
@click.option(
    "--junit-with-stacktrace",
    is_flag=True,
    default=False,
    help="when set to true the JUnit XML output will contain the stacktrace",
)
@click.option(
    "-l",
    "--logging-level",
    default="INFO",
    help="set logging level to one of debug, warn or info (default)",
)
@click.option(
    "--show-skips",
    default=False,
    is_flag=True,
    help="when set skips are shown",
)
@click.option(
    "--periodic-thread-dumper",
    default=None,
    help="sets the interval in minutes of when to run the periodic thread dumper",
)
@click.option(
    "-p",
    "--preserve-results/--no-preserve-results",
    default=False,
    help="when set we will not remove any existing results directory",
)
@click.option(
    "--record-env-vars",
    default=False,
    is_flag=True,
    help="when set will record shell environment variables to debug file: run_details.json",
)
@click.option(
    "--report",
    default="report",
    help="the location to put the test report when --generate-report is used",
    type=click.Path(path_type=Path),
)
@click.option(
    "-r",
    "--results",
    default="results",
    help="the results directory used by cucu",
    type=click.Path(path_type=Path),
)
@click.option(
    "--runtime-timeout",
    default=None,
    type=int,
    help="the runtime timeout in seconds after which the current run will terminate any running tests and exit",
)
@click.option(
    "--feature-timeout",
    default=1800,
    help="When run tests in parallel, the maximum amount of time (seconds) a feature can run",
)
@click.option(
    "--secrets",
    default=None,
    help="coma separated list of variable names that we should hide"
    " their value all of the output produced by cucu",
)
@click.option(
    "-t",
    "--tags",
    default=[],
    multiple=True,
    help="Only execute features or scenarios with tags matching "
    "expression provided. example: --tags @dev, --tags ~@dev",
)
@click.option(
    "-w",
    "--workers",
    default=None,
    help="Specifies the number of workers to use to run tests in parallel",
    type=int,
)
@click.option(
    "--verbose/--no-verbose",
    default=False,
    help="runs with verbose logging and shows additional stacktrace",
)
@click.option(
    "-s",
    "--selenium-remote-url",
    default=None,
    help="the HTTP url for a selenium hub setup to run the browser tests on",
)
def run(
    filepath,
    browser,
    color_output,
    dry_run,
    env,
    generate_report,
    fail_fast,
    headless,
    name,
    debug_on_failure,
    junit,
    junit_with_stacktrace,
    logging_level,
    periodic_thread_dumper,
    preserve_results,
    record_env_vars,
    report,
    results,
    runtime_timeout,
    feature_timeout,
    secrets,
    show_skips,
    tags,
    selenium_remote_url,
    workers,
    verbose,
):
    """
    run a set of feature files

    Note: All the os.environ variables are set to be available in the child processes
    """
    init_global_hook_variables()
    dumper = None

    if os.environ.get("CUCU") == "true":
        # when cucu is already running it means that we're running inside
        # another cucu process and therefore we should make sure the results
        # directory isn't the default one and throw an exception otherwise
        if results == Path("results"):
            raise Exception(
                "running within cucu but --results was not used, "
                "this would lead to some very difficult to debug "
                "failures as this process would clobber the "
                "parent results directory"
            )

    # set for testing cucu itself but basically allows you to know when cucu
    # is running itself as part of internal testing
    os.environ["CUCU"] = "true"

    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    if not preserve_results:
        if results.exists():
            shutil.rmtree(results)

    results.mkdir(parents=True, exist_ok=True)

    if selenium_remote_url is not None:
        os.environ["CUCU_SELENIUM_REMOTE_URL"] = selenium_remote_url

    if periodic_thread_dumper is not None:
        interval_min = float(periodic_thread_dumper)
        dumper = thread_dumper.start(interval_min)

    # need to set this before initializing any browsers below
    os.environ["CUCU_BROWSER"] = browser.lower()

    if junit is None:
        junit = results

    if show_skips:
        os.environ["CUCU_SHOW_SKIPS"] = "true"

    if junit_with_stacktrace:
        os.environ["CUCU_JUNIT_WITH_STACKTRACE"] = "true"

    if record_env_vars:
        os.environ["CUCU_RECORD_ENV_VARS"] = "true"

    cucu_run_id_seed = f"{time.perf_counter()}_{os.getpid()}"
    os.environ["CUCU_RUN_ID"] = CONFIG["CUCU_RUN_ID"] = generate_short_id(
        cucu_run_id_seed
    )
    worker_id_seed = f"{CONFIG['CUCU_RUN_ID']}_{os.getpid()}"
    os.environ["WORKER_PARENT_ID"] = CONFIG["WORKER_RUN_ID"] = (
        generate_short_id(worker_id_seed)
    )

    os.environ["CUCU_FILEPATH"] = CONFIG["CUCU_FILEPATH"] = str(filepath)

    create_run(results, filepath)

    try:
        if workers is None:  # or workers == 1:
            logger.debug(
                f"Starting cucu_run {CONFIG['CUCU_RUN_ID']} with single worker"
            )
            if runtime_timeout:
                logger.debug("setting up runtime timeout timer")

                def runtime_exit():
                    logger.error("runtime timeout reached, aborting run")
                    CONFIG["__CUCU_CTX"]._runner.aborted = True
                    os.kill(os.getpid(), signal.SIGINT)

                timer = Timer(runtime_timeout, runtime_exit)
                timer.start()

                def cancel_timer(_):
                    logger.debug("cancelled runtime timeout timer")
                    timer.cancel()

                register_after_all_hook(cancel_timer)

            exit_code = behave(
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
                skip_init_global_hook_variables=True,
            )

            if exit_code != 0:
                raise RuntimeError("test run failed, see above for details")

        else:
            logger.debug(
                f"Starting cucu_run {CONFIG['CUCU_RUN_ID']} with multiple workers: {workers}"
            )
            if filepath.is_dir():
                feature_filepaths = list(filepath.rglob("*.feature"))
            else:
                feature_filepaths = [filepath]

            if sys.platform == "darwin":
                logger.info(
                    "MAC OS detected, using 'forkserver' start method since 'fork' is unstable"
                )
                start_method = "forkserver"
            else:
                start_method = "fork"

            with WorkerPool(
                n_jobs=int(workers), start_method=start_method
            ) as pool:
                # Each feature file is applied to the pool as an async task.
                # It then polls the async result of each task. It the result
                # is ready, it removes the result from the list of results that
                # need to be checked again until all the results are checked.
                # If the timer is triggered, it stops the while loop and
                # logs all the unfinished features.
                # The pool is terminated automatically when it exits the
                # context.
                timer = None
                timeout_reached = False
                if runtime_timeout:
                    logger.debug("setting up runtime timeout timer")

                    def runtime_exit():
                        nonlocal timeout_reached
                        logger.error("runtime timeout reached, aborting run")
                        timeout_reached = True

                    timer = Timer(runtime_timeout, runtime_exit)
                    timer.start()

                def kill_workers():
                    for worker in pool._workers:
                        try:
                            worker_proc = psutil.Process(worker.pid)
                            for child in worker_proc.children():
                                child.kill()

                            worker_proc.kill()
                        except psutil.NoSuchProcess:
                            pass

                def handle_kill_signal(signum, frame):
                    signal.signal(
                        signum, signal.SIG_IGN
                    )  # ignore additional signals
                    logger.warning(
                        f"received signal {signum}, sending kill signal to workers"
                    )
                    kill_workers()
                    if timer:
                        timer.cancel()

                    os.kill(os.getpid(), signal.SIGINT)

                # This is for local runs where you want to cancel the run with a ctrl+c or SIGTERM
                signal.signal(signal.SIGINT, handle_kill_signal)
                signal.signal(signal.SIGTERM, handle_kill_signal)

                async_results = {}
                for feature_filepath in feature_filepaths:
                    async_results[feature_filepath] = pool.apply_async(
                        behave,
                        [
                            feature_filepath,
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
                        ],
                        {
                            "redirect_output": True,
                        },
                        task_timeout=float(feature_timeout),
                    )
                    logger.info(f"scheduled feature file {feature_filepath}")

                # poll while we have running tasks until the overall time limit
                task_failed = {}
                while not timeout_reached:
                    remaining = {}
                    for feature, result in async_results.items():
                        if timeout_reached:
                            break

                        if result.ready():
                            try:
                                # wait 0.1s max for interprocess communication
                                exit_code = result.get(0.1)
                                if exit_code != 0:
                                    task_failed[feature] = result
                            except TimeoutError as err:
                                if f"timeout={feature_timeout}" in str(err):
                                    print(f"{err}")
                                    task_failed[feature] = result
                                # ignore timeout errors from interprocess communication slowness
                            except Exception:
                                logger.exception(
                                    f"an exception is raised during feature {feature}"
                                )
                                task_failed[feature] = result
                        else:
                            remaining[feature] = result

                    async_results = remaining

                    if len(remaining) == 0:
                        if timer:
                            # we're done so cancel any outstanding overall time limit
                            timer.cancel()
                        break

                    time.sleep(1)

                if timeout_reached:
                    logger.warning(
                        "Timeout reached, send kill signal to workers"
                    )
                    kill_workers()

                task_failed.update(async_results)

                if task_failed:
                    failing_features = [str(x) for x in task_failed.keys()]
                    logger.error(
                        f"Failing Features:\n{'\n'.join(failing_features)}"
                    )
                    raise RuntimeError(
                        "there are failures, see above for details"
                    )
    finally:
        if dumper is not None:
            dumper.stop()

        if results.exists():
            finish_worker_record(worker_run_id=CONFIG.get("WORKER_PARENT_ID"))
            consolidate_database_files(results)

        if generate_report:
            _generate_report(
                results_dir=results,
                report_folder=report,
                junit_folder=junit,
            )


def _generate_report(
    results_dir: Path,
    report_folder: Path,
    junit_folder: Path | None = None,
    combine: bool = False,
):
    if report_folder.exists():
        shutil.rmtree(report_folder)

    report_folder.mkdir(parents=True, exist_ok=True)

    if results_dir.exists():
        consolidate_database_files(results_dir, combine)

    report_location = reporter.generate(results_dir, report_folder)
    print(f"HTML test report at {report_location}")

    if junit_folder:
        for junit_file in junit_folder.rglob("*.xml"):
            try:           
                junit = ET.parse(junit_file)
            except ET.ParseError:
                logger.error(f"failed to parse junit file {junit_file}, skipping")
                continue

            test_suite = junit.getroot()
            ts_folder = test_suite.get("foldername")
            for test_case in test_suite.iter("testcase"):
                report_path = os.path.join(
                    report_folder,
                    ts_folder,
                    test_case.get("foldername"),
                    "index.html",
                )
                test_case.set("report_path", report_path)
            junit.write(junit_file, encoding="utf-8", xml_declaration=False)


@main.command()
@click.argument(
    "results_dir", default="results", type=click.Path(path_type=Path)
)
@click.option(
    "-l",
    "--logging-level",
    default="INFO",
    help="set logging level to one of debug, warn or info (default)",
)
@click.option(
    "--show-skips",
    default=False,
    is_flag=True,
    help="when set skips are shown",
)
@click.option(
    "-o",
    "--output",
    default="report",
    type=click.Path(path_type=Path),
)
@click.option(
    "-j",
    "--junit",
    default=None,
    help="specify the output directory for JUnit XML files, default is "
    "the same location as --results",
    type=click.Path(path_type=Path),
)
@click.option(
    "--combine",
    default=False,
    is_flag=True,
    help="combine multiple cucu_runs into a single report",
)
def report(
    results_dir: Path,
    logging_level,
    show_skips,
    output: Path,
    junit: Path,
    combine: bool,
):
    """
    generate a test report from a results directory
    """
    init_global_hook_variables()

    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    if show_skips:
        os.environ["CUCU_SHOW_SKIPS"] = "true"

    run_db_path = results_dir / "run.db"
    if run_db_path.exists():
        # query cucu_run to get the original filepath used during the run
        with sqlite3.connect(run_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT filepath FROM cucu_run ORDER BY start_at DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                filepath = row[0]
                # initialize any underlying custom step code things
                behave_init(filepath)

    _generate_report(
        results_dir=results_dir,
        report_folder=output,
        junit_folder=junit,
        combine=combine,
    )


@main.command()
@click.argument(
    "filepath", default="features", type=click.Path(path_type=Path)
)
@click.option(
    "-f",
    "--format",
    default="human",
    help="output format to use, available: human, json."
    "default: human. PRO TIP: `brew install fzf` and then "
    "`cucu steps | fzf` and easily find the step you need.",
)
def steps(filepath, format):
    """
    print available cucu steps
    """
    init_global_hook_variables()

    if format == "human":
        print_human_readable_steps(filepath=filepath)

    elif format == "json":
        print_json_steps(filepath=filepath)

    else:
        raise RuntimeError(f'unsupported format "{format}"')


@main.command()
@click.argument("filepath", type=click.Path(path_type=Path), nargs=-1)
@click.option(
    "--fix/--no-fix", default=False, help="fix lint violations, default: False"
)
@click.option(
    "-l",
    "--logging-level",
    default="INFO",
    help="set logging level to one of debug, warn or info (default)",
)
def lint(filepath, fix, logging_level):
    """
    lint feature files
    """
    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    init_global_hook_variables()

    logger.init_logging("INFO")
    filepaths = list(filepath)

    if filepaths == []:
        filepaths = ["features"]

    violations_found = 0
    violations_fixed = 0

    for filepath in filepaths:
        # initialize any underlying custom step code things
        behave_init(filepath)

        all_violations = linter.lint(filepath)

        for violations in all_violations:
            if fix:
                violations = linter.fix(violations)

            if violations:
                for violation in violations:
                    violations_found += 1

                    if violation["type"] == "steps_error":
                        print(violation["message"])
                        print(
                            "failure loading some steps, see above for details"
                        )
                        print("")
                        continue

                    location = violation["location"]
                    _type = violation["type"][0].upper()
                    message = violation["message"]
                    suffix = ""

                    if fix:
                        if violation["fixed"]:
                            suffix = " ✓"
                            violations_fixed += 1
                        else:
                            suffix = " ✗ (must be fixed manually)"

                    filepath = location["filepath"]
                    line_number = location["line"] + 1
                    print(
                        f"{filepath}:{line_number}: {_type} {message}{suffix}"
                    )

    if violations_found != 0:
        if violations_found == violations_fixed:
            print("\nlinting errors found and fixed, see above for details")

        else:
            raise ClickException(
                "linting errors found, but not fixed, see above for details"
            )


@main.command()
@click.option(
    "-l",
    "--logging-level",
    default="INFO",
    help="set logging level to one of debug, warn or info (default)",
)
@click.option(
    "-p",
    "--port",
    default=None,
    help="when the port is set the lsp will run in TCP mode and not STDIO mode",
)
def lsp(logging_level, port):
    """
    start the cucu language server
    """
    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    language_server.start(port=port)


@main.command()
@click.argument(
    "filepath", default="features", type=click.Path(path_type=Path)
)
def vars(filepath):
    """
    print built-in cucu variables
    """
    init_global_hook_variables()

    # loading the steps make it so the code that registers config variables
    # elsewhere get to execute
    behave_init(filepath)

    variables = []
    variables.append(["Name", "Description", "Default"])

    variables.extend(
        [
            [name, definition["description"], definition["default"]]
            for name, definition in CONFIG.defined_variables.items()
        ]
    )

    print(tabulate(variables, tablefmt="fancy_grid"))


@main.command()
@click.argument("repo_dir", default="", type=click.Path(path_type=Path))
@click.option(
    "-l",
    "--logging-level",
    default="INFO",
    help="set logging level to one of debug, warn or info (default)",
)
def init(repo_dir, logging_level):
    """
    initialize cucu in the current directory

    Copies the `init_data` directory to the current directory
    """
    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    init_data_dir = Path(__file__).parent.parent / "init_data"

    logger.debug(f"cucu init: copy example directory from {init_data_dir=}")

    features_dir = repo_dir / "features"
    if features_dir.exists():
        answer = input("Overwrite existing files? [y/N]:")
        if answer.lower() != "y":
            print("Aborted!")
            return

    shutil.copytree(init_data_dir, repo_dir, dirs_exist_ok=True)
    print("You can now start writing your tests")


@main.command()
@click.option(
    "-b",
    "--browser",
    default="chrome",
    help="when specified the browser will be opened with the fuzzy "
    "js library preloaded.",
)
@click.option(
    "-u",
    "--url",
    default="https://www.google.com",
    help="URL to open the browser at for debugging",
)
@click.option(
    "--detach",
    default=False,
    help="when set to detach the browser will continue to run and "
    "the cucu process will exit",
)
@click.option(
    "-l",
    "--logging-level",
    default="INFO",
    help="set logging level to one of debug, warn or info (default)",
)
def debug(browser, url, detach, logging_level):
    """
    debug cucu library
    """
    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    fuzzy_js = fuzzy.load_jquery_lib() + fuzzy.load_fuzzy_lib()
    # XXX: need to make this more generic once we make the underlying
    #      browser framework swappable.
    from cucu.browser.selenium import Selenium

    selenium = Selenium()
    selenium.open(browser, detach=detach)
    selenium.navigate(url)
    selenium.execute(fuzzy_js)

    if not detach:
        while True:
            # detect when there are changes to the cucu javascript library
            # and reload it in the currently running browser.
            time.sleep(5)


@main.command()
@click.option(
    "-l",
    "--logging-level",
    default="INFO",
    help="set logging level to one of debug, warn or info (default)",
)
@click.argument(
    "filepath", default="features", type=click.Path(path_type=Path)
)
def tags(filepath, logging_level):
    """
    print a table of tags and affected scenario counts
    """

    # import here to preserve import to set behave parse BEHAVE_STRIP_STEPS_WITH_TRAILING_COLON correctly
    from behave.model_core import FileLocation
    from behave.runner_util import parse_features

    init_global_hook_variables()
    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    if filepath.is_file():
        feature_files = [filepath]
    else:
        feature_files = list(filepath.rglob("*.feature"))

    if not filepath.exists() or not feature_files:
        raise ClickException("No feature files found.")

    file_locations = [FileLocation(f.absolute()) for f in feature_files]
    features = parse_features(file_locations)
    tag_scenarios = Counter()

    for feature in features:
        for scenario in feature.scenarios:
            affecting_tags = set(feature.tags + scenario.tags)
            tag_scenarios.update(affecting_tags)

    if not tag_scenarios:
        print("No tags found in feature files.")
        return

    table_data = [["Tag", "Scenarios Affected"]] + [
        [tag_name, str(count)]
        for tag_name, count in sorted(
            tag_scenarios.items(), key=lambda x: x[0].lower()
        )
    ]

    print(tabulate(table_data, headers="firstrow", tablefmt="fancy_grid"))


if __name__ == "__main__":
    main()

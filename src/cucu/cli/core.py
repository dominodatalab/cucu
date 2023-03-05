# -*- coding: utf-8 -*-
import click
import coverage
import glob
import json
import multiprocessing
import shutil
import signal
import time
import os

from click import ClickException
from cucu import (
    fuzzy,
    init_global_hook_variables,
    register_after_all_hook,
    reporter,
    language_server,
    logger,
)
from cucu.config import CONFIG
from cucu.cli import thread_dumper
from cucu.cli.run import behave, behave_init, write_run_details
from cucu.cli.steps import print_human_readable_steps, print_json_steps
from cucu.lint import linter
from importlib.metadata import version
from tabulate import tabulate
from threading import Timer


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
@click.argument("filepath")
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
    "-i",
    "--ipdb-on-failure/--no-ipdb-on-failure",
    default=False,
    help="on failure drop into the ipdb debug shell",
)
@click.option(
    "-j",
    "--junit",
    default=None,
    help="specify the output directory for JUnit XML files, default is "
    "the same location as --results",
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
    "--show-status",
    default=False,
    is_flag=True,
    help="when set status output is shown (helpful for CI that wants stdout updates)",
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
    "--report",
    default="report",
    help="the location to put the test report when --generate-report is used",
)
@click.option(
    "--report-only-failures",
    default=False,
    is_flag=True,
    help="when set the HTML test report will only contain the failed test results",
)
@click.option(
    "-r",
    "--results",
    default="results",
    help="the results directory used by cucu",
)
@click.option(
    "--runtime-timeout",
    default=None,
    type=int,
    help="the runtime timeout in seconds after which the current run will terminate any running tests and exit",
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
    ipdb_on_failure,
    junit,
    junit_with_stacktrace,
    logging_level,
    periodic_thread_dumper,
    preserve_results,
    report,
    report_only_failures,
    results,
    runtime_timeout,
    secrets,
    show_skips,
    show_status,
    tags,
    selenium_remote_url,
    workers,
    verbose,
):
    """
    run a set of feature files
    """
    init_global_hook_variables()
    dumper = None

    if os.environ.get("CUCU") == "true":
        # when cucu is already running it means that we're running inside
        # another cucu process and therefore we should make sure the results
        # directory isn't the default one and throw an exception otherwise
        if results == "results":
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

    if not dry_run:
        if not preserve_results:
            if os.path.exists(results):
                shutil.rmtree(results)

        os.makedirs(results, exist_ok=True)

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

    if show_status:
        os.environ["CUCU_SHOW_STATUS"] = "true"

    if junit_with_stacktrace:
        os.environ["CUCU_JUNIT_WITH_STACKTRACE"] = "true"

    if report_only_failures:
        os.environ["CUCU_REPORT_ONLY_FAILURES"] = "true"

    if not dry_run:
        write_run_details(results, filepath)

    try:
        if workers is None or workers == 1:
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
                ipdb_on_failure,
                junit,
                results,
                secrets,
                show_skips,
                tags,
                verbose,
                skip_init_global_hook_variables=True,
            )

            if exit_code != 0:
                raise ClickException("test run failed, see above for details")

        else:
            if os.path.isdir(filepath):
                basepath = os.path.join(filepath, "**/*.feature")
                feature_filepaths = glob.iglob(basepath, recursive=True)

            else:
                feature_filepaths = [filepath]

            with multiprocessing.get_context("spawn").Pool(
                int(workers)
            ) as pool:
                timer = None
                if runtime_timeout:
                    logger.debug("setting up runtime timeout timer")

                    def runtime_exit():
                        logger.error("runtime timeout reached, aborting run")
                        timeout_filepath = os.path.join(
                            results, "runtime-timeout"
                        )
                        open(timeout_filepath, "w").close()

                        for child in multiprocessing.active_children():
                            os.kill(child.pid, signal.SIGINT)
                            os.kill(child.pid, signal.SIGTERM)

                    timer = Timer(runtime_timeout, runtime_exit)
                    timer.start()

                    def cancel_timer(_):
                        logger.debug("cancelled runtime timeout timer")
                        timer.cancel()

                    register_after_all_hook(cancel_timer)

                async_results = []
                for feature_filepath in feature_filepaths:
                    async_results.append(
                        pool.apply_async(
                            behave,
                            [
                                feature_filepath,
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
                                show_skips,
                                tags,
                                verbose,
                            ],
                            {
                                "redirect_output": True,
                            },
                        )
                    )

                workers_failed = False
                for result in async_results:
                    try:
                        exit_code = result.get(runtime_timeout)
                        if exit_code != 0:
                            workers_failed = True
                    except:
                        logger.exception("an exception is raised during test")
                        workers_failed = True

                pool.close()
                pool.join()

                if timer:
                    timer.cancel()

                if workers_failed:
                    raise RuntimeError(
                        "there are failures, see above for details"
                    )
    finally:
        if dumper is not None:
            dumper.stop()

        if generate_report:
            _generate_report(
                results, report, only_failures=report_only_failures
            )


def _generate_report(filepath, output, only_failures: False):
    """
    helper method to handle report generation so it can be used by the `cucu report`
    command also the `cucu run` when told to generate a report.


    parameters:
        filepath(string): the results directory containing the previous test run
        output(string): the directory where we'll generate the report
    """
    if os.path.exists(output):
        shutil.rmtree(output)

    os.makedirs(output)

    report_location = reporter.generate(
        filepath, output, only_failures=only_failures
    )
    print(f"HTML test report at {report_location}")


@main.command()
@click.argument("filepath", default="results")
@click.option(
    "--only-failures",
    default=False,
    is_flag=True,
    help="when set the HTML test report will only contain the failed test results",
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
    "--show-status",
    default=False,
    is_flag=True,
    help="when set status output is shown (helpful for CI that wants stdout updates)",
)
@click.option("-o", "--output", default="report")
def report(
    filepath, only_failures, logging_level, show_skips, show_status, output
):
    """
    generate a test report from a results directory
    """
    init_global_hook_variables()

    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    if show_skips:
        os.environ["CUCU_SHOW_SKIPS"] = "true"

    if show_status:
        os.environ["CUCU_SHOW_STATUS"] = "true"

    run_details_filepath = os.path.join(filepath, "run_details.json")

    if os.path.exists(run_details_filepath):
        # load the run details at the time of execution for the provided results
        # directory
        run_details = {}

        with open(run_details_filepath, encoding="utf8") as _input:
            run_details = json.loads(_input.read())

        # initialize any underlying custom step code things
        behave_init(run_details["filepath"])

    _generate_report(filepath, output, only_failures=only_failures)


@main.command()
@click.argument("filepath", default="features")
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
@click.argument("filepath", nargs=-1)
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
@click.argument("filepath", default="features")
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


if __name__ == "__main__":
    main()

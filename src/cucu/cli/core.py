# -*- coding: utf-8 -*-
import click
import contextlib
import coverage
import glob
import multiprocessing
import shutil
import socket
import time
import os

from click import ClickException
from cucu import fuzzy, reporter, language_server, logger
from cucu.browser import selenium
from cucu.config import CONFIG
from cucu.cli.run import behave
from cucu.cli.steps import print_human_readable_steps, print_json_steps
from cucu.lint import linter
from importlib.metadata import version

# will start coverage tracking once COVERAGE_PROCESS_START is set
coverage.process_startup()

# quick and dirty way to simply handle having a default socket timeout for all
# things within the framework
timeout = float(CONFIG["CUCU_SELENIUM_DEFAULT_TIMEOUT"])
# socket.setdefaulttimeout(timeout)


@click.group()
@click.version_option(version("cucu"), message="%(version)s")
def main():
    """
    main entrypoint
    """
    pass


@main.command()
@click.argument("filepath")
@click.option(
    "-b",
    "--browser",
    default="chrome",
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
@click.option("-h", "--headless/--no-headless", default=True)
@click.option("-n", "--name")
@click.option(
    "-i", "--ipdb-on-failure/--no-ipdb-oo-failure", help="", default=False
)
@click.option(
    "-l",
    "--logging-level",
    default="INFO",
    help="set logging level to one of debug, warn or info (default)",
)
@click.option(
    "-p", "--preserve-results/--no-preserve-results", help="", default=False
)
@click.option("--report", default="report")
@click.option("-r", "--results", default="results")
@click.option(
    "--secrets",
    default=None,
    help="coma separated list of variable names that we should hide"
    " their value all of the output produced by cucu",
)
@click.option(
    "-t",
    "--tags",
    help="Only execute features or scenarios with tags matching "
    "expression provided. example: --tags @dev, --tags ~@dev",
    default=[],
    multiple=True,
)
@click.option(
    "-w",
    "--workers",
    help="Specifies the number of workers to use to run tests in parallel",
    default=None,
)
@click.option(
    "--verbose/--no-verbose",
    help="runs with verbose logging and shows additional stacktrace",
    default=False,
)
@click.option("-s", "--selenium-remote-url", default=None)
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
    logging_level,
    preserve_results,
    report,
    results,
    secrets,
    tags,
    selenium_remote_url,
    workers,
    verbose,
):
    """
    run a set of feature files
    """
    # load all them configs
    CONFIG.load_cucurc_files(filepath)

    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    if not dry_run:
        if not preserve_results:
            if os.path.exists(results):
                shutil.rmtree(results)

        if not os.path.exists(results):
            os.makedirs(results)

    if selenium_remote_url is not None:
        CONFIG["CUCU_SELENIUM_REMOTE_URL"] = selenium_remote_url

    selenium.init()

    try:
        if workers is None or workers == 1:
            exit_code = behave(
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
                verbose,
            )

            if exit_code != 0:
                raise ClickException("test run failed, see above for details")

        else:
            if os.path.isdir(filepath):
                basepath = os.path.join(filepath, "**/*.feature")
                feature_filepaths = glob.iglob(basepath, recursive=True)

            else:
                feature_filepaths = [filepath]

            with multiprocessing.Pool(int(workers)) as pool:
                async_results = []
                for feature_filepath in feature_filepaths:
                    async_results.append(
                        pool.apply_async(
                            behave,
                            [
                                feature_filepath,
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
                                verbose,
                            ],
                            {
                                "redirect_output": True,
                                "log_start_n_stop": True,
                            },
                        )
                    )

                workers_failed = False
                for result in async_results:
                    result.wait()
                    exit_code = result.get()
                    if exit_code != 0:
                        workers_failed = True

                pool.close()
                pool.join()

                if workers_failed:
                    raise RuntimeError(
                        "there are failures, see above for details"
                    )
    finally:
        if generate_report:
            _generate_report(results, report)


def _generate_report(filepath, output):
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

    report_location = reporter.generate(filepath, output)
    print(f"HTML test report at {report_location}")


@main.command()
@click.argument("filepath", default="results")
@click.option("-o", "--output", default="report")
def report(filepath, output):
    """
    create an HTML test report from the results directory provided
    """
    _generate_report(filepath, output)


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
def lint(filepath, fix):
    """
    lint feature files
    """
    filepaths = list(filepath)

    if filepaths == []:
        filepaths = ["features"]

    violations_found = 0
    violations_fixed = 0

    for filepath in filepaths:
        all_violations = linter.lint(filepath)

        for violations in all_violations:
            if fix:
                violations = linter.fix(violations)

            if violations:
                for violation in violations:
                    violations_found += 1
                    location = violation["location"]
                    type = violation["type"][0].upper()
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
                    print(f"{filepath}:{line_number}: {type} {message}{suffix}")

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
def lsp(logging_level):
    """
    start the cucu language server
    """
    os.environ["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())

    language_server.start()


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
def debug(browser, url, detach):
    """
    debug cucu library
    """
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

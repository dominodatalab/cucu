# -*- coding: utf-8 -*-
import click
import coverage
import shutil
import time
import os

from click import ClickException
from cucu import fuzzy, reporter, language_server, logger
from cucu.config import CONFIG
from cucu.cli.steps import print_human_readable_steps, print_json_steps
from cucu.lint import linter
from importlib.metadata import version

# will start coverage tracking once COVERAGE_PROCESS_START is set
coverage.process_startup()


@click.group()
@click.version_option(version("cucu"))
@click.option("--debug/--no-debug", default=False)
@click.option(
    "-l",
    "--logging-level",
    default="INFO",
    help="set logging level to one of debug, warn or info (default)",
)
def main(debug, logging_level):
    """
    main entrypoint
    """
    CONFIG["CUCU_LOGGING_LEVEL"] = logging_level.upper()
    logger.init_logging(logging_level.upper())


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
    "-f",
    "--format",
    default="human",
    help="set output step formatter to human or json, default: human",
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
    "--source/--no-source",
    default=False,
    help="show the source for each step definition in the logs",
)
@click.option(
    "-t",
    "--tags",
    help="Only execute features or scenarios with tags matching "
    "expression provided. example: --tags @dev, --tags ~@dev",
    default=[],
    multiple=True,
)
@click.option("-s", "--selenium-remote-url", default=None)
def run(
    filepath,
    browser,
    color_output,
    dry_run,
    env,
    format,
    generate_report,
    fail_fast,
    headless,
    name,
    ipdb_on_failure,
    preserve_results,
    report,
    results,
    secrets,
    source,
    tags,
    selenium_remote_url,
):
    """
    run a set of feature files
    """
    # load all them configs
    CONFIG.load_cucurc_files(filepath)

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

    if not dry_run:
        if not preserve_results:
            if os.path.exists(results):
                shutil.rmtree(results)
                os.makedirs(results)
        else:
            if not os.path.exists(results):
                os.makedirs(results)

    if selenium_remote_url is not None:
        CONFIG["CUCU_SELENIUM_REMOTE_URL"] = selenium_remote_url

    if format == "human":
        formatter = "cucu.formatter.cucu:CucuFormatter"

    elif format == "json":
        formatter = "cucu.formatter.json:CucuJSONFormatter"

    args = [
        # don't run disabled tests
        "--tags",
        "~@disabled",
        # always print the skipped steps and scenarios
        "--show-skipped",
        filepath,
    ]

    if dry_run:
        args += [
            "--dry-run",
            # console formater
            "--format",
            formatter,
        ]

    else:
        args += [
            # JUNIT xml file generated per feature file executed
            "--junit",
            f"--junit-directory={results}",
            # generate a JSOn file containing the exact details of the whole run
            "--format",
            "cucu.formatter.json:CucuJSONFormatter",
            f"--outfile={results}/run.json",
            # console formater
            "--format",
            formatter,
            "--logging-level",
            CONFIG["CUCU_LOGGING_LEVEL"].upper(),
        ]

    if format == "json":
        args.append("--no-summary")

    for tag in tags:
        args.append("--tags")
        args.append(tag)

    if source:
        args += ["--show-source"]
    else:
        args += ["--no-source"]

    if name is not None:
        args += ["--name", name]

    if fail_fast:
        args.append("--stop")

    try:
        from behave.__main__ import main as behave_main

        exit_code = behave_main(args)
        if exit_code != 0:
            raise ClickException("test run failed, see above for details")
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

    if not os.path.exists(output):
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
@click.option(
    "-f",
    "--format",
    default="human",
    help="output format to use, available: human, json."
    "default: human. PRO TIP: `brew install fzf` and then "
    "`cucu steps | fzf` and easily find the step you need.",
)
def steps(format):
    """
    print available cucu steps
    """
    if format == "human":
        print_human_readable_steps()
    elif format == "json":
        print_json_steps()
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
                        if "fixed" in violation:
                            suffix = " ✓"
                            violations_fixed += 1
                        else:
                            suffix = " ✗ (must be fixed manually)"

                    filepath = location["filepath"]
                    line_number = location["line"] + 1
                    print(f"{filepath}:{line_number}: {type} {message}{suffix}")

        and_message = ""

    if violations_found != 0:
        if fix:
            if violations_found == violations_fixed:
                and_message = " and fixed"
            else:
                and_message = " and not all were fixed"

        print(
            f"\nlinting errors were found{and_message}, see above for details"
        )

        if not fix:
            print("NOTE: to try and fix violations automatically use --fix")
            raise ClickException("see above for details")


@main.command()
def lsp():
    """
    start the cucu language server
    """
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

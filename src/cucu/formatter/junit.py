# -*- coding: utf-8 -*-
import os
import traceback
from datetime import datetime
from xml.sax.saxutils import escape

import bs4
from behave.formatter.base import Formatter
from behave.model_core import Status
from bs4.formatter import XMLFormatter
from tenacity import RetryError

from cucu.ansi_parser import remove_ansi
from cucu.config import CONFIG
from cucu.utils import ellipsize_filename


class CucuJUnitFormatter(Formatter):
    name = "cucu-junit"
    description = "JUnit Formater"

    def __init__(self, stream_opener, config):
        super(CucuJUnitFormatter, self).__init__(stream_opener, config)
        self.xml_root = None
        self.current_feature = None
        self.current_scenario = None
        self.curent_step = None
        self.current_scenario_traceback = None
        self.current_scenario_duration = 0.0
        self.current_scenario_results = {}
        self.feature_timestamp = None
        self.steps = []

    # -- FORMATTER API:
    def uri(self, uri):
        pass

    def feature(self, feature):
        self.current_feature = feature
        date_now = datetime.now()
        self.feature_results = {
            "name": escape(feature.name),
            "foldername": escape(ellipsize_filename(feature.name)),
            "tests": 0,
            "errors": 0,
            "failures": 0,
            "skipped": 0,
            "timestamp": date_now.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
            "scenarios": {},
        }
        if feature.tags:
            self.feature_results["tags"] = ", ".join(feature.tags)

    def background(self, background):
        # -- ADD BACKGROUND STEPS: Support *.feature file regeneration.
        for step_ in background.steps:
            self.step(step_)

    def update_scenario(self):
        if self.current_scenario is not None:
            self.current_scenario_results["time"] = str(
                round(self.current_scenario_duration, 3)
            )
            if self.current_scenario.terminated:
                status = "terminated"
            elif self.current_scenario.hook_failed:
                status = "error"
            else:
                status = self.current_scenario.compute_status().name

            self.current_scenario_results["status"] = status

            if status == "failed" and self.current_scenario_traceback:
                self.current_scenario_results["failure"] = (
                    self._collect_detail_lines()
                )
            elif status == "terminated":
                # Emit error child element for terminated (timeout) scenarios
                # so JUnit consumers (CI, TestRail) classify them as non-passing
                details = [
                    "scenario terminated: worker timeout (InterruptWorker)"
                ]
                self.current_scenario_results["error"] = details
            elif status not in ("passed", "failed", "skipped"):
                # error-like status (predominantly a before/after-scenario hook
                # failure, where no step ran; see environment.py). Standard JUnit
                # consumers classify a testcase by its child element, so we must
                # capture the hook error message and emit an <error> child below.
                details = []
                for results_attr in (
                    "before_hook_results",
                    "after_hook_results",
                ):
                    for hook_result in getattr(
                        self.current_scenario, results_attr, []
                    ):
                        if hook_result.get("status") == "error":
                            details += hook_result.get("error_message", [])

                details += self._collect_detail_lines()
                if not details:
                    details = [f"scenario errored with status: {status}"]
                self.current_scenario_results["error"] = details

            if status == "skipped":
                self.current_scenario_results["skipped"] = True

    def _collect_detail_lines(self):
        """
        build the human readable detail lines for a failed/errored scenario:
        custom failure handler output, the failing step, the exception, and
        optionally the formatted stack trace
        """
        details = []
        failure_handlers = CONFIG["__CUCU_CUSTOM_FAILURE_HANDLERS"]

        for failure_handler in failure_handlers:
            details.append(
                failure_handler(self.current_feature, self.current_scenario)
            )

        if getattr(self, "current_step", None) is not None:
            details += [
                f"{self.current_step.keyword} {self.current_step.name} (after {round(self.current_step.duration, 3)}s)"
            ]

            if error := self.current_step.exception:
                if isinstance(error, RetryError):
                    error = error.last_attempt.exception()

                if len(error.args) > 0 and isinstance(error.args[0], str):
                    error_class_name = error.__class__.__name__
                    error_lines = error.args[0].splitlines()
                    error_lines[0] = f"{error_class_name}: {error_lines[0]}"
                else:
                    error_lines = [repr(error)]
                details += error_lines

        if (
            CONFIG["CUCU_JUNIT_WITH_STACKTRACE"] == "true"
            and self.current_scenario_traceback
        ):
            details += traceback.format_tb(self.current_scenario_traceback)

        return details

    def scenario(self, scenario):
        self.update_scenario()

        self.current_scenario = scenario
        self.current_scenario_traceback = None
        self.current_scenario_duration = 0.0
        self.current_scenario_results = {
            "status": "pending",
            "time": "n/a",
            "failure": None,
            "error": None,
            "skipped": None,
        }
        self.current_scenario_results["foldername"] = escape(
            ellipsize_filename(scenario.name)
        )
        if scenario.tags:
            self.current_scenario_results["tags"] = ", ".join(scenario.tags)

        scenario_name = escape(scenario.name)
        self.feature_results["scenarios"][scenario_name] = (
            self.current_scenario_results
        )

        # we write out every new scenario into the JUnit results output
        # which allows us to have a valid JUnit XML results file per feature
        # file currently running even if the process crashes or is killed so we
        # can still generate valid reports from every run.
        self.write_results(self.feature_results)

    def match(self, step):
        pass

    def step(self, step):
        self.steps.append(step)

    def insert_step(self, step, index=-1):
        if index == -1:
            self.steps.append(step)
        else:
            self.steps.insert(index, step)

    def result(self, step):
        self.current_step = step
        if step.status == Status.failed:
            self.current_scenario_traceback = step.exc_traceback

        self.current_scenario_duration += step.duration

    def eof(self):
        """
        end of file for the feature and this is when we write the updated
        results to the file
        """
        self.update_scenario()
        self.write_results(self.feature_results)

    def close(self):
        pass

    def write_results(self, results):
        """
        given a feature results dictionary that looks like so:
            {
                "name": "name of the feature",
                "foldername": "",
                "tests": 0,
                "errors": 0,
                "failures": 0,
                "skipped": 0,
                "timestamp": "",
                "scenarios": {
                    "scenario name": {
                        "foldername": "",
                        "tags": "DOM-3435, testrail(3366,45891)",
                        "status": "passed/failed/skipped",
                        "time": "0.0000":
                        "stdout": "",
                        "stderr": "",
                    },
                    ...
                }
            }
        """

        # custom attribute ordering so attributes are printed in a consistent
        # and desired order
        class SortAttributes(XMLFormatter):
            def attributes(self, tag):
                ordered = [
                    "classname",
                    "name",
                    "foldername",
                    "tests",
                    "errors",
                    "failures",
                    "skipped",
                    "status",
                    "timestamp",
                    "time",
                    "tags",
                ]

                return [
                    (attr, tag[attr]) for attr in ordered if attr in tag.attrs
                ]

        soup = bs4.BeautifulSoup()
        testsuite = bs4.Tag(name="testsuite")
        testsuite["name"] = results["name"]
        testsuite["foldername"] = results["foldername"]
        testsuite["timestamp"] = results["timestamp"]

        junit_dir = CONFIG["CUCU_JUNIT_DIR"]
        os.makedirs(junit_dir, exist_ok=True)

        feature_name = results["name"]
        output_filepath = os.path.join(junit_dir, f"{feature_name}.xml")

        scenarios = results["scenarios"]

        if CONFIG["CUCU_SHOW_SKIPS"] != "true":
            filtered_scenarios = {}

            for name, scenario in scenarios.items():
                if scenario["status"] != "skipped":
                    filtered_scenarios[name] = scenario

            scenarios = filtered_scenarios

            if len(scenarios) == 0:
                # we had a suite of just skipped results
                return

        # calculate with the latest data
        # workaround for beatufulsoup4 removing the attribute if it is set to 0
        testsuite["tests"] = str(len(scenarios))
        testsuite["failures"] = str(
            len(
                [x for x in scenarios.values() if x["status"] == Status.failed]
            )
        )
        testsuite["skipped"] = str(
            len(
                [
                    x
                    for x in scenarios.values()
                    if x["status"] == Status.skipped
                ]
            )
        )
        testsuite["errors"] = str(
            len(
                [
                    x
                    for x in scenarios.values()
                    if x["status"]
                    not in (
                        Status.failed,
                        Status.skipped,
                        Status.passed,
                        "terminated",
                    )
                ]
            )
        )

        if "tags" in results:
            testsuite["tags"] = results["tags"]
        soup.append(testsuite)

        for scenario_name in scenarios:
            scenario = scenarios[scenario_name]
            testcase = bs4.Tag(name="testcase")
            testcase["classname"] = results["name"]
            testcase["name"] = scenario_name
            testcase["foldername"] = scenario["foldername"]
            if "tags" in scenario:
                testcase["tags"] = scenario["tags"]
            testcase["status"] = scenario["status"]
            testcase["time"] = scenario["time"]

            if scenario["failure"] is not None:
                failure_message = "\n".join(scenario["failure"])
                failure = bs4.Tag(name="failure")
                cleaned_failure_message = remove_ansi(failure_message)
                failure.append(bs4.CData(cleaned_failure_message))
                testcase.append(failure)

            if scenario.get("error") is not None:
                error_message = "\n".join(scenario["error"])
                error = bs4.Tag(name="error")
                error.append(bs4.CData(remove_ansi(error_message)))
                testcase.append(error)

            if scenario["skipped"] is not None:
                testcase.append(bs4.Tag(name="skipped"))

            testsuite.append(testcase)

        feature_name = results["name"]
        output_filepath = os.path.join(junit_dir, f"{feature_name}.xml")
        with open(output_filepath, "w", encoding="utf-8") as output:
            output.write(soup.prettify(formatter=SortAttributes()))

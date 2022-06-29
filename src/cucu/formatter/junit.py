# -*- coding: utf-8 -*-
import bs4
import os
import re
import traceback

from behave.formatter.base import Formatter
from behave.model_core import Status
from bs4.formatter import XMLFormatter
from cucu.config import CONFIG
from datetime import datetime
from xml.sax.saxutils import escape


class CucuJUnitFormatter(Formatter):
    name = "cucu-junit"
    description = "JUnit Formater"

    def __init__(self, stream_opener, config):
        super(CucuJUnitFormatter, self).__init__(stream_opener, config)
        self.xml_root = None
        self.current_scenario = None
        self.current_scenario_traceback = None
        self.current_scenario_duration = 0.0
        self.current_scenario_results = {}
        self.feature_timestamp = None
        self.steps = []

    # -- FORMATTER API:
    def uri(self, uri):
        pass

    def feature(self, feature):
        date_now = datetime.now()
        self.feature_results = {
            "name": escape(feature.name),
            "tests": 0,
            "errors": 0,
            "failures": 0,
            "skipped": 0,
            "timestamp": date_now.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
            "scenarios": {},
        }

    def background(self, background):

        # -- ADD BACKGROUND STEPS: Support *.feature file regeneration.
        for step_ in background.steps:
            self.step(step_)

    def update_scenario(self):
        if self.current_scenario is not None:
            self.current_scenario_results["time"] = str(
                round(self.current_scenario_duration, 3)
            )

            status = self.current_scenario.compute_status().name
            self.current_scenario_results["status"] = status

            if status == "failed" and self.current_scenario_traceback:
                failure = traceback.format_tb(self.current_scenario_traceback)
                self.current_scenario_results["failure"] = failure

    def scenario(self, scenario):
        self.update_scenario()

        self.current_scenario = scenario
        self.current_scenario_traceback = None
        self.current_scenario_duration = 0.0
        self.current_scenario_results = {
            "status": "pending",
            "time": "n/a",
            "failure": None,
        }
        testrail_re = re.compile(r'testrail\((.+)\)')
        for tag in scenario.tags:
            testrail_tag = testrail_re.match(tag)
            if testrail_tag is not None:
                self.current_scenario_results["testcase_ids"] = testrail_tag.group(1)

        scenario_name = escape(scenario.name)
        self.feature_results["scenarios"][
            scenario_name
        ] = self.current_scenario_results

        # we write out every new scenario into the JUnit results output which
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
                "tests": 0,
                "errors": 0,
                "failures": 0,
                "skipped": 0,
                "timestamp": "",
                "scnearios": {
                    "scenario name": {
                        "testcase_ids": "3366, 45891",
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
                    "testcase_ids",
                    "tests",
                    "errors",
                    "failures",
                    "skipped",
                    "status",
                    "timestamp",
                    "time",
                ]

                return [
                    (attr, tag[attr]) for attr in ordered if attr in tag.attrs
                ]

        soup = bs4.BeautifulSoup()
        testsuite = bs4.Tag(name="testsuite")
        testsuite["name"] = results["name"]
        testsuite["tests"] = results["tests"]
        testsuite["errors"] = results["errors"]
        testsuite["failures"] = results["failures"]
        testsuite["skipped"] = results["skipped"]
        testsuite["timestamp"] = results["timestamp"]
        soup.append(testsuite)

        for scenario_name in results["scenarios"]:
            scenario = results["scenarios"][scenario_name]
            testcase = bs4.Tag(name="testcase")
            testcase["classname"] = results["name"]
            testcase["name"] = scenario_name
            if "testcase_ids" in scenario:
                testcase["testcase_ids"] = scenario["testcase_ids"]
            testcase["status"] = scenario["status"]
            testcase["time"] = scenario["time"]

            if scenario["failure"] is not None:
                failure_message = "\n".join(scenario["failure"])
                failure = bs4.Tag(name="failure")
                failure.append(bs4.CData(failure_message))
                testcase.append(failure)

            testsuite.append(testcase)

        junit_dir = CONFIG["CUCU_JUNIT_DIR"]
        os.makedirs(junit_dir, exist_ok=True)

        feature_name = results["name"].replace(" ", "_")
        output_filepath = os.path.join(junit_dir, f"TESTS-{feature_name}.xml")
        with open(output_filepath, "w", encoding="utf-8") as output:
            output.write(soup.prettify(formatter=SortAttributes()))

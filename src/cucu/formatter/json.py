# -*- coding: utf-8 -*-
#
# adapted from:
#   https://github.com/behave/behave/blob/master/behave/formatter/json.py
#
from __future__ import absolute_import

import json
import traceback
import uuid

import six
from behave.formatter.base import Formatter
from behave.model_core import Status
from tenacity import RetryError

from cucu.config import CONFIG


# -----------------------------------------------------------------------------
# CLASS: JSONFormatter
# -----------------------------------------------------------------------------
class CucuJSONFormatter(Formatter):
    name = "cucu-json"
    description = "JSON dump of test run"
    dumps_kwargs = {"indent": 2, "sort_keys": True}

    split_text_into_lines = True  # EXPERIMENT for better readability.

    json_number_types = six.integer_types + (float,)
    json_scalar_types = json_number_types + (six.text_type, bool, type(None))

    def __init__(self, stream_opener, config):
        super(CucuJSONFormatter, self).__init__(stream_opener, config)
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.feature_count = 0
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None
        self.last_step = None
        self.steps = []
        self.write_json_header()

    def reset(self):
        self.current_feature = None
        self.current_feature_data = None
        self.current_scenario = None

    # -- FORMATTER API:
    def uri(self, uri):
        pass

    def feature(self, feature):
        self.reset()
        self.current_feature = feature
        self.current_feature_data = {
            "keyword": feature.keyword,
            "name": feature.name,
            "tags": list(feature.tags),
            "location": six.text_type(feature.location),
            "status": None,  # Not known before feature run.
        }
        element = self.current_feature_data
        if feature.description:
            element["description"] = feature.description

    def background(self, background):
        element = self.add_feature_element(
            {
                "type": "background",
                "keyword": background.keyword,
                "name": background.name,
                "location": six.text_type(background.location),
                "steps": [],
            }
        )
        if background.name:
            element["name"] = background.name

        # -- ADD BACKGROUND STEPS: Support *.feature file regeneration.
        for step_ in background.steps:
            self.step(step_)

    def scenario(self, scenario):
        self.finish_current_scenario()
        self.current_scenario = scenario

        element = self.add_feature_element(
            {
                "type": "scenario",
                "keyword": scenario.keyword,
                "name": scenario.name,
                "tags": scenario.tags,
                "location": six.text_type(scenario.location),
                "steps": [],
                "status": None,
            }
        )
        self.steps = []
        if scenario.description:
            element["description"] = scenario.description

    @classmethod
    def make_table(cls, table):
        table_data = {
            "headings": table.headings,
            "rows": [list(row) for row in table.rows],
        }
        return table_data

    def insert_step(self, step, index=-1):
        step.unique_id = uuid.uuid1()
        is_substep = getattr(step, "is_substep", False)

        step_details = {
            "keyword": step.keyword,
            "step_type": step.step_type,
            "name": step.name,
            "location": six.text_type(step.location),
            "substep": is_substep,
        }

        if step.text:
            text = step.text
            if self.split_text_into_lines and "\n" in text:
                text = text.splitlines()
            step_details["text"] = text
        if step.table:
            step_details["table"] = self.make_table(step.table)
        element = self.current_feature_element

        if index == -1:
            self.steps.append(step)
            element["steps"].append(step_details)
        else:
            self.steps.insert(index, step)
            element["steps"].insert(index, step_details)

    def step(self, step):
        self.insert_step(step, index=-1)

    def match(self, match):
        # nothing to do, but we need to implement the method
        pass

    def result(self, step):
        steps = self.current_feature_element["steps"]
        step_index = 0
        for other_step in self.steps:
            if other_step.unique_id == step.unique_id:
                break
            step_index += 1

        # keep the last step recorded result state
        self.last_step = steps[step_index]

        timestamp = None
        if step.status.name in ["passed", "failed"]:
            timestamp = step.start_timestamp

            step_variables = CONFIG.expand(step.name)

            if step.text:
                step_variables.update(CONFIG.expand(step.text))

            if step.table:
                for row in step.table.original.rows:
                    for value in row:
                        step_variables.update(CONFIG.expand(value))

            if step_variables:
                expanded = " ".join(
                    [
                        f'{key}="{value}"'
                        for (key, value) in step_variables.items()
                    ]
                )
                padding = f"    {' '*(len('Given')-len(step.keyword))}"
                step.stdout.insert(
                    0, f"{padding}# {CONFIG.hide_secrets(expanded)}\n"
                )

        stdout = None
        if "stdout" in step.__dict__ and step.stdout != []:
            stdout = [CONFIG.hide_secrets("".join(step.stdout).rstrip())]

        stderr = None
        if "stderr" in step.__dict__ and step.stderr != []:
            stderr = [CONFIG.hide_secrets("".join(step.stderr).rstrip())]

        steps[step_index]["result"] = {
            "stdout": stdout,
            "stderr": stderr,
            "status": step.status.name,
            "duration": step.duration,
            "timestamp": timestamp,
        }

        if step.error_message and step.status == Status.failed:
            # -- OPTIONAL: Provided for failed steps.
            error_message = CONFIG.hide_secrets(step.error_message)
            if self.split_text_into_lines:
                error_message = error_message.splitlines()

            result_element = steps[step_index]["result"]
            result_element["error_message"] = error_message

            if error := step.exception:
                if isinstance(error, RetryError):
                    error = error.last_attempt.exception()

                if len(error.args) > 0 and isinstance(error.args[0], str):
                    error_class_name = error.__class__.__name__
                    redacted_error_msg = CONFIG.hide_secrets(error.args[0])
                    error_lines = redacted_error_msg.splitlines()
                    error_lines[0] = f"{error_class_name}: {error_lines[0]}"
                else:
                    error_lines = [repr(error)]

                result_element["exception"] = error_lines

    def embedding(self, mime_type, data):
        # nothing to do, but we need to implement the method
        pass

    def eof(self):
        """
        End of feature
        """
        if not self.current_feature_data:
            return

        # -- NORMAL CASE: Write collected data of current feature.
        self.finish_current_scenario()
        self.update_status_data()

        self.write_json_feature(self.current_feature_data)
        self.reset()

    def close(self):
        self.write_json_footer()
        self.close_stream()

    # -- JSON-DATA COLLECTION:
    def add_feature_element(self, element):
        assert self.current_feature_data is not None
        if "elements" not in self.current_feature_data:
            self.current_feature_data["elements"] = []
        self.current_feature_data["elements"].append(element)
        return element

    @property
    def current_feature_element(self):
        assert self.current_feature_data is not None
        return self.current_feature_data["elements"][-1]

    def update_status_data(self):
        assert self.current_feature
        assert self.current_feature_data
        self.current_feature_data["status"] = self.current_feature.status.name

    def finish_current_scenario(self):
        if self.current_scenario:
            hook_failed = self.current_scenario.hook_failed
            if hook_failed:
                status_name = "errored"
            else:
                status_name = self.current_scenario.status.name

            self.current_feature_element["status"] = status_name

            if status_name in ["failed", "errored"]:
                # we need to record the error_message and exc_traceback in the
                # last executed step and mark it as failed so the reporting can
                # show the result correctly
                error_message = [self.current_scenario.error_message]
                error_message += traceback.format_tb(
                    self.current_scenario.exc_traceback
                )
                #  If a before scenario hook fails, last_step will be None.
                if (
                    self.last_step is not None
                    and "error_message" not in self.last_step["result"]
                ):
                    self.last_step["result"]["error_message"] = error_message

    # -- JSON-WRITER:
    def write_json_header(self):
        self.stream.write("[\n")

    def write_json_footer(self):
        self.stream.write("\n]\n")

    def write_json_feature(self, feature_data):
        if "elements" not in feature_data:
            return

        filtered_scenarios = [
            x
            for x in feature_data["elements"]
            if x["keyword"] == "Scenario"
            and (
                CONFIG["CUCU_SHOW_SKIPS"] == "true" or x["status"] != "skipped"
            )
        ]

        if len(filtered_scenarios) == 0:
            return

        feature_data["elements"] = filtered_scenarios

        if self.feature_count != 0:
            self.write_json_feature_separator()

        self.stream.write(json.dumps(feature_data, **self.dumps_kwargs))
        self.stream.flush()
        self.feature_count += 1

    def write_json_feature_separator(self):
        self.stream.write(",\n\n")

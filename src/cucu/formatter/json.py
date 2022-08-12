# -*- coding: utf-8 -*-
#
# adapted from:
#   https://github.com/behave/behave/blob/master/behave/formatter/json.py
#
from __future__ import absolute_import

import json
import six
import traceback
import uuid

from behave.formatter.base import Formatter
from behave.model_core import Status


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

        if "stdout" in step.__dict__:
            stdout = step.stdout
        else:
            stdout = ""
        if "stderr" in step.__dict__:
            stderr = step.stderr
        else:
            stderr = ""

        step_index = 0
        for other_step in self.steps:
            if other_step.unique_id == step.unique_id:
                break
            step_index += 1

        # keep the last step recorded result state
        self.last_step = steps[step_index]

        steps[step_index]["result"] = {
            "stdout": stdout,
            "stderr": stderr,
            "status": step.status.name,
            "duration": step.duration,
        }

        if step.error_message and step.status == Status.failed:
            # -- OPTIONAL: Provided for failed steps.
            error_message = step.error_message
            if self.split_text_into_lines and "\n" in error_message:
                error_message = error_message.splitlines()
            result_element = steps[step_index]["result"]
            result_element["error_message"] = error_message

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

        if self.feature_count == 0:
            # -- FIRST FEATURE:
            self.write_json_header()
        else:
            # -- NEXT FEATURE:
            self.write_json_feature_separator()

        self.write_json_feature(self.current_feature_data)
        self.reset()
        self.feature_count += 1

    def close(self):
        if self.feature_count == 0:
            # -- FIRST FEATURE: Corner case when no features are provided.
            self.write_json_header()
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
            status_name = self.current_scenario.status.name
            self.current_feature_element["status"] = status_name

            if status_name == "failed":
                # we need to record the error_message and exc_traceback in the
                # last executed step and mark it as failed so the reporting can
                # show the result correctly
                error_message = [self.current_scenario.error_message]
                error_message += traceback.format_tb(
                    self.current_scenario.exc_traceback
                )

                if "error_message" not in self.last_step["result"]:
                    self.last_step["result"]["error_message"] = error_message

    # -- JSON-WRITER:
    def write_json_header(self):
        self.stream.write("[\n")

    def write_json_footer(self):
        self.stream.write("\n]\n")

    def write_json_feature(self, feature_data):
        self.stream.write(json.dumps(feature_data, **self.dumps_kwargs))
        self.stream.flush()

    def write_json_feature_separator(self):
        self.stream.write(",\n\n")

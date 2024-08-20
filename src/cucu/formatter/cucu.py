# -*- coding: utf-8 -*-
from __future__ import absolute_import

import traceback

from behave.formatter.ansi_escapes import colors, escapes, up
from behave.formatter.base import Formatter
from behave.model_core import Status
from behave.model_describe import ModelPrinter
from behave.textutil import make_indentation

from cucu.config import CONFIG


class CucuFormatter(Formatter):
    """ """

    name = "cucu"
    description = "cucu specific formatter to make the logs more readable"

    DEFAULT_INDENT_SIZE = 2
    SUBSTEP_PREFIX = "  ⤷"

    def __init__(self, stream_opener, config, **kwargs):
        super(CucuFormatter, self).__init__(stream_opener, config)
        self.current_scenario = None
        self.steps = []
        self.match_step_index = 0
        self.show_timings = config.show_timings
        self.indent_size = self.DEFAULT_INDENT_SIZE
        # -- ENSURE: Output stream is open.
        self.stream = self.open()
        self.printer = ModelPrinter(self.stream)
        # -- LAZY-EVALUATE:
        self._multiline_indentation = None

        color_output = CONFIG["CUCU_COLOR_OUTPUT"]
        self.monochrome = color_output != "true"

    @property
    def multiline_indentation(self):
        if self._multiline_indentation is None:
            # align keywords
            offset = 2
            indentation = make_indentation(3 * self.indent_size + offset)
            self._multiline_indentation = indentation

        return self._multiline_indentation

    def write_tags(self, tags, indent=None, for_feature=False):
        """
        writes the tags for a scenario or feature and takes extra care to be
        sure to indent corectly for scenarios when `indent` is specified. We
        also handle putting new lines in the right locations if its a scenario
        or feature based on `for_feature` boolean flag.
        """
        indent = indent or ""
        if tags:
            text = " @".join(tags)
            line = self.colorize(f"{indent}@{text}", "cyan")
            if for_feature:
                self.stream.write(f"{line}\n")
            else:
                self.stream.write(f"\n{line}")

    # -- IMPLEMENT-INTERFACE FOR: Formatter
    def feature(self, feature):
        self.write_tags(feature.tags, for_feature=True)
        text = f'{self.colorize(feature.keyword, "magenta")}: {feature.name}\n'
        self.stream.write(text)

    def colorize(self, text, color):
        if self.monochrome:
            return text
        else:
            return colors[color] + text + escapes["reset"]

    def background(self, background):
        if not self.monochrome:
            indent = make_indentation(self.indent_size)
            keyword = self.colorize(background.keyword, "magenta")
            text = f"\n{indent}{keyword}: {background.name}\n"
            self.stream.write(text)

    def scenario(self, scenario):
        self.current_scenario = scenario

        indent = make_indentation(self.indent_size)
        text = "\n%s%s: %s\n" % (
            indent,
            self.colorize(scenario.keyword, "magenta"),
            scenario.name,
        )
        self.write_tags(scenario.tags, indent)
        self.stream.write(text)
        self.steps = []
        self.match_step_index = 0

    def step(self, step):
        self.insert_step(step)

    def insert_step(self, step, index=-1):
        # used to determine how to better handle console output
        step.has_substeps = False
        step.is_substep = False

        if index == -1:
            self.steps.append(step)
        else:
            self.steps.insert(index, step)

    def match(self, match):
        if self.monochrome:
            return

        # we'll write a step line in grey and not hit the carriage return
        step = self.steps[self.match_step_index]
        self.match_step_index += 1

        indent = make_indentation(2 * self.indent_size)
        keyword = step.keyword.rjust(5)

        prefix = ""
        if step.is_substep:
            prefix = self.SUBSTEP_PREFIX

        text = self.colorize(
            f"{indent}{prefix}{keyword} {step.name}\n", "grey"
        )
        self.stream.write(text)
        self.stream.flush()

    def calculate_max_line_length(self):
        line_lengths = [
            len(f"{step.keyword.rjust(5)} {step.name}") for step in self.steps
        ]

        return max(line_lengths) + 4

    def result(self, step):
        indent = make_indentation(2 * self.indent_size)
        keyword = step.keyword.rjust(5)

        if not (
            self.monochrome
            or step.has_substeps
            or CONFIG["__CUCU_WROTE_TO_OUTPUT"]
        ):
            self.stream.write(up(1))

        prefix = ""
        if step.is_substep:
            prefix = self.SUBSTEP_PREFIX

        if step.status == Status.passed:
            keyword = self.colorize(keyword, "green")
            text = f"{indent}{prefix}{keyword} {step.name}"
        elif step.status == Status.failed:
            text = self.colorize(
                f"{indent}{prefix}{keyword} {step.name}", "red"
            )
        elif step.status == Status.undefined:
            text = self.colorize(
                f"{indent}{prefix}{keyword} {step.name}", "yellow"
            )
        elif step.status == Status.skipped:
            text = self.colorize(
                f"{indent}{prefix}{keyword} {step.name}\n", "cyan"
            )
        elif step.status == Status.untested:
            text = self.colorize(
                f"{indent}{prefix}{keyword} {step.name}\n", "cyan"
            )

        if self.monochrome:
            self.stream.write(f"{text}")
        else:
            self.stream.write(f"\r{text}")

        if step.status in (Status.passed, Status.failed):
            max_line_length = self.calculate_max_line_length()
            status_text = ""
            if self.show_timings:
                start = step.start_timestamp
                duration = f"{step.duration:.3f}"
                status_text += f" # started at {start} took {duration}s"

            current_step_text = f"{step.keyword.rjust(5)} {step.name}"
            status_text_padding = (
                max_line_length - len(current_step_text) - len(prefix)
            )
            status_text = f'{" " * status_text_padding}{status_text}'
            status_text = self.colorize(status_text, "yellow")

            self.stream.write(f"{status_text}\n")
            if step.error_message:
                self.stream.write(f"{step.error_message}\n")

        if step.text:
            self.doc_string(step.text)

        if step.table:
            self.table(getattr(step.table, "original", step.table))

        if step.status in (Status.passed, Status.failed):
            # print the variable values in step name, multiline/table arguments
            # as a comment to ease debugging
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
                variable_line = f"{padding}# {expanded}\n"
                # hide secrets before we do anything to add color which could
                # modify the output and result in not being able to correctly
                # parse
                # TODO: I'd like to move this out of here as we should be able
                #       to intercept all of the stdout/stderr writes but seems
                #       behaves underlying self.stream here is getting around
                #       that by accessing stdout/stderr another way.
                variable_line = CONFIG.hide_secrets(variable_line)
                colored_variable_line = self.colorize(variable_line, "blue")
                self.stream.write(colored_variable_line)
                self.stream.flush()

        self.previous_step = step
        CONFIG["__CUCU_WROTE_TO_OUTPUT"] = False

    def eof(self):
        self.stream.write("\n")

        if self.current_scenario:
            if self.current_scenario.status.name == "failed":
                # we need to record the error_message and exc_traceback in the
                # last executed step and mark it as failed so the reporting can
                # show the result correctly
                error_message = traceback.format_tb(
                    self.current_scenario.exc_traceback
                )
                self.stream.write("\n".join(error_message))

    # -- MORE: Formatter helpers
    def doc_string(self, doc_string):
        self.printer.print_docstring(doc_string, self.multiline_indentation)

    def table(self, table):
        self.printer.print_table(table, self.multiline_indentation)

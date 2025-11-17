# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import time
from pathlib import Path

from behave.formatter.base import Formatter
from behave.model import ScenarioOutline

from cucu import logger
from cucu.config import CONFIG
from cucu.db import (
    close_db,
    create_database_file,
    finish_cucu_run_record,
    finish_feature_record,
    finish_scenario_record,
    finish_step_record,
    finish_worker_record,
    record_cucu_run,
    record_feature,
    record_scenario,
    start_step_record,
)
from cucu.utils import (
    generate_short_id,
    get_iso_timestamp_with_ms,
)


class RundbFormatter(Formatter):
    """
    Record to the database using the Formatter Behave API.
    This is different from hooks as we don't have access to context (ctx) here.
    Instead we use this class's data and add some data to the passed in objects: feature, scenario, step.
    Another difference is that we can't rely on hooks to execute, as the step/scenario/feature may be skipped.
    Also, use cucu's CONFIG for global data since we don't have context (ctx).

    ## Just for reference:
    Processing Logic (simplified, without ScenarioOutline and skip logic)::

        for feature in runner.features:
            formatter = make_formatters(...)
            formatter.uri(feature.filename)
            formatter.feature(feature)
            for scenario in feature.scenarios:
                formatter.scenario(scenario)
                for step in scenario.all_steps:
                    formatter.step(step)
                    step_match = step_registry.find_match(step)
                    formatter.match(step_match)
                    if step_match:
                        step_match.run()
                    else:
                        step.status = Status.undefined
                    formatter.result(step.status)
            formatter.eof() # -- FEATURE-END
        formatter.close()
    """

    # -- FORMATTER API:
    name = "rundb"
    description = "records the results of the run to the run.db database"

    def __init__(self, stream_opener, config):
        super(RundbFormatter, self).__init__(stream_opener, config)
        # We don't actually use the stream provided by Behave, so don't open it.
        # self.stream = self.open()
        self.config = config

        if (
            not CONFIG["RUN_DB_PATH"]
            or CONFIG["WORKER_RUN_ID"] != CONFIG["WORKER_PARENT_ID"]
        ):
            logger.debug(
                "Create a new worker db since this isn't the parent process"
            )
            # use seed unique enough for multiple cucu_runs to be combined but predictable within the same run
            worker_id_seed = f"{CONFIG['WORKER_PARENT_ID']}_{os.getpid()}"
            CONFIG["WORKER_RUN_ID"] = generate_short_id(worker_id_seed)

            results_path = Path(CONFIG["CUCU_RESULTS_DIR"])
            worker_run_id = CONFIG["WORKER_RUN_ID"]
            cucu_run_id = CONFIG["CUCU_RUN_ID"]
            CONFIG["RUN_DB_PATH"] = run_db_path = (
                results_path / f"run_{cucu_run_id}_{worker_run_id}.db"
            )

            if not run_db_path.exists():
                logger.debug(
                    f"Creating new run database file: {run_db_path} for {worker_id_seed}"
                )
                create_database_file(run_db_path)
                record_cucu_run()

    def uri(self, uri):
        # nothing to do, but we need to implement the method for behave
        pass

    def feature(self, feature):
        """Called before a feature is executed."""
        self.this_feature = feature
        self.this_scenario = None
        self.this_background = None
        self.next_start_at = None

        feature_run_id_seed = (
            f"{CONFIG['WORKER_RUN_ID']}_{time.perf_counter()}"
        )
        feature.feature_run_id = generate_short_id(feature_run_id_seed)
        feature.custom_data = {}

        record_feature(feature)

    def background(self, background):
        # nothing to do, but we need to implement the method for behave
        pass

    def _finish_scenario(self):
        if self.this_scenario is None:
            return

        # ensure non-executed steps have correct seq
        for index, step in enumerate(self.this_steps):
            if getattr(step, "seq", -1) == -1:
                step.seq = index + 1  # 1-based sequence
                finish_step_record(step, 0)

        finish_scenario_record(self.this_scenario)

    def scenario(self, scenario):
        """Called before a scenario is executed (or ScenarioOutline scenarios)."""
        self._finish_scenario()

        self.this_scenario = scenario
        self.this_steps = []
        self.next_start_at = get_iso_timestamp_with_ms()
        scenario.custom_data = {}
        scenario.scenario_run_id = generate_short_id(
            f"{scenario.feature.feature_run_id}_{time.perf_counter()}"
        )

        # feature.scenarios is a mix of Scenario and ScenarioOutline objects with their own scenarios list
        for index, feature_scenario in enumerate(scenario.feature.scenarios):
            if feature_scenario == scenario:
                scenario.seq = index + 1
                break

            # Scenarios belonging to a Scenario Outline are included under their Scenario Outline sequence.
            # Add a suffix to preserve ordering within the Scenario Outline.
            if isinstance(feature_scenario, ScenarioOutline):
                for sub_index, sub_scenario in enumerate(
                    feature_scenario._scenarios
                ):
                    if sub_scenario == scenario:
                        scenario.seq = index + 1 + (sub_index + 1) / 10
                        break

        record_scenario(scenario)

    def step(self, step):
        """Called before a step is executed (and matched)."""
        self.insert_step(step, index=-1)

    def insert_step(self, step, index):
        """cucu specific step insertion method used to add steps here and dynamically"""
        next_index = index if index != -1 else len(self.this_steps)
        step_run_id_seed = f"{self.this_scenario.scenario_run_id}_{next_index}_{time.perf_counter()}"
        step.step_run_id = generate_short_id(
            step_run_id_seed, length=10
        )  # up to 10 characters to give two orders of magnitude less chance of collision
        self.this_steps.insert(next_index, step)
        start_step_record(step, self.this_scenario.scenario_run_id)

    def match(self, match):
        # nothing to do, but we need to implement the method for behave
        pass

    def result(self, step):
        """Called after processing a step result is known, applies to executed/skipped too."""
        step.start_at = self.next_start_at
        self.next_start_at = step.end_at = get_iso_timestamp_with_ms()
        previous_step_duration = getattr(
            self.this_scenario, "previous_step_duration", 0
        )
        if step.status.name in ("untested", "undefined"):
            step.seq = self.this_steps.index(step) + 1

        finish_step_record(step, previous_step_duration)

    def eof(self):
        """Called after processing a feature (or a feature file)."""
        # need to finish the last scenario
        self._finish_scenario()
        finish_feature_record(self.this_feature)
        CONFIG.restore(with_pop=True)

    def close(self):
        """Called before the formatter is no longer used
        (stream/io compatibility).
        """
        finish_worker_record(None)
        finish_cucu_run_record()
        close_db()

# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import os
import time
from pathlib import Path

from behave.formatter.base import Formatter

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
)


class RundbFormatter(Formatter):
    """
    Record to database formatter.

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
        # We don't actually use the stream so don't open it.
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

    def scenario(self, scenario):
        """Called before a scenario is executed (or ScenarioOutline scenarios)."""
        self._finish_sceario()

        self.this_scenario = scenario
        self.steps = []
        self.next_start_at = datetime.datetime.now().isoformat()[:-3]
        scenario_run_id_seed = (
            f"{scenario.feature.feature_run_id}_{time.perf_counter()}"
        )
        scenario.scenario_run_id = generate_short_id(scenario_run_id_seed)
        record_scenario(scenario)

    def step(self, step):
        """Called before a step is executed (and matched)."""
        self.insert_step(step, index=-1)

    def insert_step(self, step, index):
        """cucu specific step insertion method used to add steps here and dynamically"""
        next_index = index if index != -1 else len(self.steps)
        step_run_id_seed = f"{self.this_scenario.scenario_run_id}_{next_index}_{time.perf_counter()}"
        step.step_run_id = generate_short_id(
            step_run_id_seed, length=10
        )  # up to 10 characters to give two orders of magnitude less chance of collision
        self.steps.insert(next_index, step)
        start_step_record(step, self.this_scenario.scenario_run_id)

    def match(self, match):
        """Called when a step was matched against its step implementation.

        :param match:  Registered step (as Match), undefined step (as NoMatch).
        """
        pass

    def result(self, step):
        """Called after processing a step (when the step result is known).

        :param step:  Step object with result (after being executed/skipped).
        """
        step.start_at = self.next_start_at
        self.next_start_at = step.end_at = datetime.datetime.now().isoformat()[
            :-3
        ]
        previous_step_duration = getattr(
            self.this_scenario, "previous_step_duration", 0
        )
        if step.status.name in ("untested","undefined"):
            step.seq = self.this_scenario.steps.index(step) + 1

        finish_step_record(step, previous_step_duration)

    def _finish_sceario(self):
        if self.this_scenario is None:
            return

        # ensure non-executed steps have correct seq
        for index, step in enumerate(self.steps):
            if getattr(step, "seq", -1) == -1:
                step.seq = index + 1  # 1-based sequence
                finish_step_record(step, None)

        finish_scenario_record(self.this_scenario)

    def eof(self):
        """Called after processing a feature (or a feature file)."""
        # need to finish the last scenario
        self._finish_sceario()
        finish_feature_record(self.this_feature)

    def close(self):
        """Called before the formatter is no longer used
        (stream/io compatibility).
        """
        finish_worker_record(None)
        finish_cucu_run_record()
        close_db()

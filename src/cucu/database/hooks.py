"""
Database integration with environment hooks.
"""

import hashlib
import os
import time
from datetime import datetime, timedelta

from cucu import logger
from cucu.config import CONFIG
from cucu.database import operations
from cucu.database.connection import get_connection


def start_run(ctx, start_time):
    cucu_run_id = CONFIG["CUCU_RUN_ID"]
    timestamp = datetime.fromtimestamp(start_time)
    conn = get_connection()
    conn.execute(
        """
        UPDATE CucuRun
        SET status = 'running', start_time = ?
        WHERE cucu_run_id = ?
    """,
        [timestamp, cucu_run_id],
    )


def create_feature_in_before_feature(ctx, feature):
    cucu_run_id = CONFIG["CUCU_RUN_ID"]
    conn = get_connection()
    name = feature.name
    description = feature.description
    filepath = feature.filename
    tags = [tag for tag in feature.tags] if feature.tags else []

    ctx.db_feature_id = operations.create_feature(
        conn,
        cucu_run_id,
        name,
        description,
        filepath,
        tags,
    )


def update_feature_in_after_feature(ctx, feature):
    conn = get_connection()
    total_duration_ms = None
    if hasattr(feature, "start_time") and feature.start_time:
        total_duration_ms = int((time.time() - feature.start_time) * 1000)

    status = "passed"
    if feature.status == "failed":
        status = "failed"
    elif feature.status == "skipped":
        status = "skipped"

    operations.update_feature(
        conn,
        CONFIG["current_feature_id"],
        status,
        total_duration_ms,
    )
    logger.debug(
        f"Updated Feature record {CONFIG['current_feature_id']} with status {status}"
    )

    CONFIG["current_feature_id"] = None


def create_scenario_in_before_scenario(ctx, scenario):
    conn = get_connection()
    ctx.db_scenario_id = operations.create_scenario(
        conn,
        ctx.db_feature_id,
        scenario.name,
        scenario.filename,
        scenario.line,
        scenario.tags,
        scenario.status.name,
        scenario.start_time,
    )

    step_defs = [
        {
            "scenario_id": ctx.db_scenario_id,
            "step_def_id": 0,
            "parent_step_def_id": None,
            "step_order": index + 1,
            "name": step.name,
            "keyword": step.keyword,
            "table_data": step.table,
            "text_data": step.text,
            "filename": step.filename,
            "line": step.line,
        }
        for index, step in enumerate(scenario.all_steps)
    ]
    updated_step_defs = operations.create_step_defs(conn, step_defs)
    for index, step in enumerate(scenario.all_steps):
        step.db_step_def_id = updated_step_defs[index]["step_def_id"]

    logger.debug("Updated behave step objects with step_def_id")


def update_scenario_in_after_scenario(ctx, scenario):
    conn = get_connection()
    total_duration_ms = None
    if hasattr(scenario, "start_time") and scenario.start_time:
        total_duration_ms = int((time.time() - scenario.start_time) * 1000)

    status = "passed"
    error_message = None

    if scenario.status == "failed":
        status = "failed"
        if hasattr(scenario, "exception") and scenario.exception:
            error_message = str(scenario.exception)
    elif scenario.status == "skipped":
        status = "skipped"

    operations.update_scenario(
        conn,
        CONFIG["current_scenario_id"],
        status,
        total_duration_ms,
        error_message,
    )
    logger.debug(
        f"Updated Scenario record {CONFIG['current_scenario_id']} with status {status}"
    )

    CONFIG["current_scenario_id"] = None
    CONFIG["section_stack"] = []
    CONFIG["current_section_id"] = None


def create_step_in_before_step(ctx, step):
    conn = get_connection()

    attempt = step.db_attempt = 1  # modify behave object

    step.db_step_run_id = operations.create_step_run(
        conn,
        step.db_step_def_id,
        attempt,
        step.status.name,  # from behave
        datetime.fromisoformat(step.start_timestamp),
    )
    step.db_step_run_artifact_order = 1  # reset for each step run
    logger.debug(
        f"🗄️ DB: created step run {step.db_step_run_id} for attempt {attempt} of {step.name}"
    )


def update_step_in_after_step(ctx, step):
    conn = get_connection()
    end_time = datetime.fromisoformat(step.start_timestamp) + timedelta(
        seconds=step.duration
    )

    operations.update_step_run(
        conn,
        step.db_step_run_id,
        step.status.name,
        step.duration,
        end_time,
        step.stdout,
    )


def finalize_database_in_after_all(ctx):
    conn = get_connection()
    total_duration_ms = None
    if hasattr(ctx, "start_time") and ctx.start_time:
        total_duration_ms = int((time.time() - ctx.start_time) * 1000)

    status = "passed"
    if hasattr(ctx, "failed") and ctx.failed:
        status = "failed"

    operations.update_cucu_run(
        conn,
        CONFIG["cucu_run_id"],
        status,
        total_duration_ms,
    )
    logger.info(
        f"Updated CucuRun record {CONFIG['cucu_run_id']} with status {status}"
    )


def record_screenshot_artifact(ctx, step, filepath):
    conn = get_connection()
    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
    file_hash = None
    if file_size > 0:
        with open(filepath, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

    artifact_id = operations.create_artifact(
        conn,
        step.db_step_run_id,
        step.db_step_run_artifact_order,
        filepath,
        "screenshot",
        file_size,
        file_hash,
    )

    step.db_step_run_artifact_order += 1
    return artifact_id

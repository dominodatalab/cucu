"""
Database integration with environment hooks.
"""

import time
from datetime import datetime

from cucu import logger
from cucu.config import CONFIG
from cucu.database.connection import get_connection
from cucu.database.operations import (
    create_artifact,
    create_feature,
    create_scenario,
    create_section,
    create_step,
    create_step_post,
    create_step_run,
    update_cucu_run,
    update_feature,
    update_scenario,
    update_step_run,
)


def db_before_all(ctx, start_time):
    timestamp = datetime.fromtimestamp(start_time)
    with get_connection() as conn:
        cucu_run_id = CONFIG["CUCU_RUN_ID"]
        conn.execute(
            """
            UPDATE CucuRun
            SET start_time = ?
            WHERE cucu_run_id = ?
        """,
            [timestamp, cucu_run_id],
        )
        logger.info(conn.query("FROM CucuRun"))


def finalize_database_in_after_all(ctx):
    conn = get_connection()
    # Calculate total duration
    total_duration_ms = None
    if hasattr(ctx, "start_time") and ctx.start_time:
        total_duration_ms = int((time.time() - ctx.start_time) * 1000)

    # Update the CucuRun record
    status = "passed"
    if hasattr(ctx, "failed") and ctx.failed:
        status = "failed"

    update_cucu_run(
        conn,
        ctx.database["cucu_run_id"],
        status,
        total_duration_ms,
    )
    logger.info(
        f"Updated CucuRun record {ctx.database['cucu_run_id']} with status {status}"
    )


def create_feature_in_before_feature(ctx, feature):
    conn = get_connection()
    # Extract feature information
    name = feature.name
    description = feature.description
    filepath = feature.filename
    tags = [tag for tag in feature.tags] if feature.tags else []

    # Create the Feature record
    ctx.database["current_feature_id"] = create_feature(
        conn,
        ctx.database["cucu_run_id"],
        name,
        description,
        filepath,
        tags,
    )
    logger.debug(
        f"Created Feature record with ID {ctx.database['current_feature_id']}"
    )


def update_feature_in_after_feature(ctx, feature):
    conn = get_connection()
    # Calculate total duration
    total_duration_ms = None
    if hasattr(feature, "start_time") and feature.start_time:
        total_duration_ms = int((time.time() - feature.start_time) * 1000)

    # Determine status based on scenario results
    status = "passed"
    if feature.status == "failed":
        status = "failed"
    elif feature.status == "skipped":
        status = "skipped"

    # Update the Feature record
    update_feature(
        conn,
        ctx.database["current_feature_id"],
        status,
        total_duration_ms,
    )
    logger.debug(
        f"Updated Feature record {ctx.database['current_feature_id']} with status {status}"
    )

    # Clear current feature ID
    ctx.database["current_feature_id"] = None


def create_scenario_in_before_scenario(ctx, scenario):
    conn = get_connection()
    # Extract scenario information
    name = scenario.name
    description = getattr(scenario, "description", "")
    tags = [tag for tag in scenario.tags] if scenario.tags else []

    # Create the Scenario record
    ctx.database["current_scenario_id"] = create_scenario(
        conn,
        ctx.database["current_feature_id"],
        name,
        description,
        tags,
    )
    logger.debug(
        f"Created Scenario record with ID {ctx.database['current_scenario_id']}"
    )

    # Reset section stack for new scenario
    ctx.database["section_stack"] = []
    ctx.database["current_section_id"] = None


def update_scenario_in_after_scenario(ctx, scenario):
    conn = get_connection()
    # Calculate total duration
    total_duration_ms = None
    if hasattr(scenario, "start_time") and scenario.start_time:
        total_duration_ms = int((time.time() - scenario.start_time) * 1000)

    # Determine status and error message
    status = "passed"
    error_message = None

    if scenario.status == "failed":
        status = "failed"
        # Extract error information if available
        if hasattr(scenario, "exception") and scenario.exception:
            error_message = str(scenario.exception)
    elif scenario.status == "skipped":
        status = "skipped"

    # Update the Scenario record
    update_scenario(
        conn,
        ctx.database["current_scenario_id"],
        status,
        total_duration_ms,
        error_message,
    )
    logger.debug(
        f"Updated Scenario record {ctx.database['current_scenario_id']} with status {status}"
    )

    # Clear current scenario ID and section stack
    ctx.database["current_scenario_id"] = None
    ctx.database["section_stack"] = []
    ctx.database["current_section_id"] = None


def create_section_in_section_step(ctx, level, text, order_index=None):
    conn = get_connection()
    # Determine parent section based on heading level and current section stack
    parent_section_id = None

    # Reset section stack for levels less than or equal to current level
    # Example: If we have ## (level 2) and we encounter # (level 1),
    # we need to reset all sections of level >= 1
    new_stack = []
    for section_id, section_level in ctx.database["section_stack"]:
        if section_level < level:
            new_stack.append((section_id, section_level))
            parent_section_id = section_id

    ctx.database["section_stack"] = new_stack

    # Create the Section record
    section_id = create_section(
        conn,
        ctx.database["current_scenario_id"],
        text,
        level,
        parent_section_id,
        order_index,
    )

    # Update current section ID and add to stack
    ctx.database["current_section_id"] = section_id
    ctx.database["section_stack"].append((section_id, level))

    logger.debug(f"Created Section record with ID {section_id}, level {level}")
    return section_id


def create_step_in_before_step(ctx, step):
    conn = get_connection()
    # Extract step information
    keyword = step.keyword.strip()
    text = step.name
    step_type = "regular"  # Default type

    # Determine section ID from current section
    section_id = ctx.database.get("current_section_id")

    # Extract file information if available
    file_path = None
    line_number = None
    if hasattr(step, "location") and step.location:
        file_path = step.location.filename
        line_number = step.location.line

    # Create the Step record
    ctx.database["current_step_id"] = create_step(
        conn,
        ctx.database["current_scenario_id"],
        keyword,
        text,
        step_type,
        section_id,
        None,  # parent_step_id
        None,  # level
        step.index,  # order_index
        file_path,
        line_number,
    )
    logger.debug(
        f"Created Step record with ID {ctx.database['current_step_id']}"
    )

    # Create the initial StepRun record
    ctx.database["current_step_run_id"] = create_step_run(
        conn,
        ctx.database["current_step_id"],
        1,  # attempt_number
        True,  # is_final_attempt (assumed true for now)
    )
    logger.debug(
        f"Created StepRun record with ID {ctx.database['current_step_run_id']}"
    )


def update_step_in_after_step(ctx, step):
    conn = get_connection()
    # Calculate duration
    duration_ms = None
    if hasattr(step, "duration") and step.duration is not None:
        duration_ms = int(step.duration * 1000)

    # Determine status and error information
    status = "passed"
    error_message = None
    stack_trace = None

    if step.status == "failed":
        status = "failed"
        # Extract error information if available
        if hasattr(step, "exception") and step.exception:
            error_message = str(step.exception)
            if hasattr(step.exception, "__traceback__"):
                import traceback

                stack_trace = "".join(
                    traceback.format_tb(step.exception.__traceback__)
                )
    elif step.status == "skipped":
        status = "skipped"

    # Update the StepRun record
    update_step_run(
        conn,
        ctx.database["current_step_run_id"],
        status,
        duration_ms,
        error_message,
        stack_trace,
    )
    logger.debug(
        f"Updated StepRun record {ctx.database['current_step_run_id']} with status {status}"
    )

    # Clear current step IDs
    ctx.database["current_step_id"] = None
    ctx.database["current_step_run_id"] = None


def record_screenshot_artifact(ctx, filepath, step_run_id=None):
    conn = get_connection()
    # Get file metadata
    import os

    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0

    # Create a file hash (optional)
    file_hash = None
    if file_size > 0:
        import hashlib

        with open(filepath, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

    # Determine association IDs
    cucu_run_id = ctx.database.get("cucu_run_id")
    feature_id = ctx.database.get("current_feature_id")
    scenario_id = ctx.database.get("current_scenario_id")

    # Use provided step_run_id or current one
    if step_run_id is None:
        step_run_id = ctx.database.get("current_step_run_id")

    # Create the Artifact record
    artifact_id = create_artifact(
        conn,
        filepath,
        "screenshot",
        file_size,
        file_hash,
        {"type": "screenshot"},
        cucu_run_id,
        feature_id,
        scenario_id,
        step_run_id,
    )

    logger.debug(
        f"Created Artifact record with ID {artifact_id} for screenshot {filepath}"
    )

    # Create a StepPost record if this is associated with a step
    if step_run_id:
        step_post_id = create_step_post(
            conn,
            step_run_id,
            "screenshot",
            f"Screenshot saved to {filepath}",
        )
        logger.debug(f"Created StepPost record with ID {step_post_id}")

    return artifact_id

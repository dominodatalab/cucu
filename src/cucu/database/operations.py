"""
🗄️ DB:  for storing and retrieving test execution data.
"""

import json
import time
from typing import Any, Dict, List, Optional, Tuple

import duckdb

from cucu import logger
from cucu.database.schema import create_schema


def execute_with_retry(
    conn: duckdb.DuckDBPyConnection,
    query: str,
    params: Optional[Tuple] = None,
    retry_count: int = 3,
) -> Any:
    """
    Execute a database query with retry logic.

    Args:
        conn: Database connection
        query: SQL query to execute
        params: Query parameters
        retry_count: Number of retry attempts

    Returns:
        Query result
    """
    last_error = None

    for attempt in range(retry_count):
        try:
            if params:
                return conn.execute(query, params)
            else:
                return conn.execute(query)
        except Exception as e:
            last_error = e
            logger.warning(
                f"🗄️ DB: failed (attempt {attempt+1}/{retry_count}): {str(e)}"
            )
            if attempt < retry_count - 1:
                time.sleep(0.5 * (attempt + 1))  # Exponential backoff
            else:
                logger.error(
                    f"🗄️ DB: failed after {retry_count} attempts: {str(e)}"
                )
                raise last_error


def init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    schema_created = create_schema(conn)
    if schema_created:
        logger.info("🗄️ DB: schema created successfully")
        logger.debug(conn.query("show tables"))
        logger.debug(conn.query("show CucuRun"))


def create_cucu_run(
    conn: duckdb.DuckDBPyConnection,
    command_line,
    env_vars,
    system_info,
    status,
    worker_count,
    start_time,
    browser,
    headless,
    results_dir,
) -> int:
    # Create a new CucuRun record
    cucu_run_id = conn.query("select nextval('seq_cucu_run_id')").fetchone()[0]
    conn.execute(
        """
            INSERT INTO CucuRun (
                cucu_run_id,
                command_line,
                env_vars,
                system_info,
                status,
                worker_count,
                start_time,
                browser,
                headless,
                results_dir
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cucu_run_id,
            command_line,
            env_vars,
            system_info,
            status,
            worker_count,
            start_time,
            browser,
            headless,
            results_dir,
        ),
    )
    logger.info(f"🗄️ DB: Starting CucuRun ID: {cucu_run_id}")
    logger.debug(conn.query("from CucuRun"))
    return cucu_run_id


def update_cucu_run(
    conn: duckdb.DuckDBPyConnection,
    cucu_run_id: int,
    status: str,
    total_duration_ms: Optional[int] = None,
) -> bool:
    """
    Update an existing CucuRun record.

    Args:
        conn: Database connection
        cucu_run_id: CucuRun ID to update
        status: New status value
        total_duration_ms: Total duration in milliseconds

    Returns:
        True if the record was updated successfully
    """
    query = """
    UPDATE CucuRun
    SET end_time = CURRENT_TIMESTAMP,
        status = ?,
        total_duration_ms = ?
    WHERE cucu_run_id = ?
    """

    params = (status, total_duration_ms, cucu_run_id)

    execute_with_retry(conn, query, params)
    logger.debug(f"Updated CucuRun record {cucu_run_id} with status {status}")
    return True


def create_feature(
    conn: duckdb.DuckDBPyConnection,
    cucu_run_id: int,
    name: str,
    description: Optional[str],
    filepath: str,
    tags: Optional[List[str]] = None,
) -> int:
    """
    Create a new Feature record.

    Args:
        conn: Database connection
        cucu_run_id: Parent CucuRun ID
        name: Feature name
        description: Feature description
        filepath: Feature file path
        tags: Feature tags

    Returns:
        The ID of the new Feature record
    """
    query = """
    INSERT INTO Feature (
        cucu_run_id, name, description, filepath, tags, start_time, status
    ) VALUES (
        ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'running'
    ) RETURNING feature_id
    """

    tags_str = None
    if tags:
        tags_str = ",".join(tags)

    params = (cucu_run_id, name, description, filepath, tags_str)

    result = execute_with_retry(conn, query, params)
    feature_id = result.fetchone()[0]

    logger.debug(f"Created Feature record with ID {feature_id}")
    return feature_id


def update_feature(
    conn: duckdb.DuckDBPyConnection,
    feature_id: int,
    status: str,
    total_duration_ms: Optional[int] = None,
) -> bool:
    """
    Update an existing Feature record.

    Args:
        conn: Database connection
        feature_id: Feature ID to update
        status: New status value
        total_duration_ms: Total duration in milliseconds

    Returns:
        True if the record was updated successfully
    """
    query = """
    UPDATE Feature
    SET end_time = CURRENT_TIMESTAMP,
        status = ?,
        total_duration_ms = ?
    WHERE feature_id = ?
    """

    params = (status, total_duration_ms, feature_id)

    execute_with_retry(conn, query, params)
    logger.debug(f"Updated Feature record {feature_id} with status {status}")
    return True


def create_scenario(
    conn: duckdb.DuckDBPyConnection,
    feature_id: int,
    name: str,
    description: Optional[str],
    tags: Optional[List[str]] = None,
) -> int:
    """
    Create a new Scenario record.

    Args:
        conn: Database connection
        feature_id: Parent Feature ID
        name: Scenario name
        description: Scenario description
        tags: Scenario tags

    Returns:
        The ID of the new Scenario record
    """
    query = """
    INSERT INTO Scenario (
        feature_id, name, description, tags, start_time, status
    ) VALUES (
        ?, ?, ?, ?, CURRENT_TIMESTAMP, 'running'
    ) RETURNING scenario_id
    """

    tags_str = None
    if tags:
        tags_str = ",".join(tags)

    params = (feature_id, name, description, tags_str)

    result = execute_with_retry(conn, query, params)
    scenario_id = result.fetchone()[0]

    logger.debug(f"Created Scenario record with ID {scenario_id}")
    return scenario_id


def update_scenario(
    conn: duckdb.DuckDBPyConnection,
    scenario_id: int,
    status: str,
    total_duration_ms: Optional[int] = None,
    error_message: Optional[str] = None,
) -> bool:
    """
    Update an existing Scenario record.

    Args:
        conn: Database connection
        scenario_id: Scenario ID to update
        status: New status value
        total_duration_ms: Total duration in milliseconds
        error_message: Error message if failed

    Returns:
        True if the record was updated successfully
    """
    query = """
    UPDATE Scenario
    SET end_time = CURRENT_TIMESTAMP,
        status = ?,
        total_duration_ms = ?,
        error_message = ?
    WHERE scenario_id = ?
    """

    params = (status, total_duration_ms, error_message, scenario_id)

    execute_with_retry(conn, query, params)
    logger.debug(f"Updated Scenario record {scenario_id} with status {status}")
    return True


def create_section(
    conn: duckdb.DuckDBPyConnection,
    scenario_id: int,
    text: str,
    level: int,
    parent_section_id: Optional[int] = None,
    order_index: Optional[int] = None,
) -> int:
    """
    Create a new Section record.

    Args:
        conn: Database connection
        scenario_id: Parent Scenario ID
        text: Section text
        level: Heading level (1-4)
        parent_section_id: Parent Section ID for nested sections
        order_index: Order index within parent

    Returns:
        The ID of the new Section record
    """
    query = """
    INSERT INTO Section (
        scenario_id, parent_section_id, text, level, timestamp, order_index
    ) VALUES (
        ?, ?, ?, ?, CURRENT_TIMESTAMP, ?
    ) RETURNING section_id
    """

    params = (scenario_id, parent_section_id, text, level, order_index)

    result = execute_with_retry(conn, query, params)
    section_id = result.fetchone()[0]

    logger.debug(f"Created Section record with ID {section_id}")
    return section_id


def create_step(
    conn: duckdb.DuckDBPyConnection,
    scenario_id: int,
    keyword: str,
    text: str,
    step_type: str,
    section_id: Optional[int] = None,
    parent_step_id: Optional[int] = None,
    level: Optional[int] = None,
    order_index: Optional[int] = None,
    file_path: Optional[str] = None,
    line_number: Optional[int] = None,
) -> int:
    """
    Create a new Step record.

    Args:
        conn: Database connection
        scenario_id: Parent Scenario ID
        keyword: Step keyword (Given, When, Then, etc.)
        text: Step text
        step_type: Type of step
        section_id: Parent Section ID
        parent_step_id: Parent Step ID for substeps
        level: Step nesting level
        order_index: Order index within parent
        file_path: Source file path
        line_number: Source line number

    Returns:
        The ID of the new Step record
    """
    query = """
    INSERT INTO Step (
        scenario_id, section_id, parent_step_id, keyword, text, level,
        step_type, order_index, created_at, file_path, line_number
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?
    ) RETURNING step_id
    """

    params = (
        scenario_id,
        section_id,
        parent_step_id,
        keyword,
        text,
        level,
        step_type,
        order_index,
        file_path,
        line_number,
    )

    result = execute_with_retry(conn, query, params)
    step_id = result.fetchone()[0]

    logger.debug(f"Created Step record with ID {step_id}")
    return step_id


def create_step_run(
    conn: duckdb.DuckDBPyConnection,
    step_id: int,
    attempt_number: int,
    is_final_attempt: bool = False,
) -> int:
    """
    Create a new StepRun record.

    Args:
        conn: Database connection
        step_id: Parent Step ID
        attempt_number: Attempt number (1-based)
        is_final_attempt: Whether this is the final attempt

    Returns:
        The ID of the new StepRun record
    """
    query = """
    INSERT INTO StepRun (
        step_id, start_time, status, attempt_number, is_final_attempt
    ) VALUES (
        ?, CURRENT_TIMESTAMP, 'running', ?, ?
    ) RETURNING step_run_id
    """

    params = (step_id, attempt_number, is_final_attempt)

    result = execute_with_retry(conn, query, params)
    step_run_id = result.fetchone()[0]

    logger.debug(f"Created StepRun record with ID {step_run_id}")
    return step_run_id


def update_step_run(
    conn: duckdb.DuckDBPyConnection,
    step_run_id: int,
    status: str,
    duration_ms: Optional[int] = None,
    error_message: Optional[str] = None,
    stack_trace: Optional[str] = None,
) -> bool:
    """
    Update an existing StepRun record.

    Args:
        conn: Database connection
        step_run_id: StepRun ID to update
        status: New status value
        duration_ms: Duration in milliseconds
        error_message: Error message if failed
        stack_trace: Stack trace if failed

    Returns:
        True if the record was updated successfully
    """
    query = """
    UPDATE StepRun
    SET end_time = CURRENT_TIMESTAMP,
        status = ?,
        duration_ms = ?,
        error_message = ?,
        stack_trace = ?
    WHERE step_run_id = ?
    """

    params = (status, duration_ms, error_message, stack_trace, step_run_id)

    execute_with_retry(conn, query, params)
    logger.debug(f"Updated StepRun record {step_run_id} with status {status}")
    return True


def create_step_post(
    conn: duckdb.DuckDBPyConnection,
    step_run_id: int,
    action_type: str,
    details: Optional[str] = None,
) -> int:
    """
    Create a new StepPost record.

    Args:
        conn: Database connection
        step_run_id: Parent StepRun ID
        action_type: Type of post-step action
        details: Details about the action

    Returns:
        The ID of the new StepPost record
    """
    query = """
    INSERT INTO StepPost (
        step_run_id, timestamp, action_type, details
    ) VALUES (
        ?, CURRENT_TIMESTAMP, ?, ?
    ) RETURNING step_post_id
    """

    params = (step_run_id, action_type, details)

    result = execute_with_retry(conn, query, params)
    step_post_id = result.fetchone()[0]

    logger.debug(f"Created StepPost record with ID {step_post_id}")
    return step_post_id


def create_scenario_post(
    conn: duckdb.DuckDBPyConnection,
    scenario_id: int,
    action_type: str,
    details: Optional[str] = None,
    status: Optional[str] = None,
) -> int:
    """
    Create a new ScenarioPost record.

    Args:
        conn: Database connection
        scenario_id: Parent Scenario ID
        action_type: Type of post-scenario action
        details: Details about the action
        status: Status of the post-scenario action

    Returns:
        The ID of the new ScenarioPost record
    """
    query = """
    INSERT INTO ScenarioPost (
        scenario_id, timestamp, action_type, details, status
    ) VALUES (
        ?, CURRENT_TIMESTAMP, ?, ?, ?
    ) RETURNING scenario_post_id
    """

    params = (scenario_id, action_type, details, status)

    result = execute_with_retry(conn, query, params)
    scenario_post_id = result.fetchone()[0]

    logger.debug(f"Created ScenarioPost record with ID {scenario_post_id}")
    return scenario_post_id


def create_artifact(
    conn: duckdb.DuckDBPyConnection,
    filepath: str,
    artifact_type: str,
    file_size: int,
    file_hash: Optional[str] = None,
    metadata: Optional[Dict] = None,
    cucu_run_id: Optional[int] = None,
    feature_id: Optional[int] = None,
    scenario_id: Optional[int] = None,
    step_run_id: Optional[int] = None,
    scenario_post_id: Optional[int] = None,
) -> int:
    """
    Create a new Artifact record.

    Args:
        conn: Database connection
        filepath: Path to the artifact file
        artifact_type: Type of artifact (screenshot, log, etc.)
        file_size: Size of the file in bytes
        file_hash: Hash of the file contents
        metadata: Additional metadata about the artifact
        cucu_run_id: Parent CucuRun ID
        feature_id: Parent Feature ID
        scenario_id: Parent Scenario ID
        step_run_id: Parent StepRun ID
        scenario_post_id: Parent ScenarioPost ID

    Returns:
        The ID of the new Artifact record
    """
    query = """
    INSERT INTO Artifact (
        filepath, artifact_type, file_size, file_hash, created_at, metadata,
        cucu_run_id, feature_id, scenario_id, step_run_id, scenario_post_id
    ) VALUES (
        ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?
    ) RETURNING artifact_id
    """

    params = (
        filepath,
        artifact_type,
        file_size,
        file_hash,
        json.dumps(metadata, sort_keys=True),
        cucu_run_id,
        feature_id,
        scenario_id,
        step_run_id,
        scenario_post_id,
    )

    result = execute_with_retry(conn, query, params)
    artifact_id = result.fetchone()[0]

    logger.debug(f"Created Artifact record with ID {artifact_id}")
    return artifact_id

"""
🗄️ DB:  for storing and retrieving test execution data.
"""

import json
import time
from typing import Any, Dict, List, Optional, Tuple

import duckdb

from cucu import logger


def execute_with_retry(
    conn: duckdb.DuckDBPyConnection,
    query: str,
    params: Optional[Tuple] = None,
    retry_count: int = 3,
) -> Any:
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


def create_schema(conn: Optional[duckdb.DuckDBPyConnection] = None) -> bool:
    # Check if tables already exist
    tables_exist = conn.execute(
        """
        SELECT count(*)
        FROM information_schema.tables
        WHERE table_name = 'CucuRun'
        """
    ).fetchone()[0]

    if tables_exist > 0:
        raise RuntimeError(
            "🗄️ DB: Schema already exists. Please delete the database file to recreate it."
        )

    # 1. CucuRun table - master record for each test execution
    conn.execute("""
    CREATE TABLE CucuRun (
        cucu_run_id INTEGER PRIMARY KEY,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        command_line TEXT NOT NULL,
        env_vars TEXT NOT NULL,
        system_info TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'running',
        worker_count INTEGER DEFAULT 1,
        start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        total_duration FLOAT,
        browser TEXT,
        headless BOOLEAN,
        results_dir TEXT
    )
    """)

    # 2. Feature table - maps to a feature file
    conn.execute("""
    CREATE TABLE Feature (
        feature_id INTEGER PRIMARY KEY,
        cucu_run_id INTEGER NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        name TEXT NOT NULL,
        description TEXT,
        filename TEXT NOT NULL,
        tags TEXT,
        status TEXT NOT NULL DEFAULT 'not started',
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        FOREIGN KEY (cucu_run_id) REFERENCES CucuRun(cucu_run_id)
    )
    """)

    # 3. Scenario table - maps to a scenario within a feature file
    conn.execute("""
    CREATE TABLE Scenario (
        scenario_id INTEGER PRIMARY KEY,
        feature_id INTEGER NOT NULL,
        db_created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        db_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        name TEXT NOT NULL,
        description TEXT,
        filename TEXT NOT NULL,
        line_number INTEGER NOT NULL,
        tags TEXT,
        status TEXT NOT NULL DEFAULT 'not started',
        duration FLOAT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        cleanup_log TEXT,
        worker_id TEXT,
        FOREIGN KEY (feature_id) REFERENCES Feature(feature_id)
    )
    """)

    # 4. StepDef table - maps to steps or sections within a scenario
    conn.execute("""
    CREATE TABLE StepDef (
        step_def_id INTEGER PRIMARY KEY,
        scenario_id INTEGER NOT NULL,
        parent_step_def_id INTEGER,
        db_created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        db_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        name TEXT NOT NULL,
        kind TEXT NOT NULL,
        filename TEXT,
        line_number INTEGER,
        section_level INTEGER NOT NULL DEFAULT 0,
        step_order INTEGER NOT NULL,
        step_level INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (scenario_id) REFERENCES Scenario(scenario_id),
        FOREIGN KEY (parent_step_def_id) REFERENCES StepDef(step_def_id)
    )
    """)

    # 5. StepRun table - records each execution attempt of a step
    conn.execute("""
    CREATE TABLE StepRun (
        step_run_id INTEGER PRIMARY KEY,
        step_def_id INTEGER NOT NULL,
        db_created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        db_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        attempt INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'not started',
        started_at TIMESTAMP,
        ended_at TIMESTAMP,
        duration FLOAT,
        debug_log TEXT,
        browser_url TEXT,
        browser_title TEXT,
        browser_tab INTEGER,
        browser_total_tabs INTEGER,
        browser_log TEXT,
        FOREIGN KEY (step_def_id) REFERENCES StepDef(step_def_id)
    )
    """)

    # 6. Artifact table - records file-based outputs
    conn.execute("""
    CREATE TABLE Artifact (
        artifact_id INTEGER PRIMARY KEY,
        step_run_id INTEGER NOT NULL,
        db_created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        db_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        type TEXT NOT NULL,
        mime_type TEXT,
        file_size INTEGER,
        hash TEXT,
        artifact_order INTEGER NOT NULL,
        FOREIGN KEY (step_run_id) REFERENCES StepRun(step_run_id)
    )
    """)

    # Create indexes for performance optimization
    conn.execute(
        "CREATE INDEX idx_feature_cucu_run_id ON Feature(cucu_run_id)"
    )
    conn.execute(
        "CREATE INDEX idx_scenario_feature_id ON Scenario(feature_id)"
    )
    conn.execute(
        "CREATE INDEX idx_stepdef_scenario_id ON StepDef(scenario_id)"
    )
    conn.execute(
        "CREATE INDEX idx_stepdef_parent_id ON StepDef(parent_step_def_id)"
    )
    conn.execute("CREATE INDEX idx_steprun_stepdef_id ON StepRun(step_def_id)")
    conn.execute(
        "CREATE INDEX idx_artifact_step_run_id ON Artifact(step_run_id)"
    )
    conn.execute("CREATE SEQUENCE seq_cucu_run_id START 1; ")
    conn.execute("CREATE SEQUENCE seq_feature_id START 1; ")
    conn.execute("CREATE SEQUENCE seq_scenario_id START 1; ")
    conn.execute("CREATE SEQUENCE seq_parent_step_def_id START 1; ")
    conn.execute("CREATE SEQUENCE seq_step_def_id START 1; ")
    conn.execute("CREATE SEQUENCE seq_step_run_id START 1; ")

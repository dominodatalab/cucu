"""
🗄️ DB:  for storing and retrieving test execution data.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import pandas

from cucu import logger


def _to_timestamp(time_float: float) -> datetime:
    return datetime.fromtimestamp(time_float)


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
        except duckdb.ParserException:
            raise
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
        logger.info(conn.query("show tables"))
        logger.info(conn.query("show CucuRun"))


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
    logger.info(
        conn.query("FROM CucuRun WHERE cucu_run_id = ?", params=[cucu_run_id])
    )
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
    logger.info(f"Updated CucuRun record {cucu_run_id} with status {status}")
    return True


def create_feature(
    conn: duckdb.DuckDBPyConnection,
    cucu_run_id: int,
    name: str,
    description: Optional[str],
    filename: str,
    tags: Optional[List[str]] = None,
) -> int:
    feature_id = conn.query("select nextval('seq_feature_id')").fetchone()[0]

    query = """
    INSERT INTO Feature (
        cucu_run_id, feature_id, name, description, filename, tags, start_time, status
    ) VALUES (
        ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'running'
    )
    """

    tags_str = ",".join(tags)
    params = (cucu_run_id, feature_id, name, description, filename, tags_str)

    result = execute_with_retry(conn, query, params)
    feature_id = result.fetchone()[0]

    logger.info(f"🗄️ DB: Created Feature record with ID {feature_id}")
    logger.info(
        conn.query("FROM Feature WHERE feature_id = ?", params=[feature_id])
    )

    return feature_id


def create_scenario(
    conn: duckdb.DuckDBPyConnection,
    feature_id,
    name,
    filename,
    line,
    tags,
    status,
    start_time,
    worker_id=None,
) -> int:
    scenario_id = conn.query("select nextval('seq_scenario_id')").fetchone()[0]

    query = """
    INSERT INTO Scenario (
        scenario_id,
        feature_id,
        name,
        filename,
        line,
        tags,
        status,
        start_time,
        worker_id
    ) VALUES (
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?
    )
    """

    tags_str = ",".join(tags)

    params = (
        scenario_id,
        feature_id,
        name,
        filename,
        line,
        tags_str,
        status,
        _to_timestamp(start_time),
        worker_id,
    )

    execute_with_retry(conn, query, params)
    logger.info(f"🗄️ DB: Created Scenario record with ID {scenario_id}")
    logger.info(
        conn.query("FROM Scenario WHERE scenario_id = ?", params=[scenario_id])
    )
    return scenario_id


def create_step_defs(conn, step_defs: List[Dict]) -> None:
    for step_def in step_defs:
        step_def["step_def_id"] = conn.query(
            "select nextval('seq_step_def_id')"
        ).fetchone()[0]

    steps_def_df = pandas.DataFrame(step_defs)
    conn.register("steps_def_df", steps_def_df)
    conn.query("INSERT INTO StepDef BY NAME SELECT * FROM steps_def_df")

    step_def_ids = [x["step_def_id"] for x in step_defs]
    logger.info(f"🗄️ DB: Created Step Defs {step_def_ids}")
    logger.info(
        conn.query(
            "FROM StepDef WHERE step_def_id in ?", params=[step_def_ids]
        )
    )
    return step_defs


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
    logger.info(f"Updated Feature record {feature_id} with status {status}")
    return True


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
    logger.info(f"Updated Scenario record {scenario_id} with status {status}")
    return True


def create_step_run(
    conn: duckdb.DuckDBPyConnection,
    step_def_id: int,
    attempt: int,
    status: str,
    start_time: datetime,
) -> int:
    step_run_id = conn.query("select nextval('seq_step_run_id')").fetchone()[0]
    query = """
    INSERT INTO StepRun (
        step_run_id, step_def_id, attempt, status, start_time
    ) VALUES (
        ?, ?, ?, ?, ?
    )
    """
    params = (step_run_id, step_def_id, attempt, status, start_time)
    execute_with_retry(conn, query, params)
    logger.info(f"🗄️ DB: Created StepRun record with ID {step_run_id}")
    logger.info(
        conn.query("FROM StepRun WHERE step_run_id = ?", params=[step_run_id])
    )

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
    logger.info(f"Updated StepRun record {step_run_id} with status {status}")
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

    logger.info(f"Created StepPost record with ID {step_post_id}")
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

    logger.info(f"Created ScenarioPost record with ID {scenario_post_id}")
    return scenario_post_id


def create_artifact(
    conn: duckdb.DuckDBPyConnection,
    filename: str,
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
        filename, artifact_type, file_size, file_hash, created_at, metadata,
        cucu_run_id, feature_id, scenario_id, step_run_id, scenario_post_id
    ) VALUES (
        ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?
    ) RETURNING artifact_id
    """

    params = (
        filename,
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

    logger.info(f"Created Artifact record with ID {artifact_id}")
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
        command_line TEXT NOT NULL,
        env_vars TEXT NOT NULL,
        system_info TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'not_started',
        worker_count INTEGER DEFAULT 1,
        start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        total_duration FLOAT,
        browser TEXT,
        headless BOOLEAN,
        results_dir TEXT,
    )
    """)

    # 2. Feature table - maps to a feature file
    conn.execute("""
    CREATE TABLE Feature (
        feature_id INTEGER PRIMARY KEY,
        cucu_run_id INTEGER NOT NULL,
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
        name TEXT NOT NULL,
        filename TEXT NOT NULL,
        line INTEGER NOT NULL,
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
        step_order INTEGER NOT NULL,
        step_level INTEGER NOT NULL DEFAULT 0,
        section_level INTEGER NOT NULL DEFAULT 0,
        keyword TEXT NOT NULL,
        name TEXT NOT NULL,
        table_data TEXT,
        text_data TEXT,
        filename TEXT,
        line INTEGER,
        FOREIGN KEY (scenario_id) REFERENCES Scenario(scenario_id),
        FOREIGN KEY (parent_step_def_id) REFERENCES StepDef(step_def_id)
    )
    """)

    # 5. StepRun table - records each execution attempt of a step
    conn.execute("""
    CREATE TABLE StepRun (
        step_run_id INTEGER PRIMARY KEY,
        step_def_id INTEGER NOT NULL,
        attempt INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'unset',
        start_time TIMESTAMP,
        end_time TIMESTAMP,
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

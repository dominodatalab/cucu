"""
🗄️ DB:  for storing and retrieving test execution data.
"""

import functools
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import pandas
import portalocker

from cucu import logger
from cucu.config import CONFIG

_path = None
_conn = None
_lock = None


def _init(db_path):
    global _path, _conn, _lock
    _path = db_path
    _lock = portalocker.Lock(Path(db_path).parent / "db_lock")
    _conn = duckdb.connect(db_path)


def get_lock():
    if _lock is None:
        _init(CONFIG["DB_PATH"])

    return _lock


def _to_timestamp(time_float: float) -> datetime:
    return datetime.fromtimestamp(time_float)


def locked(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with get_lock():
            return func(*args, **kwargs)

    return wrapper


@locked
def execute_with_retry(
    query: str,
    params: Optional[Tuple] = None,
    retry_count: int = 3,
) -> Any:
    last_error = None

    for attempt in range(retry_count):
        try:
            if params:
                return _conn.execute(query, params)
            else:
                return _conn.execute(query)
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


@locked
def create_cucu_run(
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
    cucu_run_id = _conn.query("select nextval('seq_cucu_run_id')").fetchone()[
        0
    ]
    _conn.execute(
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
    logger.debug(
        _conn.query("FROM CucuRun WHERE cucu_run_id = ?", params=[cucu_run_id])
    )
    return cucu_run_id


@locked
def start_cucu_run(timestamp, cucu_run_id) -> None:
    _conn.execute(
        """
        UPDATE CucuRun
        SET status = 'running', start_time = ?
        WHERE cucu_run_id = ?
    """,
        [timestamp, cucu_run_id],
    )


@locked
def update_cucu_run(
    cucu_run_id: int,
    status: str,
):
    query = """
    UPDATE CucuRun
    SET status = ?
    WHERE cucu_run_id = ?
    """

    params = (status, cucu_run_id)

    execute_with_retry(query, params)
    logger.info(
        f"🗄️ DB: Updated CucuRun record {cucu_run_id} with status {status}"
    )
    logger.debug(
        _conn.query("FROM CucuRun WHERE cucu_run_id = ?", params=[cucu_run_id])
    )


@locked
def create_feature(
    cucu_run_id: int,
    name: str,
    description: Optional[str],
    filename: str,
    tags: Optional[List[str]] = None,
) -> int:
    feature_id = _conn.query("select nextval('seq_feature_id')").fetchone()[0]

    query = """
    INSERT INTO Feature (
        cucu_run_id, feature_id, name, description, filename, tags, start_time, status
    ) VALUES (
        ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'running'
    )
    """

    tags_str = ",".join(tags)
    params = (cucu_run_id, feature_id, name, description, filename, tags_str)

    result = execute_with_retry(query, params)
    feature_id = result.fetchone()[0]

    logger.info(f"🗄️ DB: Created Feature record with ID {feature_id}")
    logger.debug(
        _conn.query("FROM Feature WHERE feature_id = ?", params=[feature_id])
    )

    return feature_id


@locked
def create_scenario(
    feature_id,
    name,
    filename,
    line,
    tags,
    status,
    start_time,
    worker_id=None,
) -> int:
    scenario_id = _conn.query("select nextval('seq_scenario_id')").fetchone()[
        0
    ]

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

    execute_with_retry(query, params)
    logger.info(f"🗄️ DB: Created Scenario record with ID {scenario_id}")
    logger.debug(
        _conn.query(
            "FROM Scenario WHERE scenario_id = ?", params=[scenario_id]
        )
    )
    return scenario_id


@locked
def create_step_defs(step_defs: List[Dict]) -> None:
    for step_def in step_defs:
        step_def["step_def_id"] = _conn.query(
            "select nextval('seq_step_def_id')"
        ).fetchone()[0]

    steps_def_df = pandas.DataFrame(step_defs)
    _conn.register("steps_def_df", steps_def_df)
    _conn.query("INSERT INTO StepDef BY NAME SELECT * FROM steps_def_df")

    step_def_ids = [x["step_def_id"] for x in step_defs]
    logger.info(f"🗄️ DB: Created Step Defs {step_def_ids}")
    logger.debug(
        _conn.query(
            "FROM StepDef WHERE step_def_id in ?", params=[step_def_ids]
        )
    )
    return step_defs


@locked
def update_feature(
    feature_id: int,
    status: str,
    duration: float,
):
    query = """
        UPDATE Feature
        SET end_time = CURRENT_TIMESTAMP,
            status = ?,
            duration = ?
        WHERE feature_id = ?
    """

    params = (status, duration, feature_id)

    execute_with_retry(query, params)
    logger.info(
        f"🗄️ DB: Updated Feature record {feature_id} with status {status}"
    )
    logger.debug(
        _conn.query("FROM Feature WHERE feature_id = ?", params=[feature_id])
    )


@locked
def update_scenario(
    scenario_id: int,
    status: str,
    duration: float,
):
    query = """
    UPDATE Scenario
    SET status = ?,
        duration = ?
    WHERE scenario_id = ?
    """

    params = [status, duration, scenario_id]

    execute_with_retry(query, params)
    logger.info(
        f"🗄️ DB: Updated Scenario record {scenario_id} with status {status}"
    )
    logger.debug(
        _conn.query(
            "FROM Scenario WHERE scenario_id = ?", params=[scenario_id]
        )
    )


@locked
def create_step_run(
    step_def_id: int,
    attempt: int,
    status: str,
    start_time: datetime,
) -> int:
    step_run_id = _conn.query("select nextval('seq_step_run_id')").fetchone()[
        0
    ]
    query = """
    INSERT INTO StepRun (
        step_run_id, step_def_id, attempt, status, start_time
    ) VALUES (
        ?, ?, ?, ?, ?
    )
    """
    params = (step_run_id, step_def_id, attempt, status, start_time)
    execute_with_retry(query, params)
    logger.debug(f"🗄️ DB: created step run {step_run_id} for attempt {attempt}")
    logger.debug(
        _conn.query("FROM StepRun WHERE step_run_id = ?", params=[step_run_id])
    )

    return step_run_id


@locked
def update_step_run(
    step_run_id: int,
    status: str,
    duration: float,
    end_time: datetime,
    debug_log: str,
) -> bool:
    query = """
    UPDATE StepRun
    SET status = ?,
        duration = ?,
        end_time = ?,
        debug_log = ?,
    WHERE step_run_id = ?
    """

    params = (
        status,
        duration,
        end_time,
        debug_log,
        step_run_id,
    )

    execute_with_retry(query, params)
    logger.info(
        f"🗄️ DB: Updated StepRun record {step_run_id} with status {status}"
    )
    logger.debug(
        _conn.query("FROM StepRun WHERE step_run_id = ?", params=[step_run_id])
    )
    return True


@locked
def create_scenario_post(
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

    result = execute_with_retry(query, params)
    scenario_post_id = result.fetchone()[0]

    logger.info(f"Created ScenarioPost record with ID {scenario_post_id}")
    return scenario_post_id


@locked
def create_artifact(
    step_run_id: int,
    artifact_order: int,
    filepath: str,
    type,
    file_size,
    hash,
) -> int:
    artifact_id = _conn.query("select nextval('seq_artifact_id')").fetchone()[
        0
    ]

    query = """
    INSERT INTO Artifact (
        artifact_id,
        step_run_id,
        artifact_order,
        filepath,
        type,
        file_size,
        hash
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?
    )
    """

    params = (
        artifact_id,
        step_run_id,
        artifact_order,
        filepath,
        type,
        file_size,
        hash,
    )
    execute_with_retry(query, params)

    logger.info(f"🗄️ DB: Created Artifact record with ID {artifact_id}")
    logger.debug(
        _conn.query(
            "FROM Artifact WHERE artifact_id = ?", params=[artifact_id]
        )
    )
    return artifact_id


@locked
def init_schema() -> None:
    tables_exist = _conn.execute(
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
    _conn.execute("""
    CREATE TABLE CucuRun (
        cucu_run_id INTEGER PRIMARY KEY,
        command_line TEXT NOT NULL,
        env_vars TEXT NOT NULL,
        system_info TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'not_started',
        worker_count INTEGER DEFAULT 1,
        duration FLOAT,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        browser TEXT,
        headless BOOLEAN,
        results_dir TEXT,
    )
    """)

    # 2. Feature table - maps to a feature file
    _conn.execute("""
    CREATE TABLE Feature (
        feature_id INTEGER PRIMARY KEY,
        cucu_run_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        filename TEXT NOT NULL,
        tags TEXT,
        status TEXT NOT NULL DEFAULT 'not started',
        duration FLOAT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        FOREIGN KEY (cucu_run_id) REFERENCES CucuRun(cucu_run_id)
    )
    """)

    # 3. Scenario table - maps to a scenario within a feature file
    _conn.execute("""
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
    _conn.execute("""
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
    _conn.execute("""
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
    _conn.execute("""
    CREATE TABLE Artifact (
        artifact_id INTEGER PRIMARY KEY,
        step_run_id INTEGER NOT NULL,
        artifact_order INTEGER NOT NULL,
        filepath TEXT NOT NULL,
        type TEXT NOT NULL,
        file_size INTEGER,
        hash TEXT,
        FOREIGN KEY (step_run_id) REFERENCES StepRun(step_run_id)
    )
    """)

    # Create indexes for performance optimization
    _conn.execute(
        "CREATE INDEX idx_feature_cucu_run_id ON Feature(cucu_run_id)"
    )
    _conn.execute(
        "CREATE INDEX idx_scenario_feature_id ON Scenario(feature_id)"
    )
    _conn.execute(
        "CREATE INDEX idx_stepdef_scenario_id ON StepDef(scenario_id)"
    )
    _conn.execute(
        "CREATE INDEX idx_stepdef_parent_id ON StepDef(parent_step_def_id)"
    )
    _conn.execute(
        "CREATE INDEX idx_steprun_stepdef_id ON StepRun(step_def_id)"
    )
    _conn.execute(
        "CREATE INDEX idx_artifact_step_run_id ON Artifact(step_run_id)"
    )
    _conn.execute("CREATE SEQUENCE seq_cucu_run_id START 1; ")
    _conn.execute("CREATE SEQUENCE seq_feature_id START 1; ")
    _conn.execute("CREATE SEQUENCE seq_scenario_id START 1; ")
    _conn.execute("CREATE SEQUENCE seq_parent_step_def_id START 1; ")
    _conn.execute("CREATE SEQUENCE seq_step_def_id START 1; ")
    _conn.execute("CREATE SEQUENCE seq_step_run_id START 1; ")
    _conn.execute("CREATE SEQUENCE seq_artifact_id START 1; ")

    logger.info("🗄️ DB: schema created successfully")
    logger.debug(_conn.query("show tables"))
    logger.debug(_conn.query("show CucuRun"))

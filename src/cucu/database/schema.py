"""
Database schema creation and management.
"""

from typing import Optional

import duckdb

from cucu import logger


def create_schema(conn: Optional[duckdb.DuckDBPyConnection] = None) -> bool:
    """
    Create the database schema if it doesn't exist.

    Args:
        conn: Optional database connection to use

    Returns:
        True if the schema was created, False if it already existed
    """
    from .connection import get_connection

    if conn is None:
        conn = get_connection()

    if conn is None:
        return False

    # Check if tables already exist
    tables_exist = conn.execute(
        """
        SELECT count(*) 
        FROM information_schema.tables 
        WHERE table_name = 'CucuRun'
        """
    ).fetchone()[0]

    if tables_exist > 0:
        logger.debug("🗄️ DB: schema already exists")
        return False

    # Create tables with proper relationships

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

    return True

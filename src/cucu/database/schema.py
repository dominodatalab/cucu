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

    logger.info("Creating database schema")

    # Check if tables already exist
    tables_exist = conn.execute(
        """
        SELECT count(*) 
        FROM information_schema.tables 
        WHERE table_name = 'CucuRun'
        """
    ).fetchone()[0]

    if tables_exist > 0:
        logger.debug("Database schema already exists")
        return False

    # Create tables with proper relationships

    # 1. CucuRun table - master record for each test execution
    conn.execute("""
    CREATE TABLE CucuRun (
        cucu_run_id INTEGER PRIMARY KEY,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        command_args TEXT,
        browser TEXT,
        environment_vars TEXT,
        worker_count INTEGER,
        headless BOOLEAN,
        results_dir TEXT,
        status TEXT,
        total_duration_ms INTEGER,
        system_info TEXT
    )
    """)

    # 2. Feature table - maps to a feature file
    conn.execute("""
    CREATE TABLE Feature (
        feature_id INTEGER PRIMARY KEY,
        cucu_run_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        filepath TEXT NOT NULL,
        tags TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        status TEXT,
        total_duration_ms INTEGER,
        FOREIGN KEY (cucu_run_id) REFERENCES CucuRun(cucu_run_id) ON DELETE CASCADE
    )
    """)

    # 3. Scenario table - maps to a scenario within a feature file
    conn.execute("""
    CREATE TABLE Scenario (
        scenario_id INTEGER PRIMARY KEY,
        feature_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        tags TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        status TEXT,
        total_duration_ms INTEGER,
        error_message TEXT,
        FOREIGN KEY (feature_id) REFERENCES Feature(feature_id) ON DELETE CASCADE
    )
    """)

    # 4. ScenarioPost table - records post-scenario activities
    conn.execute("""
    CREATE TABLE ScenarioPost (
        scenario_post_id INTEGER PRIMARY KEY,
        scenario_id INTEGER NOT NULL,
        timestamp TIMESTAMP,
        action_type TEXT,
        details TEXT,
        status TEXT,
        FOREIGN KEY (scenario_id) REFERENCES Scenario(scenario_id) ON DELETE CASCADE
    )
    """)

    # 5. Section table - maps to section steps that organize test steps
    conn.execute("""
    CREATE TABLE Section (
        section_id INTEGER PRIMARY KEY,
        scenario_id INTEGER NOT NULL,
        parent_section_id INTEGER,
        text TEXT NOT NULL,
        level INTEGER,
        timestamp TIMESTAMP,
        order_index INTEGER,
        FOREIGN KEY (scenario_id) REFERENCES Scenario(scenario_id) ON DELETE CASCADE,
        FOREIGN KEY (parent_section_id) REFERENCES Section(section_id) ON DELETE CASCADE
    )
    """)

    # 6. Step table - maps to individual test steps
    conn.execute("""
    CREATE TABLE Step (
        step_id INTEGER PRIMARY KEY,
        scenario_id INTEGER NOT NULL,
        section_id INTEGER,
        parent_step_id INTEGER,
        keyword TEXT,
        text TEXT NOT NULL,
        level INTEGER,
        step_type TEXT,
        order_index INTEGER,
        created_at TIMESTAMP,
        file_path TEXT,
        line_number INTEGER,
        FOREIGN KEY (scenario_id) REFERENCES Scenario(scenario_id) ON DELETE CASCADE,
        FOREIGN KEY (section_id) REFERENCES Section(section_id) ON DELETE CASCADE,
        FOREIGN KEY (parent_step_id) REFERENCES Step(step_id) ON DELETE CASCADE
    )
    """)

    # 7. StepRun table - records each execution attempt of a step
    conn.execute("""
    CREATE TABLE StepRun (
        step_run_id INTEGER PRIMARY KEY,
        step_id INTEGER NOT NULL,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        status TEXT,
        duration_ms INTEGER,
        attempt_number INTEGER,
        error_message TEXT,
        stack_trace TEXT,
        is_final_attempt BOOLEAN,
        FOREIGN KEY (step_id) REFERENCES Step(step_id) ON DELETE CASCADE
    )
    """)

    # 8. StepPost table - records post-step activities
    conn.execute("""
    CREATE TABLE StepPost (
        step_post_id INTEGER PRIMARY KEY,
        step_run_id INTEGER NOT NULL,
        timestamp TIMESTAMP,
        action_type TEXT,
        details TEXT,
        FOREIGN KEY (step_run_id) REFERENCES StepRun(step_run_id) ON DELETE CASCADE
    )
    """)

    # 9. Artifact table - records file-based outputs
    conn.execute("""
    CREATE TABLE Artifact (
        artifact_id INTEGER PRIMARY KEY,
        cucu_run_id INTEGER,
        feature_id INTEGER,
        scenario_id INTEGER,
        step_run_id INTEGER,
        scenario_post_id INTEGER,
        filepath TEXT NOT NULL,
        artifact_type TEXT,
        file_size INTEGER,
        file_hash TEXT,
        created_at TIMESTAMP,
        metadata TEXT,
        FOREIGN KEY (cucu_run_id) REFERENCES CucuRun(cucu_run_id) ON DELETE CASCADE,
        FOREIGN KEY (feature_id) REFERENCES Feature(feature_id) ON DELETE CASCADE,
        FOREIGN KEY (scenario_id) REFERENCES Scenario(scenario_id) ON DELETE CASCADE,
        FOREIGN KEY (step_run_id) REFERENCES StepRun(step_run_id) ON DELETE CASCADE,
        FOREIGN KEY (scenario_post_id) REFERENCES ScenarioPost(scenario_post_id) ON DELETE CASCADE
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
        "CREATE INDEX idx_scenario_post_scenario_id ON ScenarioPost(scenario_id)"
    )
    conn.execute(
        "CREATE INDEX idx_section_scenario_id ON Section(scenario_id)"
    )
    conn.execute(
        "CREATE INDEX idx_section_parent_section_id ON Section(parent_section_id)"
    )
    conn.execute("CREATE INDEX idx_step_scenario_id ON Step(scenario_id)")
    conn.execute("CREATE INDEX idx_step_section_id ON Step(section_id)")
    conn.execute(
        "CREATE INDEX idx_step_parent_step_id ON Step(parent_step_id)"
    )
    conn.execute("CREATE INDEX idx_step_run_step_id ON StepRun(step_id)")
    conn.execute(
        "CREATE INDEX idx_step_post_step_run_id ON StepPost(step_run_id)"
    )
    conn.execute(
        "CREATE INDEX idx_artifact_step_run_id ON Artifact(step_run_id)"
    )
    conn.execute(
        "CREATE INDEX idx_artifact_scenario_id ON Artifact(scenario_id)"
    )
    conn.execute(
        "CREATE INDEX idx_artifact_feature_id ON Artifact(feature_id)"
    )
    conn.execute(
        "CREATE INDEX idx_artifact_cucu_run_id ON Artifact(cucu_run_id)"
    )

    logger.info("Database schema created successfully")
    return True

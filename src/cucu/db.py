"""
Database creation and management utilities for cucu.
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from cucu.config import CONFIG


def create_run_database(results_dir):
    """
    Create a run database with run details.

    Args:
        results_dir (str): The results directory path

    Returns:
        str: The database filepath
    """
    results_path = Path(results_dir)

    worker_run_id = CONFIG["WORKER_RUN_ID"]
    cucu_run_id = CONFIG["CUCU_RUN_ID"]
    db_filepath = results_path / f"run_{cucu_run_id}_{worker_run_id}.db"

    run_details = {
        "cucu_run_id": cucu_run_id,
        "worker_run_id": worker_run_id,
        "full_arguments": sys.argv,
        "date": datetime.now().isoformat(),
    }

    _create_run_database_table(db_filepath, run_details)

    return str(db_filepath)


def record_feature(feature):
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO features (feature_run_id, worker_run_id, name, filename, description, tags, start_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                feature.feature_run_id,
                CONFIG["WORKER_RUN_ID"],
                feature.name,
                feature.filename,
                "\n".join(feature.description)
                if isinstance(feature.description, list)
                else str(feature.description),
                " ".join(feature.tags),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()


def record_scenario(ctx):
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO scenarios (scenario_run_id, feature_run_id, name, seq, tags, start_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                ctx.scenario.scenario_run_id,
                ctx.scenario.feature.feature_run_id,
                ctx.scenario.name,
                ctx.scenario_index,
                " ".join(ctx.scenario.tags),
                ctx.scenario.start_at,
            ),
        )

        conn.commit()


def start_step_record(ctx, step):
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO steps (step_run_id, scenario_run_id, seq, keyword, name, location, is_substep, start_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                step.step_run_id,
                ctx.scenario.scenario_run_id,
                ctx.step_index + 1,
                step.keyword,
                step.name,
                str(step.location),
                step.has_substeps,
                step.start_at,
            ),
        )

        conn.commit()


def finish_step_record(step, duration):
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE steps
            SET status = ?, duration = ?, end_at = ?, debug_output = ?, browser_logs = ?, browser_info = ?
            WHERE step_run_id = ?
        """,
            (
                step.status.name,
                duration,
                step.end_at,
                step.debug_output,
                step.browser_logs,
                step.browser_info,
                step.step_run_id,
            ),
        )

        conn.commit()


def finish_scenario_record(scenario):
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    start_dt = datetime.fromisoformat(scenario.start_at)
    end_dt = datetime.fromisoformat(scenario.end_at)
    duration = (end_dt - start_dt).total_seconds()

    scenario_logs_dir = CONFIG.get("SCENARIO_LOGS_DIR")
    if not scenario_logs_dir or not Path(scenario_logs_dir).exists():
        log_files_json = "[]"
    else:
        logs_path = Path(scenario_logs_dir)
        log_files = [
            str(file.relative_to(logs_path))
            for file in logs_path.rglob("*")
            if file.is_file()
        ]
        log_files_json = json.dumps(sorted(log_files))

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE scenarios
            SET status = ?, duration = ?, end_at = ?, log_files = ?, cucu_config = ?
            WHERE scenario_run_id = ?
        """,
            (
                scenario.status.name,
                duration,
                scenario.end_at,
                log_files_json,
                scenario.cucu_config_json,
                scenario.scenario_run_id,
            ),
        )

        conn.commit()


def finish_feature_record(feature):
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE features
            SET end_at = ?
            WHERE feature_run_id = ?
        """,
            (
                datetime.now().isoformat(),
                feature.feature_run_id,
            ),
        )

        conn.commit()


def finish_worker_record():
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE workers
            SET end_at = ?
            WHERE worker_run_id = ?
        """,
            (
                datetime.now().isoformat(),
                CONFIG["WORKER_RUN_ID"],
            ),
        )

        conn.commit()


def _create_run_database_table(db_filepath, run_details):
    with sqlite3.connect(db_filepath) as conn:
        _create_database_schema(conn)
        
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO cucu_run (cucu_run_id, full_arguments, date, start_at)
            VALUES (?, ?, ?, ?)
        """,
            (
                run_details["cucu_run_id"],
                json.dumps(run_details["full_arguments"]),
                run_details["date"],
                run_details["date"],
            ),
        )

        cursor.execute(
            """
            INSERT INTO workers (worker_run_id, cucu_run_id, start_at)
            VALUES (?, ?, ?)
        """,
            (
                run_details["worker_run_id"],
                run_details["cucu_run_id"],
                run_details["date"],
            ),
        )

        conn.commit()


def _create_database_schema(conn):
    """Create all database tables and views in a single method."""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cucu_run (
            cucu_run_id TEXT PRIMARY KEY,
            full_arguments TEXT,
            date TEXT,
            start_at TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            worker_run_id TEXT PRIMARY KEY,
            cucu_run_id TEXT,
            start_at TIMESTAMP,
            end_at TIMESTAMP,
            FOREIGN KEY (cucu_run_id) REFERENCES cucu_run (cucu_run_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS features (
            feature_run_id TEXT PRIMARY KEY,
            worker_run_id TEXT,
            name TEXT,
            filename TEXT,
            description TEXT,
            tags TEXT,
            start_at TIMESTAMP,
            end_at TIMESTAMP,
            FOREIGN KEY (worker_run_id) REFERENCES workers (worker_run_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            scenario_run_id TEXT PRIMARY KEY,
            feature_run_id TEXT,
            name TEXT,
            seq INTEGER,
            tags TEXT,
            status TEXT,
            duration REAL,
            start_at TIMESTAMP,
            end_at TIMESTAMP,
            log_files JSON,
            cucu_config JSON,
            FOREIGN KEY (feature_run_id) REFERENCES features (feature_run_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            step_run_id TEXT PRIMARY KEY,
            scenario_run_id TEXT,
            seq INTEGER,
            keyword TEXT,
            name TEXT,
            location TEXT,
            is_substep BOOLEAN,
            status TEXT,
            duration REAL,
            start_at TIMESTAMP,
            end_at TIMESTAMP,
            debug_output TEXT,
            browser_logs TEXT,
            browser_info JSON,
            FOREIGN KEY (scenario_run_id) REFERENCES scenarios (scenario_run_id)
        )
    """)
    
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS flat AS
        SELECT
            w.cucu_run_id,
            s.start_at,
            s.duration,
            f.name AS feature_name,
            s.name AS scenario_name,
            f.tags || ' ' || s.tags AS tags,
            s.log_files
        FROM scenarios s
        JOIN features f ON s.feature_run_id = f.feature_run_id
        JOIN workers w ON f.worker_run_id = w.worker_run_id
    """)
    
    conn.commit()

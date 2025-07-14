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
    create_flat_view(db_filepath)

    return str(db_filepath)


def record_feature(feature):
    """
    Record a feature in the database.

    Args:
        feature: The feature object containing name, filename, and other details
    """
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    if not db_filepath:
        return

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

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
                "\n".join(getattr(feature, "description", []))
                if hasattr(feature, "description")
                and isinstance(feature.description, list)
                else str(getattr(feature, "description", "")),
                " ".join(getattr(feature, "tags", [])),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()


def record_scenario(ctx):
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    if not db_filepath:
        return

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

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
                FOREIGN KEY (feature_run_id) REFERENCES features (feature_run_id)
            )
        """)

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
    """
    Start recording a step in the database.

    Args:
        ctx: The context object containing step_index
        step: The step object containing name and other details
    """
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    if not db_filepath:
        return

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

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
                FOREIGN KEY (scenario_run_id) REFERENCES scenarios (scenario_run_id)
            )
        """)

        cursor.execute(
            """
            INSERT INTO steps (step_run_id, scenario_run_id, seq, keyword, name, location, is_substep, start_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                step.step_run_id,
                ctx.scenario.scenario_run_id,
                ctx.step_index + 1,  # Convert 0-based to 1-based index
                getattr(step, "keyword", ""),
                step.name,
                str(getattr(step, "location", "")),
                getattr(step, "has_substeps", False),
                step.start_at,
            ),
        )

        conn.commit()


def finish_step_record(step, duration):
    """
    Finish recording a step in the database by updating status, duration, and end_at.

    Args:
        step: The step object containing step_run_id, status and other details
        duration: The step duration in seconds
    """
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    if not db_filepath:
        return

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE steps
            SET status = ?, duration = ?, end_at = ?
            WHERE step_run_id = ?
        """,
            (
                step.status.name,
                duration,
                step.end_at,
                step.step_run_id,
            ),
        )

        conn.commit()


def finish_scenario_record(scenario):
    """
    Finish recording a scenario in the database by updating status, duration, and end_at.

    Args:
        scenario: The scenario object containing scenario_run_id, status and other details
    """
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    if not db_filepath:
        return

    # calculate duration from ISO timestamps
    start_dt = datetime.fromisoformat(scenario.start_at)
    end_dt = datetime.fromisoformat(scenario.end_at)
    duration = (end_dt - start_dt).total_seconds()

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE scenarios
            SET status = ?, duration = ?, end_at = ?
            WHERE scenario_run_id = ?
        """,
            (
                scenario.status.name,
                duration,
                scenario.end_at,
                scenario.scenario_run_id,
            ),
        )

        conn.commit()


def finish_feature_record(feature):
    """
    Finish recording a feature in the database by updating end_at timestamp.

    Args:
        feature: The feature object containing feature_run_id and other details
    """
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    if not db_filepath:
        return

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
    """
    Finish recording a worker in the database by updating end_at timestamp.
    """
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    if not db_filepath:
        return

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
    """Create a run database with run details using unified table structure."""
    with sqlite3.connect(db_filepath) as conn:
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


def create_flat_view(db_filepath):
    """
    Create a flat view that combines data from cucu_run, features, and scenarios tables.

    The view provides the following columns:
    - cucu_run_id: From the cucu_run table
    - start_at: Scenario start timestamp
    - duration: Scenario duration in seconds
    - feature_name: Name of the feature
    - scenario_name: Name of the scenario
    - tags: Combined tags from feature and scenario

    Args:
        db_filepath (str): The database filepath
    """
    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE VIEW IF NOT EXISTS flat AS
            SELECT 
                w.cucu_run_id,
                s.start_at,
                s.duration,
                f.name AS feature_name,
                s.name AS scenario_name,
                f.tags || ' ' || s.tags AS tags
            FROM scenarios s
            JOIN features f ON s.feature_run_id = f.feature_run_id
            JOIN workers w ON f.worker_run_id = w.worker_run_id
        """)

        conn.commit()

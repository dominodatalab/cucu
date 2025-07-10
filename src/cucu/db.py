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
    """
    Record a feature in the database.

    Args:
        feature: The feature object containing name, filename, and other details
    """
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    if not db_filepath:
        return

    feature_run_id = CONFIG["FEATURE_RUN_ID"]

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        # Create features table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS features (
                feature_run_id TEXT PRIMARY KEY,
                worker_run_id TEXT,
                name TEXT,
                filename TEXT,
                started_at TIMESTAMP,
                FOREIGN KEY (worker_run_id) REFERENCES workers (worker_run_id)
            )
        """)

        cursor.execute(
            """
            INSERT INTO features (feature_run_id, worker_run_id, name, filename, started_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                feature_run_id,
                CONFIG["WORKER_RUN_ID"],
                feature.name,
                feature.filename,
                datetime.now().isoformat(),
            ),
        )

        conn.commit()


def record_scenario(scenario):
    """
    Record a scenario in the database.

    Args:
        scenario: The scenario object containing name and other details
    """
    db_filepath = CONFIG.get("RUN_DB_FILEPATH")
    if not db_filepath:
        return

    scenario_run_id = CONFIG["SCENARIO_RUN_ID"]

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        # Create scenarios table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenarios (
                scenario_run_id TEXT PRIMARY KEY,
                feature_run_id TEXT,
                name TEXT,
                started_at TIMESTAMP,
                FOREIGN KEY (feature_run_id) REFERENCES features (feature_run_id)
            )
        """)

        cursor.execute(
            """
            INSERT INTO scenarios (scenario_run_id, feature_run_id, name, started_at)
            VALUES (?, ?, ?, ?)
        """,
            (
                scenario_run_id,
                CONFIG.get("FEATURE_RUN_ID"),
                scenario.name,
                datetime.now().isoformat(),
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
                started_at TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                worker_run_id TEXT PRIMARY KEY,
                cucu_run_id TEXT,
                started_at TIMESTAMP,
                FOREIGN KEY (cucu_run_id) REFERENCES cucu_run (cucu_run_id)
            )
        """)

        cursor.execute(
            """
            INSERT INTO cucu_run (cucu_run_id, full_arguments, date, started_at)
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
            INSERT INTO workers (worker_run_id, cucu_run_id, started_at)
            VALUES (?, ?, ?)
        """,
            (
                run_details["worker_run_id"],
                run_details["cucu_run_id"],
                run_details["date"],
            ),
        )

        conn.commit()

"""
Database creation and management utilities for cucu.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from cucu.config import CONFIG
from cucu.utils import generate_short_id


def create_run_database(results_dir):
    """
    Create a run database with run details.

    Args:
        results_dir (str): The results directory path

    Returns:
        str: The database filepath
    """
    results_path = Path(results_dir)

    # Get or create cucu run ID
    cucu_run_id = CONFIG.get("CUCU_RUN_ID")
    if not cucu_run_id:
        CONFIG["CUCU_RUN_ID"] = cucu_run_id = generate_short_id()

    # Generate worker run ID
    worker_run_id = generate_short_id()
    CONFIG["WORKER_RUN_ID"] = worker_run_id

    # Create database filepath
    db_filepath = results_path / f"run_{cucu_run_id}_{worker_run_id}.db"

    run_details = {
        "cucu_run_id": cucu_run_id,
        "worker_run_id": worker_run_id,
        "full_arguments": sys.argv,
        "env": _get_env_values(),
        "date": datetime.now().isoformat(),
    }

    _create_run_database_table(db_filepath, run_details)

    return str(db_filepath)


def _get_env_values():
    """Get environment values based on configuration."""
    return (
        dict(os.environ)
        if CONFIG["CUCU_RECORD_ENV_VARS"]
        else "To enable use the --record-env-vars flag"
    )


def _create_run_database_table(db_filepath, run_details):
    """Create a run database with run details using unified table structure."""
    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cucu_run_id TEXT,
                worker_run_id TEXT,
                full_arguments TEXT,
                env TEXT,
                date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute(
            """
            INSERT INTO run_details (cucu_run_id, worker_run_id, full_arguments, env, date)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                run_details["cucu_run_id"],
                run_details["worker_run_id"],
                json.dumps(run_details["full_arguments"]),
                json.dumps(run_details["env"])
                if isinstance(run_details["env"], dict)
                else run_details["env"],
                run_details["date"],
            ),
        )

        conn.commit()

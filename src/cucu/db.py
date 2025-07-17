"""
Database creation and management utilities for cucu.
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from cucu.config import CONFIG


def record_cucu_run():
    worker_run_id = CONFIG["WORKER_RUN_ID"]
    cucu_run_id = CONFIG["CUCU_RUN_ID"]
    db_filepath = CONFIG["RUN_DB_PATH"]

    run_details = {
        "cucu_run_id": cucu_run_id,
        "worker_run_id": worker_run_id,
        "full_arguments": sys.argv,
        "date": datetime.now().isoformat(),
    }

    with sqlite3.connect(db_filepath) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO cucu_run (cucu_run_id, full_arguments, date, start_at)
            VALUES (?, ?, ?, ?)
        """,
            (
                cucu_run_id,
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

    return str(db_filepath)


def record_feature(feature):
    db_filepath = CONFIG["RUN_DB_PATH"]
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
    db_filepath = CONFIG["RUN_DB_PATH"]
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
    db_filepath = CONFIG["RUN_DB_PATH"]
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
    db_filepath = CONFIG["RUN_DB_PATH"]
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
    db_filepath = CONFIG["RUN_DB_PATH"]
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
    db_filepath = CONFIG["RUN_DB_PATH"]
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
    db_filepath = CONFIG["RUN_DB_PATH"]
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


def create_database_file(db_filepath):
    with sqlite3.connect(db_filepath) as conn:
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


def consolidate_database_files(results_dir):
    results_path = Path(results_dir)
    target_db_path = results_path / "run.db"

    db_files = [
        db for db in results_path.glob("**/*.db") if db.name != "run.db"
    ]

    if not target_db_path.exists() and db_files:
        create_database_file(target_db_path)

    tables_to_copy = ["cucu_run", "workers", "features", "scenarios", "steps"]

    with sqlite3.connect(target_db_path) as target_conn:
        target_cursor = target_conn.cursor()

        for db_file in db_files:
            with sqlite3.connect(db_file) as source_conn:
                source_cursor = source_conn.cursor()

                for table_name in tables_to_copy:
                    source_cursor.execute(f"SELECT * FROM {table_name}")
                    rows = source_cursor.fetchall()

                    source_cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in source_cursor.fetchall()]
                    placeholders = ",".join(["?" for _ in columns])

                    target_cursor.executemany(
                        f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})",
                        rows,
                    )
                    target_conn.commit()

            db_file.unlink()

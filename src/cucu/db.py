"""
Database creation and management utilities for cucu.
"""

import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from peewee import (
    BooleanField,
    DateTimeField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)
from playhouse.sqlite_ext import JSONField, SqliteExtDatabase
from tenacity import RetryError

from cucu import logger as cucu_logger
from cucu.config import CONFIG

db_filepath = CONFIG["RUN_DB_PATH"]
db = SqliteExtDatabase(db_filepath)

logger = logging.getLogger("peewee")
logger.setLevel(logging.WARNING)  # Only show warnings and errors


class BaseModel(Model):
    class Meta:
        database = db


class cucu_run(BaseModel):
    cucu_run_id = TextField(primary_key=True)
    full_arguments = JSONField()
    filepath = TextField()
    start_at = DateTimeField()
    end_at = DateTimeField(null=True)
    db_path = TextField(null=True)
    run_info = JSONField(null=True)


class worker(BaseModel):
    worker_run_id = TextField(primary_key=True)
    cucu_run = ForeignKeyField(
        cucu_run,
        backref="workers",
        column_name="cucu_run_id",
        null=True,
    )
    parent_id = ForeignKeyField(
        "self",
        field="worker_run_id",
        backref="child_workers",
        column_name="parent_run_id",
        null=True,
    )
    start_at = DateTimeField()
    end_at = DateTimeField(null=True)
    custom_data = JSONField(null=True)


class feature(BaseModel):
    feature_run_id = TextField(primary_key=True)
    worker = ForeignKeyField(
        worker,
        backref="features",
        column_name="worker_run_id",
    )
    name = TextField()
    status = TextField(null=True)
    start_at = DateTimeField()
    end_at = DateTimeField(null=True)
    custom_data = JSONField(null=True)
    tags = JSONField()
    filename = TextField()
    description = TextField()


class scenario(BaseModel):
    scenario_run_id = TextField(primary_key=True)
    feature = ForeignKeyField(
        feature,
        backref="scenarios",
        column_name="feature_run_id",
    )
    name = TextField()
    seq = FloatField(null=True)
    status = TextField(null=True)
    duration = FloatField(null=True)
    start_at = DateTimeField(null=True)
    end_at = DateTimeField(null=True)
    tags = JSONField()
    custom_data = JSONField(null=True)
    browser_info = JSONField(null=True)
    cucu_config = JSONField(null=True)
    line_number = IntegerField()
    log_files = JSONField(null=True)


class step(BaseModel):
    step_run_id = TextField(primary_key=True)
    scenario = ForeignKeyField(
        scenario,
        backref="steps",
        column_name="scenario_run_id",
    )
    section_level = IntegerField(null=True)
    seq = IntegerField()
    parent_seq = IntegerField(null=True)
    is_substep = BooleanField(null=True)  # info available after step ends
    has_substeps = BooleanField()
    keyword = TextField()
    name = TextField()
    status = TextField(null=True)
    duration = FloatField(null=True)
    start_at = DateTimeField(null=True)
    end_at = DateTimeField(null=True)
    stdout = JSONField()
    stderr = JSONField()
    error_message = JSONField(null=True)
    exception = JSONField(null=True)
    debug_output = TextField()
    browser_info = JSONField()
    text = JSONField(null=True)
    table_data = JSONField(null=True)
    location = TextField()
    browser_logs = TextField()
    screenshots = JSONField(null=True)


def record_cucu_run():
    filepath = CONFIG["CUCU_FILEPATH"]
    cucu_run_id_val = CONFIG["CUCU_RUN_ID"]
    worker_run_id = CONFIG["WORKER_RUN_ID"]

    db.connect(reuse_if_open=True)
    start_at = datetime.now().isoformat()
    cucu_run.create(
        cucu_run_id=cucu_run_id_val,
        full_arguments=sys.argv,
        filepath=filepath,
        start_at=start_at,
    )

    parent_id = (
        CONFIG.get("WORKER_PARENT_ID")
        if CONFIG.get("WORKER_PARENT_ID") != worker_run_id
        else None
    )
    worker.create(
        worker_run_id=worker_run_id,
        cucu_run_id=cucu_run_id_val,
        parent_id=parent_id,
        start_at=datetime.now().isoformat(),
    )

    return str(db_filepath)


def record_feature(feature_obj):
    db.connect(reuse_if_open=True)
    feature.create(
        feature_run_id=feature_obj.feature_run_id,
        worker=CONFIG["WORKER_RUN_ID"],
        name=feature_obj.name,
        filename=feature_obj.filename,
        description="\n".join(feature_obj.description)
        if isinstance(feature_obj.description, list)
        else str(feature_obj.description),
        tags=feature_obj.tags,
        start_at=datetime.now().isoformat(),
    )


def record_scenario(scenario_obj):
    db.connect(reuse_if_open=True)
    scenario.create(
        scenario_run_id=scenario_obj.scenario_run_id,
        feature_run_id=scenario_obj.feature.feature_run_id,
        name=scenario_obj.name,
        line_number=scenario_obj.line,
        seq=scenario_obj.seq,
        tags=scenario_obj.tags,
        start_at=getattr(scenario_obj, "start_at", None),
    )


def start_step_record(step_obj, scenario_run_id):
    db.connect(reuse_if_open=True)

    table = None
    if step_obj.table:
        table = {
            "headings": step_obj.table.headings,
            "rows": [list(row) for row in step_obj.table.rows],
        }

    step.create(
        step_run_id=step_obj.step_run_id,
        scenario_run_id=scenario_run_id,
        seq=getattr(step_obj, "seq", -1),
        keyword=step_obj.keyword,
        name=step_obj.name,
        status=step_obj.status.name,
        text=step_obj.text.splitlines() if step_obj.text else [],
        table_data=table,
        location=str(step_obj.location),
        is_substep=getattr(step_obj, "is_substep", False),
        has_substeps=getattr(step_obj, "has_substeps", False),
        section_level=getattr(step_obj, "section_level", None),
        browser_info="",
        browser_logs="",
        debug_output="",
        stderr=[],
        stdout=[],
    )


def finish_step_record(step_obj, duration):
    db.connect(reuse_if_open=True)
    screenshot_infos = []
    if hasattr(step_obj, "screenshots") and step_obj.screenshots:
        for screenshot in step_obj.screenshots:
            screenshot_info = {
                "step_name": screenshot.get("step_name"),
                "label": screenshot.get("label"),
                "location": screenshot.get("location"),
                "size": screenshot.get("size"),
                "filepath": screenshot.get("filepath"),
            }
            screenshot_infos.append(screenshot_info)

    error_message = None
    exception = []
    if step.error_message and step_obj.status.name == "failed":
        error_message = CONFIG.hide_secrets(step_obj.error_message)

        if error := step_obj.exception:
            if isinstance(error, RetryError):
                error = error.last_attempt.exception()

            if len(error.args) > 0 and isinstance(error.args[0], str):
                error_class_name = error.__class__.__name__
                redacted_error_msg = CONFIG.hide_secrets(error.args[0])
                error_lines = redacted_error_msg.splitlines()
                error_lines[0] = f"{error_class_name}: {error_lines[0]}"
            else:
                error_lines = [repr(error)]

            exception = error_lines

    step.update(
        browser_info=getattr(step_obj, "browser_info", ""),
        browser_logs=getattr(step_obj, "browser_logs", ""),
        debug_output=getattr(step_obj, "debug_output", ""),
        duration=duration,
        end_at=getattr(step_obj, "end_at", None),
        error_message=error_message,
        exception=exception,
        has_substeps=getattr(step_obj, "has_substeps", False),
        parent_seq=getattr(step_obj, "parent_seq", None),
        screenshots=screenshot_infos,
        section_level=getattr(step_obj, "section_level", None),
        seq=step_obj.seq,
        start_at=getattr(step_obj, "start_at", None),
        status=step_obj.status.name,
        stderr=getattr(step_obj, "stderr", []),
        stdout=getattr(step_obj, "stdout", []),
    ).where(step.step_run_id == step_obj.step_run_id).execute()


def finish_scenario_record(scenario_obj):
    db.connect(reuse_if_open=True)
    if getattr(scenario_obj, "start_at", None):
        start_at = datetime.fromisoformat(scenario_obj.start_at)
    else:
        start_at = None
    if getattr(scenario_obj, "end_at", None):
        end_at = datetime.fromisoformat(scenario_obj.end_at)
    else:
        end_at = None
    if start_at and end_at:
        duration = (end_at - start_at).total_seconds()
    else:
        duration = None

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
        log_files_json = sorted(log_files)

    if scenario_obj.hook_failed:
        status = "errored"
    else:
        status = scenario_obj.status.name

    scenario.update(
        status=status,
        duration=duration,
        end_at=end_at,
        log_files=log_files_json,
        cucu_config=getattr(scenario_obj, "cucu_config_json", dict()),
        browser_info=getattr(scenario_obj, "browser_info", dict()),
        custom_data=getattr(scenario_obj, "custom_data", dict()),
    ).where(scenario.scenario_run_id == scenario_obj.scenario_run_id).execute()


def finish_feature_record(feature_obj):
    db.connect(reuse_if_open=True)
    feature.update(
        status=feature_obj.status.name,
        end_at=datetime.now().isoformat(),
        custom_data=feature_obj.custom_data,
    ).where(feature.feature_run_id == feature_obj.feature_run_id).execute()


def finish_worker_record(custom_data=None, worker_run_id=None):
    db.connect(reuse_if_open=True)
    target_worker_run_id = worker_run_id or CONFIG["WORKER_RUN_ID"]
    worker.update(
        end_at=datetime.now().isoformat(),
        custom_data=custom_data,
    ).where(worker.worker_run_id == target_worker_run_id).execute()


def finish_cucu_run_record():
    db.connect(reuse_if_open=True)
    cucu_run.update(
        end_at=datetime.now().isoformat(),
    ).where(cucu_run.cucu_run_id == CONFIG["CUCU_RUN_ID"]).execute()


def close_db():
    if not db.is_closed():
        db.close()


def create_database_file(db_filepath):
    db.init(db_filepath)
    db.connect(reuse_if_open=True)
    db.create_tables([cucu_run, worker, feature, scenario, step])
    db.execute_sql("""
            CREATE VIEW IF NOT EXISTS flat_all AS
            SELECT
                COUNT(DISTINCT s.feature_run_id) AS features,
                COUNT(s.scenario_run_id) AS scenarios,
                SUM(CASE WHEN s.status = 'passed' THEN 1 ELSE 0 END) AS passed,
                SUM(CASE WHEN s.status = 'failed' THEN 1 ELSE 0 END) AS failed,
                SUM(CASE WHEN s.status = 'skipped' THEN 1 ELSE 0 END) AS skipped,
                SUM(CASE WHEN s.status = 'errored' THEN 1 ELSE 0 END) AS errored,
                SUM(s.duration) AS duration
            FROM scenario s
        """)
    db.execute_sql("""
            CREATE VIEW IF NOT EXISTS flat_feature AS
            SELECT
                w.cucu_run_id,
                f.start_at,
                f.name AS feature_name,
                COUNT(s.scenario_run_id) AS scenarios,
                SUM(CASE WHEN s.status = 'passed' THEN 1 ELSE 0 END) AS passed,
                SUM(CASE WHEN s.status = 'failed' THEN 1 ELSE 0 END) AS failed,
                SUM(CASE WHEN s.status = 'skipped' THEN 1 ELSE 0 END) AS skipped,
                SUM(CASE WHEN s.status = 'errored' THEN 1 ELSE 0 END) AS errored,
                SUM(s.duration) AS duration
            FROM cucu_run r
            JOIN worker w ON r.cucu_run_id = w.cucu_run_id
            JOIN feature f ON w.worker_run_id = f.worker_run_id
            JOIN scenario s ON f.feature_run_id = s.feature_run_id
            GROUP BY f.feature_run_id
            ORDER BY f.start_at ASC
        """)
    db.execute_sql("""
            CREATE VIEW IF NOT EXISTS flat AS
            SELECT
                w.cucu_run_id,
                s.start_at,
                s.duration,
                f.name AS feature_name,
                s.name AS scenario_name,
                CASE
                    WHEN f.tags = '[]' AND s.tags = '[]' THEN JSON('[]')
                    WHEN f.tags = '[]' THEN s.tags
                    WHEN s.tags = '[]' THEN f.tags
                    ELSE JSON(REPLACE(f.tags, ']', '') || ',' || REPLACE(s.tags, '[', ''))
                END as tags,
                s.log_files
            FROM scenario s
            JOIN feature f ON s.feature_run_id = f.feature_run_id
            JOIN worker w ON f.worker_run_id = w.worker_run_id
        """)
    db.execute_sql("""
            CREATE VIEW IF NOT EXISTS flat_scenario AS
            SELECT
                s.scenario_run_id,
                f.name AS feature_name,
                s.name AS scenario_name,
                CASE
                    WHEN f.tags = '[]' AND s.tags = '[]' THEN JSON('[]')
                    WHEN f.tags = '[]' THEN s.tags
                    WHEN s.tags = '[]' THEN f.tags
                    ELSE JSON(REPLACE(f.tags, ']', '') || ',' || REPLACE(s.tags, '[', ''))
                END as tags,
                f.filename || ':' || s.line_number AS feature_file_line,
                s.status,
                (
                    SELECT json_group_array(json_object(
                        'status', st.status,
                        'duration', st.duration,
                        'name', st.name
                    ))
                    FROM step st
                    WHERE st.scenario_run_id = s.scenario_run_id
                    ORDER BY st.seq
                ) AS steps,
                (
                    SELECT st.debug_output
                    FROM step st
                    WHERE st.scenario_run_id = s.scenario_run_id
                    ORDER BY st.seq DESC
                    LIMIT 1
                ) AS last_step_debug_log
            FROM scenario s
            JOIN feature f ON s.feature_run_id = f.feature_run_id
        """)


def get_first_cucu_run_filepath():
    run_record = cucu_run.select().first()
    return run_record.filepath


def consolidate_database_files(results_dir, combine=False):
    # This function would need a more advanced approach with peewee, so for now, keep using sqlite3 for consolidation
    results_path = Path(results_dir)
    target_db_path = results_path / "run.db"
    if not target_db_path.exists():
        cucu_logger.info(
            f"Creating new consolidated database at {target_db_path}"
        )
        create_database_file(target_db_path)
    else:
        cucu_logger.debug(f"Found existing database at {target_db_path}")

    if not combine:
        db_files = [
            db for db in results_path.glob("**/run*.db") if db.name != "run.db"
        ]
    else:
        # include all run.db files in all subdirectories
        db_files = [
            db for db in results_path.rglob("run*.db") if db != Path("run.db")
        ]

    if not db_files:
        cucu_logger.debug("No database files found to consolidate.")
        return
    else:
        cucu_logger.debug(
            f"Found {len(db_files)} database files to consolidate."
        )

    tables_to_copy = ["cucu_run", "worker", "feature", "scenario", "step"]
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

                    # prep cucu_run for combining multiple runs
                    if table_name == "cucu_run":
                        db_path_index = columns.index("db_path")
                        rows = [
                            tuple(
                                item if idx != db_path_index else str(db_file)
                                for idx, item in enumerate(row)
                            )
                            for row in rows
                        ]

                    placeholders = ",".join(["?" for _ in columns])
                    target_cursor.executemany(
                        f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})",
                        rows,
                    )
                    target_conn.commit()

            if not combine and db_file.name != "run.db":
                # remove the worker db files
                db_file.unlink()


def init_html_report_db(db_path):
    db.init(db_path)
    db.connect(reuse_if_open=True)


def close_html_report_db():
    db.close()

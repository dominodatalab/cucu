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
    date = TextField()
    start_at = DateTimeField()
    end_at = DateTimeField(null=True)


class worker(BaseModel):
    worker_run_id = TextField(primary_key=True)
    cucu_run_id = ForeignKeyField(
        cucu_run,
        field="cucu_run_id",
        backref="workers",
        column_name="cucu_run_id",
        null=True,
    )
    parent_id = ForeignKeyField(
        "self",
        field="worker_run_id",
        backref="child_workers",
        column_name="parent_id",
        null=True,
    )
    start_at = DateTimeField()
    end_at = DateTimeField(null=True)
    custom_data = JSONField(null=True)


class feature(BaseModel):
    feature_run_id = TextField(primary_key=True)
    worker_run_id = ForeignKeyField(
        worker,
        field="worker_run_id",
        backref="features",
        column_name="worker_run_id",
    )
    name = TextField()
    filename = TextField()
    description = TextField()
    tags = TextField()
    start_at = DateTimeField()
    end_at = DateTimeField(null=True)
    custom_data = JSONField(null=True)


class scenario(BaseModel):
    scenario_run_id = TextField(primary_key=True)
    feature_run_id = ForeignKeyField(
        feature,
        field="feature_run_id",
        backref="scenarios",
        column_name="feature_run_id",
    )
    name = TextField()
    line_number = IntegerField()
    seq = IntegerField()
    tags = TextField()
    status = TextField(null=True)
    duration = FloatField(null=True)
    start_at = DateTimeField()
    end_at = DateTimeField(null=True)
    log_files = JSONField(null=True)
    cucu_config = JSONField(null=True)
    browser_info = JSONField(null=True)
    custom_data = JSONField(null=True)


class step(BaseModel):
    step_run_id = TextField(primary_key=True)
    scenario_run_id = ForeignKeyField(
        scenario,
        field="scenario_run_id",
        backref="steps",
        column_name="scenario_run_id",
    )
    seq = IntegerField()
    section_level = IntegerField(null=True)
    parent_seq = IntegerField(null=True)
    keyword = TextField()
    name = TextField()
    text = TextField(null=True)
    table_data = JSONField(null=True)
    location = TextField()
    is_substep = BooleanField()
    has_substeps = BooleanField()
    status = TextField(null=True)
    duration = FloatField(null=True)
    start_at = DateTimeField()
    end_at = DateTimeField(null=True)
    debug_output = TextField(null=True)
    browser_logs = TextField(null=True)
    browser_info = JSONField(null=True)
    screenshots = JSONField(null=True)


def record_cucu_run():
    cucu_run_id_val = CONFIG["CUCU_RUN_ID"]
    worker_run_id = CONFIG["WORKER_RUN_ID"]

    db.connect(reuse_if_open=True)
    start_at = datetime.now().isoformat()
    cucu_run.create(
        cucu_run_id=cucu_run_id_val,
        full_arguments=sys.argv,
        date=start_at,
        start_at=start_at,
    )

    worker.create(
        worker_run_id=worker_run_id,
        cucu_run_id=cucu_run_id_val,
        parent_id=CONFIG.get("WORKER_PARENT_ID")
        if CONFIG.get("WORKER_PARENT_ID") != worker_run_id
        else None,
        start_at=datetime.now().isoformat(),
    )
    db.close()
    return str(db_filepath)


def record_feature(feature_obj):
    db.connect(reuse_if_open=True)
    feature.create(
        feature_run_id=feature_obj.feature_run_id,
        worker_run_id=CONFIG["WORKER_RUN_ID"],
        name=feature_obj.name,
        filename=feature_obj.filename,
        description="\n".join(feature_obj.description)
        if isinstance(feature_obj.description, list)
        else str(feature_obj.description),
        tags=" ".join(feature_obj.tags),
        start_at=datetime.now().isoformat(),
    )
    db.close()


def record_scenario(ctx):
    db.connect(reuse_if_open=True)
    scenario.create(
        scenario_run_id=ctx.scenario.scenario_run_id,
        feature_run_id=ctx.scenario.feature.feature_run_id,
        name=ctx.scenario.name,
        line_number=ctx.scenario.line,
        seq=ctx.scenario_index,
        tags=" ".join(ctx.scenario.tags),
        start_at=ctx.scenario.start_at,
    )
    db.close()


def start_step_record(ctx, step_obj):
    db.connect(reuse_if_open=True)
    if not step_obj.table:
        table = None
    else:
        table = [step_obj.table.headings]
        table.extend([row.cells for row in step_obj.table.rows])
    step.create(
        step_run_id=step_obj.step_run_id,
        scenario_run_id=ctx.scenario.scenario_run_id,
        seq=step_obj.seq,
        keyword=step_obj.keyword,
        name=step_obj.name,
        text=step_obj.text if step_obj.text else None,
        table_data=table if step_obj.table else None,
        location=str(step_obj.location),
        is_substep=step_obj.is_substep,
        has_substeps=step_obj.has_substeps,
        section_level=getattr(step_obj, "section_level", None),
        start_at=step_obj.start_at,
    )
    db.close()


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

    step.update(
        section_level=getattr(step_obj, "section_level", None),
        parent_seq=step_obj.parent_seq,
        has_substeps=step_obj.has_substeps,
        status=step_obj.status.name,
        duration=duration,
        end_at=step_obj.end_at,
        debug_output=step_obj.debug_output,
        browser_logs=step_obj.browser_logs,
        browser_info=step_obj.browser_info,
        screenshots=screenshot_infos,
    ).where(step.step_run_id == step_obj.step_run_id).execute()
    db.close()


def finish_scenario_record(scenario_obj):
    db.connect(reuse_if_open=True)
    start_dt = datetime.fromisoformat(scenario_obj.start_at)
    end_dt = datetime.fromisoformat(scenario_obj.end_at)
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
        log_files_json = sorted(log_files)
    custom_data_json = scenario_obj.custom_data
    scenario.update(
        status=scenario_obj.status.name,
        duration=duration,
        end_at=scenario_obj.end_at,
        log_files=log_files_json,
        cucu_config=scenario_obj.cucu_config_json,
        browser_info=scenario_obj.browser_info,
        custom_data=custom_data_json,
    ).where(scenario.scenario_run_id == scenario_obj.scenario_run_id).execute()
    db.close()


def finish_feature_record(feature_obj):
    db.connect(reuse_if_open=True)
    feature.update(
        end_at=datetime.now().isoformat(),
        custom_data=feature_obj.custom_data,
    ).where(feature.feature_run_id == feature_obj.feature_run_id).execute()
    db.close()


def finish_worker_record(custom_data=None, worker_run_id=None):
    db.connect(reuse_if_open=True)
    target_worker_run_id = worker_run_id or CONFIG["WORKER_RUN_ID"]
    worker.update(
        end_at=datetime.now().isoformat(),
        custom_data=custom_data,
    ).where(worker.worker_run_id == target_worker_run_id).execute()
    db.close()


def finish_cucu_run_record():
    db.connect(reuse_if_open=True)
    cucu_run.update(
        end_at=datetime.now().isoformat(),
    ).where(cucu_run.cucu_run_id == CONFIG["CUCU_RUN_ID"]).execute()
    db.close()


def create_database_file(db_filepath):
    db.init(db_filepath)
    db.connect(reuse_if_open=True)
    db.create_tables([cucu_run, worker, feature, scenario, step])
    db.execute_sql("""
            CREATE VIEW IF NOT EXISTS flat AS
            SELECT
                w.cucu_run_id,
                s.start_at,
                s.duration,
                f.name AS feature_name,
                s.name AS scenario_name,
                f.tags || ' ' || s.tags AS tags,
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
                f.tags || ' ' || s.tags AS tags,
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
    db.close()


def consolidate_database_files(results_dir):
    # This function would need a more advanced approach with peewee, so for now, keep using sqlite3 for consolidation
    results_path = Path(results_dir)
    target_db_path = results_path / "run.db"
    db_files = [
        db for db in results_path.glob("**/*.db") if db.name != "run.db"
    ]
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
                    placeholders = ",".join(["?" for _ in columns])
                    target_cursor.executemany(
                        f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})",
                        rows,
                    )
                    target_conn.commit()
            db_file.unlink()

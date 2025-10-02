"""
Tests for the cucu database module using Peewee ORM.
"""

import tempfile
from pathlib import Path

import pytest
import pytest_check as check
from playhouse.sqlite_ext import SqliteExtDatabase

from cucu import db
from cucu.db import (
    cucu_run,
    feature,
    scenario,
    step,
    worker,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db = SqliteExtDatabase(tmp.name)
        original_db = db.db

        # Switch to test database
        db.db = test_db

        # Set up models to use test database
        for model in [cucu_run, worker, feature, scenario, step]:
            model._meta.database = test_db

        test_db.connect()
        test_db.create_tables([cucu_run, worker, feature, scenario, step])

        yield test_db

        test_db.close()
        # Restore original database
        db.db = original_db
        for model in [cucu_run, worker, feature, scenario, step]:
            model._meta.database = original_db

        Path(tmp.name).unlink()


@pytest.fixture
def sample_records_combined(temp_db):
    """Create sample records for testing database operations."""
    cucu_run_obj = cucu_run.create(
        cucu_run_id="test_run",
        full_arguments=["arg1", "arg2"],
        filepath="/path/to/test.feature",
        date="2024-01-01T10:00:00",
        start_at="2024-01-01T10:00:00",
    )

    worker_obj = worker.create(
        worker_run_id="test_worker",
        cucu_run_id="test_run",
        start_at="2024-01-01T10:00:00",
        custom_data={"key": "value", "number": 123},
    )

    feature_obj = feature.create(
        feature_run_id="test_feature",
        worker_run_id="test_worker",
        name="Test Feature",
        filename="test.feature",
        description="Test description",
        tags="tag1 tag2 tag3",
        start_at="2024-01-01T10:00:00",
    )

    scenario_obj = scenario.create(
        scenario_run_id="test_scenario",
        feature_run_id="test_feature",
        name="Test Scenario",
        line_number=10,
        seq=1,
        tags="smoke critical",
        start_at="2024-01-01T10:00:00",
    )

    step_obj = step.create(
        step_run_id="test_step",
        scenario_run_id="test_scenario",
        seq=1,
        keyword="Given",
        name="test step",
        location="test.feature:10",
        has_substeps=False,
        start_at="2024-01-01T10:00:00",
        browser_info="",
        browser_logs="",
        debug_output="",
        stderr=[],
        stdout=[],
    )

    cucu_run.create(
        cucu_run_id="consistency_test",
        full_arguments=[],
        filepath="/path/to/consistency.feature",
        date="2024-01-01T10:00:00",
        start_at="2024-01-01T10:00:00",
    )

    worker_consistency = worker.create(
        worker_run_id="worker_consistency",
        cucu_run_id="consistency_test",
        start_at="2024-01-01T10:00:00",
        end_at=None,
        custom_data=None,
    )

    feature_consistency = feature.create(
        feature_run_id="feature_consistency",
        worker_run_id="worker_consistency",
        name="Consistency Feature",
        filename="consistency.feature",
        description="Test description",
        tags="consistency",
        start_at="2024-01-01T10:00:00",
    )

    scenario_consistency = scenario.create(
        scenario_run_id="scenario_consistency",
        feature_run_id="feature_consistency",
        name="Consistency Scenario",
        line_number=10,
        seq=1,
        tags="consistency",
        start_at="2024-01-01T10:00:00",
    )

    step_consistency = step.create(
        step_run_id="step_consistency",
        scenario_run_id="scenario_consistency",
        seq=1,
        keyword="Given",
        name="consistency step",
        location="consistency.feature:10",
        has_substeps=False,
        start_at="2024-01-01T10:00:00",
        browser_info="",
        browser_logs="",
        debug_output="",
        stderr=[],
        stdout=[],
    )

    return {
        "cucu_run": cucu_run_obj,
        "worker": worker_obj,
        "feature": feature_obj,
        "scenario": scenario_obj,
        "step": step_obj,
        "worker_consistency": worker_consistency,
        "feature_consistency": feature_consistency,
        "scenario_consistency": scenario_consistency,
        "step_consistency": step_consistency,
    }


def test_json_serialization_and_tags_formatting(sample_records_combined):
    retrieved_worker = worker.get(worker.worker_run_id == "test_worker")
    expected_data = {"key": "value", "number": 123}
    check.equal(retrieved_worker.custom_data, expected_data)

    check.equal(sample_records_combined["feature"].tags, "tag1 tag2 tag3")
    check.equal(sample_records_combined["scenario"].tags, "smoke critical")


def test_datetime_iso_format(temp_db):
    iso_datetime = "2024-01-01T10:30:45"

    cucu_run_obj = cucu_run.create(
        cucu_run_id="iso_test",
        full_arguments=[],
        filepath="/path/to/iso_test.feature",
        date=iso_datetime,
        start_at=iso_datetime,
    )

    check.equal(cucu_run_obj.start_at, iso_datetime)
    check.equal(cucu_run_obj.date, iso_datetime)


def test_complex_data_serialization(sample_records_combined):
    table_data = [
        ["Header1", "Header2"],
        ["Row1Col1", "Row1Col2"],
        ["Row2Col1", "Row2Col2"],
    ]

    screenshots_data = [
        {
            "step_name": "test step",
            "label": "before",
            "location": "test.feature:10",
            "size": {"width": 1920, "height": 1080},
            "filepath": "/path/to/screenshot.png",
        }
    ]

    step.update(
        table_data=table_data,
        is_substep=False,
        screenshots=screenshots_data,
    ).where(step.step_run_id == "test_step").execute()

    retrieved = step.get(step.step_run_id == "test_step")
    check.equal(retrieved.table_data, table_data)
    check.equal(retrieved.screenshots, screenshots_data)


def test_relationships_and_record_completion(sample_records_combined):
    check.equal(
        sample_records_combined["worker"].cucu_run_id.cucu_run_id, "test_run"
    )
    check.equal(
        sample_records_combined["feature"].worker_run_id.worker_run_id,
        "test_worker",
    )
    check.equal(
        sample_records_combined["scenario"].feature_run_id.feature_run_id,
        "test_feature",
    )
    check.equal(
        sample_records_combined["step"].scenario_run_id.scenario_run_id,
        "test_scenario",
    )

    check.is_none(sample_records_combined["scenario"].status)
    check.is_none(sample_records_combined["scenario"].end_at)
    check.is_none(sample_records_combined["step"].status)
    check.is_none(sample_records_combined["step"].end_at)

    scenario.update(
        status="passed", duration=1.5, end_at="2024-01-01T10:00:01.5"
    ).where(scenario.scenario_run_id == "test_scenario").execute()

    step.update(
        status="passed",
        duration=0.5,
        end_at="2024-01-01T10:00:00.5",
        is_substep=False,
    ).where(step.step_run_id == "test_step").execute()

    updated_scenario = scenario.get(
        scenario.scenario_run_id == "test_scenario"
    )
    updated_step = step.get(step.step_run_id == "test_step")

    check.equal(updated_scenario.status, "passed")
    check.equal(updated_scenario.duration, 1.5)
    check.equal(updated_scenario.end_at, "2024-01-01T10:00:01.5")
    check.equal(updated_step.status, "passed")
    check.equal(updated_step.duration, 0.5)
    check.equal(updated_step.end_at, "2024-01-01T10:00:00.5")


def test_data_consistency_and_null_handling(sample_records_combined):
    check.equal(
        cucu_run.select()
        .where(cucu_run.cucu_run_id == "consistency_test")
        .count(),
        1,
    )
    check.equal(
        worker.select()
        .where(worker.cucu_run_id == "consistency_test")
        .count(),
        1,
    )
    check.equal(
        feature.select()
        .where(feature.worker_run_id == "worker_consistency")
        .count(),
        1,
    )
    check.equal(
        scenario.select()
        .where(scenario.feature_run_id == "feature_consistency")
        .count(),
        1,
    )
    check.equal(
        step.select()
        .where(step.scenario_run_id == "scenario_consistency")
        .count(),
        1,
    )

    retrieved_worker = worker.get(worker.worker_run_id == "worker_consistency")
    check.is_none(retrieved_worker.end_at)
    check.is_none(retrieved_worker.custom_data)

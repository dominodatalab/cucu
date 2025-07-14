import sqlite3
import tempfile
from unittest import mock

from cucu.db import (
    create_flat_view,
    create_run_database,
    finish_scenario_record,
    record_feature,
    record_scenario,
)


def _setup_config_mock(config_mock, run_id, worker_id, db_filepath):
    config_mock.__getitem__.side_effect = lambda key: {
        "WORKER_RUN_ID": worker_id,
        "CUCU_RUN_ID": run_id,
    }[key]
    if db_filepath:
        config_mock.get.return_value = db_filepath


def _create_feature_mock(feature_id, name, filename, description, tags):
    feature_mock = mock.MagicMock()
    feature_mock.feature_run_id = feature_id
    feature_mock.name = name
    feature_mock.filename = filename
    feature_mock.description = description
    feature_mock.tags = tags
    return feature_mock


def _create_scenario_context_mock(
    scenario_id, feature_id, name, tags, start_at, index=1
):
    ctx_mock = mock.MagicMock()
    ctx_mock.scenario.scenario_run_id = scenario_id
    ctx_mock.scenario.feature.feature_run_id = feature_id
    ctx_mock.scenario.name = name
    ctx_mock.scenario.tags = tags
    ctx_mock.scenario.start_at = start_at
    ctx_mock.scenario_index = index
    return ctx_mock


def _create_scenario_finish_mock(scenario_id, status, start_at, end_at):
    scenario_mock = mock.MagicMock()
    scenario_mock.scenario_run_id = scenario_id
    scenario_mock.status = mock.MagicMock()
    scenario_mock.status.name = status
    scenario_mock.start_at = start_at
    scenario_mock.end_at = end_at
    return scenario_mock


def test_flat_view_creation_and_query():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            _setup_config_mock(config_mock, "run_123", "worker_456", None)
            db_filepath = create_run_database(temp_dir)
            config_mock.get.return_value = db_filepath

            feature_mock = _create_feature_mock(
                "feature_789",
                "Login Feature",
                "login.feature",
                "Test login functionality",
                ["login", "auth"],
            )
            record_feature(feature_mock)

            ctx_mock = _create_scenario_context_mock(
                "scenario_101",
                "feature_789",
                "Valid login",
                ["smoke", "positive"],
                "2024-01-01T10:01:30",
            )
            record_scenario(ctx_mock)

            scenario_mock = _create_scenario_finish_mock(
                "scenario_101",
                "passed",
                "2024-01-01T10:01:30",
                "2024-01-01T10:01:31.5",
            )
            finish_scenario_record(scenario_mock)

        create_flat_view(db_filepath)

        with sqlite3.connect(db_filepath) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='view' AND name='flat'"
            )
            view_exists = cursor.fetchone()
            assert view_exists is not None

            cursor.execute("SELECT * FROM flat")
            result = cursor.fetchone()
            assert result is not None

            (
                cucu_run_id,
                start_at,
                duration,
                feature_name,
                scenario_name,
                tags,
            ) = result

            assert cucu_run_id == "run_123"
            assert start_at == "2024-01-01T10:01:30"
            assert duration == 1.5
            assert feature_name == "Login Feature"
            assert scenario_name == "Valid login"
            assert tags == "login auth smoke positive"


def test_flat_view_with_empty_tags():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            _setup_config_mock(config_mock, "run_456", "worker_789", None)
            db_filepath = create_run_database(temp_dir)
            config_mock.get.return_value = db_filepath

            feature_mock = _create_feature_mock(
                "feature_101",
                "Empty Tags Feature",
                "empty.feature",
                "No tags",
                [],
            )
            record_feature(feature_mock)

            ctx_mock = _create_scenario_context_mock(
                "scenario_202",
                "feature_101",
                "Empty tags scenario",
                [],
                "2024-01-01T10:01:30",
            )
            record_scenario(ctx_mock)

            scenario_mock = _create_scenario_finish_mock(
                "scenario_202",
                "passed",
                "2024-01-01T10:01:30",
                "2024-01-01T10:02:00",
            )
            finish_scenario_record(scenario_mock)

        create_flat_view(db_filepath)

        with sqlite3.connect(db_filepath) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tags FROM flat")
            result = cursor.fetchone()
            assert result[0] == " "


def test_flat_view_with_partial_tags():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            _setup_config_mock(config_mock, "run_789", "worker_101", None)
            db_filepath = create_run_database(temp_dir)
            config_mock.get.return_value = db_filepath

            feature_mock1 = _create_feature_mock(
                "feature_202",
                "Feature Only Tags",
                "partial.feature",
                "Only feature tags",
                ["feature-tag1", "feature-tag2"],
            )
            record_feature(feature_mock1)

            ctx_mock1 = _create_scenario_context_mock(
                "scenario_303",
                "feature_202",
                "No scenario tags",
                [],
                "2024-01-01T10:01:30",
            )
            record_scenario(ctx_mock1)

            feature_mock2 = _create_feature_mock(
                "feature_303",
                "Scenario Only Tags",
                "partial2.feature",
                "Only scenario tags",
                [],
            )
            record_feature(feature_mock2)

            ctx_mock2 = _create_scenario_context_mock(
                "scenario_404",
                "feature_303",
                "Has scenario tags",
                ["scenario-tag1", "scenario-tag2"],
                "2024-01-01T10:02:30",
            )
            record_scenario(ctx_mock2)

            scenario_mock1 = _create_scenario_finish_mock(
                "scenario_303",
                "passed",
                "2024-01-01T10:01:30",
                "2024-01-01T10:02:00",
            )
            finish_scenario_record(scenario_mock1)

            scenario_mock2 = _create_scenario_finish_mock(
                "scenario_404",
                "passed",
                "2024-01-01T10:02:30",
                "2024-01-01T10:03:00",
            )
            finish_scenario_record(scenario_mock2)

        create_flat_view(db_filepath)

        with sqlite3.connect(db_filepath) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT scenario_name, tags FROM flat ORDER BY scenario_name"
            )
            results = cursor.fetchall()

            assert len(results) == 2
            assert results[1][0] == "No scenario tags"
            assert results[1][1] == "feature-tag1 feature-tag2 "
            assert results[0][0] == "Has scenario tags"
            assert results[0][1] == " scenario-tag1 scenario-tag2"

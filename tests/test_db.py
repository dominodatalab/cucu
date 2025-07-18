import sqlite3
import tempfile
from pathlib import Path
from unittest import mock

from cucu.db import (
    consolidate_database_files,
    create_database_file,
    finish_scenario_record,
    finish_step_record,
    record_cucu_run,
    record_feature,
    record_scenario,
    start_step_record,
)


def _setup_config_mock(config_mock, run_id, worker_id, db_filepath):
    config_mock.__getitem__.side_effect = lambda key: {
        "WORKER_RUN_ID": worker_id,
        "CUCU_RUN_ID": run_id,
        "RUN_DB_PATH": db_filepath,
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
    scenario_id, feature_id, name, tags, start_at, index=1, line_number=1
):
    ctx_mock = mock.MagicMock()
    ctx_mock.scenario.scenario_run_id = scenario_id
    ctx_mock.scenario.feature.feature_run_id = feature_id
    ctx_mock.scenario.name = name
    ctx_mock.scenario.line = line_number
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
    scenario_mock.cucu_config_json = "{}"
    scenario_mock.custom_data = {}
    return scenario_mock


def test_flat_view_creation_and_query():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/run_run_123_worker_456.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )
            create_database_file(db_filepath)
            record_cucu_run()
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
                log_files,
            ) = result

            assert cucu_run_id == "run_123"
            assert start_at == "2024-01-01T10:01:30"
            assert duration == 1.5
            assert feature_name == "Login Feature"
            assert scenario_name == "Valid login"
            assert tags == "login auth smoke positive"
            assert log_files == "[]"


def test_flat_view_with_empty_tags():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/run_run_456_worker_789.db"
            _setup_config_mock(
                config_mock, "run_456", "worker_789", db_filepath
            )
            create_database_file(db_filepath)
            record_cucu_run()
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

        with sqlite3.connect(db_filepath) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tags, log_files FROM flat")
            result = cursor.fetchone()
            assert result[0] == " "
            assert result[1] == "[]"


def test_flat_view_with_partial_tags():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/run_run_789_worker_101.db"
            _setup_config_mock(
                config_mock, "run_789", "worker_101", db_filepath
            )
            create_database_file(db_filepath)
            record_cucu_run()
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

        with sqlite3.connect(db_filepath) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT scenario_name, tags, log_files FROM flat ORDER BY scenario_name"
            )
            results = cursor.fetchall()

            assert len(results) == 2
            assert results[1][0] == "No scenario tags"
            assert results[1][1] == "feature-tag1 feature-tag2 "
            assert results[1][2] == "[]"
            assert results[0][0] == "Has scenario tags"
            assert results[0][1] == " scenario-tag1 scenario-tag2"
            assert results[0][2] == "[]"


@mock.patch("cucu.db.CONFIG")
def test_consolidate_database_files(config_mock):
    """Test database consolidation merges multiple worker databases into run.db"""
    with tempfile.TemporaryDirectory() as temp_dir:
        results_dir = Path(temp_dir)

        # Create main run.db
        main_db_path = results_dir / "run.db"
        create_database_file(main_db_path)

        # Create worker database 1
        worker1_db_path = results_dir / "worker_001.db"
        create_database_file(worker1_db_path)

        # Create worker database 2
        worker2_db_path = results_dir / "worker_002.db"
        create_database_file(worker2_db_path)

        _setup_config_mock(
            config_mock, "run_001", "worker_001", str(worker1_db_path)
        )

        with sqlite3.connect(worker1_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cucu_run (cucu_run_id, full_arguments, date, start_at) VALUES (?, ?, ?, ?)",
                (
                    "run_001",
                    '["test1"]',
                    "2024-01-01T10:00:00",
                    "2024-01-01T10:00:00",
                ),
            )
            cursor.execute(
                "INSERT INTO workers (worker_run_id, cucu_run_id, start_at) VALUES (?, ?, ?)",
                ("worker_001", "run_001", "2024-01-01T10:00:00"),
            )
            cursor.execute(
                "INSERT INTO features (feature_run_id, worker_run_id, name, filename, description, tags, start_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    "feature_001",
                    "worker_001",
                    "Test Feature 1",
                    "test1.feature",
                    "Description 1",
                    "tag1",
                    "2024-01-01T10:00:00",
                ),
            )
            cursor.execute(
                "INSERT INTO scenarios (scenario_run_id, feature_run_id, name, line_number, seq, tags, start_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    "scenario_001",
                    "feature_001",
                    "Test Scenario 1",
                    10,
                    1,
                    "tag1",
                    "2024-01-01T10:00:00",
                ),
            )
            conn.commit()

        _setup_config_mock(
            config_mock, "run_001", "worker_002", str(worker2_db_path)
        )

        with sqlite3.connect(worker2_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO workers (worker_run_id, cucu_run_id, start_at) VALUES (?, ?, ?)",
                ("worker_002", "run_001", "2024-01-01T10:01:00"),
            )
            cursor.execute(
                "INSERT INTO features (feature_run_id, worker_run_id, name, filename, description, tags, start_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    "feature_002",
                    "worker_002",
                    "Test Feature 2",
                    "test2.feature",
                    "Description 2",
                    "tag2",
                    "2024-01-01T10:01:00",
                ),
            )
            cursor.execute(
                "INSERT INTO scenarios (scenario_run_id, feature_run_id, name, line_number, seq, tags, start_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    "scenario_002",
                    "feature_002",
                    "Test Scenario 2",
                    20,
                    1,
                    "tag2",
                    "2024-01-01T10:01:00",
                ),
            )
            conn.commit()

        assert worker1_db_path.exists()
        assert worker2_db_path.exists()

        consolidate_database_files(str(results_dir))

        assert not worker1_db_path.exists()
        assert not worker2_db_path.exists()

        assert main_db_path.exists()

        with sqlite3.connect(main_db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM cucu_run")
            assert cursor.fetchone()[0] == 1

            cursor.execute("SELECT COUNT(*) FROM workers")
            assert cursor.fetchone()[0] == 2

            cursor.execute(
                "SELECT worker_run_id FROM workers ORDER BY worker_run_id"
            )
            workers = cursor.fetchall()
            assert workers[0][0] == "worker_001"
            assert workers[1][0] == "worker_002"

            cursor.execute("SELECT COUNT(*) FROM features")
            assert cursor.fetchone()[0] == 2

            cursor.execute("SELECT name FROM features ORDER BY name")
            features = cursor.fetchall()
            assert features[0][0] == "Test Feature 1"
            assert features[1][0] == "Test Feature 2"

            cursor.execute("SELECT COUNT(*) FROM scenarios")
            assert cursor.fetchone()[0] == 2

            cursor.execute("SELECT name FROM scenarios ORDER BY name")
            scenarios = cursor.fetchall()
            assert scenarios[0][0] == "Test Scenario 1"
            assert scenarios[1][0] == "Test Scenario 2"


@mock.patch("cucu.db.CONFIG")
def test_consolidate_database_files_with_subdirectories(config_mock):
    """Test database consolidation finds databases in subdirectories"""
    with tempfile.TemporaryDirectory() as temp_dir:
        results_dir = Path(temp_dir)

        # Create main run.db
        main_db_path = results_dir / "run.db"
        create_database_file(main_db_path)

        sub_dir = results_dir / "worker_logs"
        sub_dir.mkdir()
        worker_db_path = sub_dir / "worker_001.db"
        create_database_file(worker_db_path)

        _setup_config_mock(
            config_mock, "run_001", "worker_001", str(worker_db_path)
        )

        with sqlite3.connect(worker_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO workers (worker_run_id, cucu_run_id, start_at) VALUES (?, ?, ?)",
                ("worker_001", "run_001", "2024-01-01T10:00:00"),
            )
            conn.commit()

        consolidate_database_files(str(results_dir))

        assert not worker_db_path.exists()

        with sqlite3.connect(main_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM workers")
            assert cursor.fetchone()[0] == 1


@mock.patch("cucu.db.CONFIG")
def test_consolidate_database_files_empty_tables(config_mock):
    """Test database consolidation handles empty tables gracefully"""
    with tempfile.TemporaryDirectory() as temp_dir:
        results_dir = Path(temp_dir)

        main_db_path = results_dir / "run.db"
        create_database_file(main_db_path)

        worker_db_path = results_dir / "worker_001.db"
        create_database_file(worker_db_path)

        consolidate_database_files(str(results_dir))

        assert not worker_db_path.exists()

        assert main_db_path.exists()
        with sqlite3.connect(main_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM workers")
            assert cursor.fetchone()[0] == 0


def test_step_screenshots_recording():
    """Test that step screenshots are properly recorded in JSON format"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/run_run_123_worker_456.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )
            create_database_file(db_filepath)
            record_cucu_run()
            config_mock.get.return_value = db_filepath

            # Create feature and scenario
            feature_mock = _create_feature_mock(
                "feature_789",
                "Screenshot Feature",
                "screenshot.feature",
                "Test screenshot functionality",
                ["screenshot"],
            )
            record_feature(feature_mock)

            ctx_mock = _create_scenario_context_mock(
                "scenario_101",
                "feature_789",
                "Screenshot scenario",
                ["test"],
                "2024-01-01T10:01:30",
            )
            ctx_mock.step_index = 0  # Add step index
            record_scenario(ctx_mock)

            # Create a step mock with screenshots
            step_mock = mock.MagicMock()
            step_mock.step_run_id = "step_001"
            step_mock.keyword = "Given"
            step_mock.name = "I take screenshots"
            step_mock.location = "screenshot.feature:5"
            step_mock.has_substeps = False
            step_mock.start_at = "2024-01-01T10:01:30"

            # Mock screenshots data
            step_mock.screenshots = [
                {
                    "step_name": "I take screenshots",
                    "label": "first screenshot",
                    "location": "(100,200)",
                    "size": "(300,400)",
                    "filepath": "/path/to/screenshot1.png",
                },
                {
                    "step_name": "I take screenshots",
                    "label": "second screenshot",
                    "location": "(150,250)",
                    "size": "(400,500)",
                    "filepath": "/path/to/screenshot2.png",
                },
            ]

            # Record the step
            start_step_record(ctx_mock, step_mock)

            # Finish the step
            step_mock.status.name = "passed"
            step_mock.end_at = "2024-01-01T10:01:31"
            step_mock.debug_output = ""
            step_mock.browser_logs = ""
            step_mock.browser_info = "{}"

            finish_step_record(step_mock, 1.0)

            # Verify screenshots are stored as JSON
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT screenshots FROM steps WHERE step_run_id = ?",
                    ("step_001",),
                )
                result = cursor.fetchone()

                assert result is not None
                screenshots_json = result[0]
                assert screenshots_json is not None

                # Parse and verify the JSON
                import json

                screenshots = json.loads(screenshots_json)
                assert len(screenshots) == 2

                # Verify first screenshot
                assert screenshots[0]["step_name"] == "I take screenshots"
                assert screenshots[0]["label"] == "first screenshot"
                assert screenshots[0]["location"] == "(100,200)"
                assert screenshots[0]["size"] == "(300,400)"
                assert screenshots[0]["filepath"] == "/path/to/screenshot1.png"

                # Verify second screenshot
                assert screenshots[1]["step_name"] == "I take screenshots"
                assert screenshots[1]["label"] == "second screenshot"
                assert screenshots[1]["location"] == "(150,250)"
                assert screenshots[1]["size"] == "(400,500)"
                assert screenshots[1]["filepath"] == "/path/to/screenshot2.png"


def test_step_no_screenshots_recording():
    """Test that steps without screenshots have empty JSON array"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/run_run_123_worker_456.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )
            create_database_file(db_filepath)
            record_cucu_run()
            config_mock.get.return_value = db_filepath

            # Create feature and scenario
            feature_mock = _create_feature_mock(
                "feature_789",
                "No Screenshot Feature",
                "noscreenshot.feature",
                "Test no screenshot functionality",
                ["test"],
            )
            record_feature(feature_mock)

            ctx_mock = _create_scenario_context_mock(
                "scenario_101",
                "feature_789",
                "No screenshot scenario",
                ["test"],
                "2024-01-01T10:01:30",
            )
            ctx_mock.step_index = 0  # Add step index
            record_scenario(ctx_mock)

            # Create a step mock without screenshots
            step_mock = mock.MagicMock()
            step_mock.step_run_id = "step_002"
            step_mock.keyword = "Given"
            step_mock.name = "I do not take screenshots"
            step_mock.location = "noscreenshot.feature:5"
            step_mock.has_substeps = False
            step_mock.start_at = "2024-01-01T10:01:30"

            # No screenshots attribute
            if hasattr(step_mock, "screenshots"):
                delattr(step_mock, "screenshots")

            # Record the step
            start_step_record(ctx_mock, step_mock)

            # Finish the step
            step_mock.status.name = "passed"
            step_mock.end_at = "2024-01-01T10:01:31"
            step_mock.debug_output = ""
            step_mock.browser_logs = ""
            step_mock.browser_info = "{}"

            finish_step_record(step_mock, 1.0)

            # Verify screenshots is empty JSON array
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT screenshots FROM steps WHERE step_run_id = ?",
                    ("step_002",),
                )
                result = cursor.fetchone()

                assert result is not None
                screenshots_json = result[0]
                assert screenshots_json == "[]"


def test_step_screenshots_json_column():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/run_run_123_worker_456.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )
            create_database_file(db_filepath)
            record_cucu_run()

            # Create feature and scenario
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

            # Create step mock with screenshots
            step_mock = mock.MagicMock()
            step_mock.step_run_id = "step_001"
            step_mock.keyword = "Given"
            step_mock.name = "I open a browser"
            step_mock.location = "login.feature:5"
            step_mock.has_substeps = False
            step_mock.start_at = "2024-01-01T10:01:30"
            step_mock.status.name = "passed"
            step_mock.end_at = "2024-01-01T10:01:31"
            step_mock.debug_output = "Debug info"
            step_mock.browser_logs = "[]"
            step_mock.browser_info = "{}"

            # Add screenshots data
            step_mock.screenshots = [
                {
                    "step_name": "I open a browser",
                    "label": "screenshot 1",
                    "location": "(100,200)",
                    "size": "(800,600)",
                    "filepath": "/path/to/screenshot1.png",
                },
                {
                    "step_name": "I open a browser",
                    "label": "screenshot 2",
                    "location": "(150,250)",
                    "size": "(1024,768)",
                    "filepath": "/path/to/screenshot2.png",
                },
            ]

            ctx_mock.step_index = 0
            start_step_record(ctx_mock, step_mock)
            finish_step_record(step_mock, 1.0)

            # Verify screenshots JSON was saved correctly
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT screenshots FROM steps WHERE step_run_id = ?",
                    ("step_001",),
                )
                result = cursor.fetchone()

                assert result is not None
                screenshots_json = result[0]

                import json

                screenshots = json.loads(screenshots_json)
                assert len(screenshots) == 2

                assert screenshots[0]["step_name"] == "I open a browser"
                assert screenshots[0]["label"] == "screenshot 1"
                assert screenshots[0]["location"] == "(100,200)"
                assert screenshots[0]["size"] == "(800,600)"
                assert screenshots[0]["filepath"] == "/path/to/screenshot1.png"

                assert screenshots[1]["step_name"] == "I open a browser"
                assert screenshots[1]["label"] == "screenshot 2"
                assert screenshots[1]["location"] == "(150,250)"
                assert screenshots[1]["size"] == "(1024,768)"
                assert screenshots[1]["filepath"] == "/path/to/screenshot2.png"


def test_step_without_screenshots():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/run_run_123_worker_456.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )
            create_database_file(db_filepath)
            record_cucu_run()

            # Create feature and scenario
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

            # Create step mock without screenshots
            step_mock = mock.MagicMock()
            step_mock.step_run_id = "step_002"
            step_mock.keyword = "When"
            step_mock.name = "I click submit"
            step_mock.location = "login.feature:6"
            step_mock.has_substeps = False
            step_mock.start_at = "2024-01-01T10:01:31"
            step_mock.status.name = "passed"
            step_mock.end_at = "2024-01-01T10:01:32"
            step_mock.debug_output = "Debug info"
            step_mock.browser_logs = "[]"
            step_mock.browser_info = "{}"

            # No screenshots attribute
            del step_mock.screenshots

            ctx_mock.step_index = 1
            start_step_record(ctx_mock, step_mock)
            finish_step_record(step_mock, 1.0)

            # Verify empty screenshots JSON was saved
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT screenshots FROM steps WHERE step_run_id = ?",
                    ("step_002",),
                )
                result = cursor.fetchone()

                assert result is not None
                screenshots_json = result[0]
                assert screenshots_json == "[]"

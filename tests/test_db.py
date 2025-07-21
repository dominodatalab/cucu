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


def _create_step_mock(
    step_id,
    keyword,
    name,
    location,
    start_at,
    has_substeps=False,
    is_substep=False,
    text=None,
    table=None,
):
    step_mock = mock.MagicMock()
    step_mock.step_run_id = step_id
    step_mock.keyword = keyword
    step_mock.name = name
    step_mock.text = text
    step_mock.table = table
    step_mock.location = location
    step_mock.is_substep = is_substep
    step_mock.has_substeps = has_substeps
    step_mock.start_at = start_at
    return step_mock


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
            step_mock.text = None
            step_mock.table = None
            step_mock.location = "screenshot.feature:5"
            step_mock.is_substep = False
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
            step_mock.text = None
            step_mock.table = None
            step_mock.location = "noscreenshot.feature:5"
            step_mock.is_substep = False
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
            step_mock.text = None
            step_mock.table = None
            step_mock.location = "login.feature:5"
            step_mock.is_substep = False
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
            step_mock.text = None
            step_mock.table = None
            step_mock.location = "login.feature:6"
            step_mock.is_substep = False
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


def test_feature_custom_data_recording():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/test_feature_custom_data.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )

            create_database_file(db_filepath)
            record_cucu_run()

            # Test feature with complex custom_data
            feature_mock = _create_feature_mock(
                "feature_custom_001",
                "Feature with Custom Data",
                "custom.feature",
                "Testing custom data storage",
                ["custom", "test"],
            )
            feature_mock.custom_data = {
                "environment": "staging",
                "priority": "high",
                "metadata": {
                    "created_by": "test_suite",
                    "version": "1.2.3",
                    "tags": ["performance", "regression"],
                },
                "execution_context": {
                    "parallel_workers": 4,
                    "timeout_seconds": 300,
                },
            }

            record_feature(feature_mock)

            # Import here to avoid circular imports in test setup
            from cucu.db import finish_feature_record

            finish_feature_record(feature_mock)

            # Verify custom_data was stored correctly
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, custom_data FROM features WHERE feature_run_id = ?",
                    ("feature_custom_001",),
                )
                result = cursor.fetchone()

                assert result is not None
                feature_name, custom_data_json = result
                assert feature_name == "Feature with Custom Data"
                assert custom_data_json is not None

                # Parse and verify the JSON content
                import json

                custom_data = json.loads(custom_data_json)
                assert custom_data["environment"] == "staging"
                assert custom_data["priority"] == "high"
                assert custom_data["metadata"]["created_by"] == "test_suite"
                assert custom_data["metadata"]["version"] == "1.2.3"
                assert (
                    custom_data["execution_context"]["parallel_workers"] == 4
                )


def test_feature_empty_custom_data():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/test_feature_empty_custom_data.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )

            create_database_file(db_filepath)
            record_cucu_run()

            # Test feature with empty custom_data
            feature_mock = _create_feature_mock(
                "feature_empty_001",
                "Feature with Empty Custom Data",
                "empty.feature",
                "Testing empty custom data",
                ["empty"],
            )
            feature_mock.custom_data = {}

            record_feature(feature_mock)

            from cucu.db import finish_feature_record

            finish_feature_record(feature_mock)

            # Verify custom_data is NULL
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT custom_data FROM features WHERE feature_run_id = ?",
                    ("feature_empty_001",),
                )
                result = cursor.fetchone()

                assert result is not None
                custom_data_json = result[0]
                assert custom_data_json == "{}"


def test_scenario_custom_data_recording():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/test_scenario_custom_data.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )

            create_database_file(db_filepath)
            record_cucu_run()

            # Create feature first
            feature_mock = _create_feature_mock(
                "feature_scenario_001",
                "Feature for Scenario Custom Data",
                "scenario_custom.feature",
                "Testing scenario custom data",
                ["scenario", "custom"],
            )
            record_feature(feature_mock)

            # Create scenario context
            ctx_mock = _create_scenario_context_mock(
                "scenario_custom_001",
                "feature_scenario_001",
                "Scenario with Custom Data",
                ["custom", "data"],
                "2024-01-01T10:00:00",
                line_number=10,
            )
            record_scenario(ctx_mock)

            # Create scenario finish mock with complex custom_data
            scenario_mock = _create_scenario_finish_mock(
                "scenario_custom_001",
                "passed",
                "2024-01-01T10:00:00",
                "2024-01-01T10:01:30",
            )
            scenario_mock.custom_data = {
                "test_data": {
                    "input_values": ["user123", "password456"],
                    "expected_outcome": "successful_login",
                    "retry_count": 0,
                },
                "performance_metrics": {
                    "response_time_ms": 1250,
                    "memory_usage_mb": 45.2,
                    "cpu_usage_percent": 15.7,
                },
                "browser_info": {
                    "user_agent": "Chrome/91.0",
                    "viewport": {"width": 1920, "height": 1080},
                    "cookies_enabled": True,
                },
                "execution_metadata": {
                    "worker_id": "worker_001",
                    "attempt_number": 1,
                    "environment_variables": {
                        "TEST_ENV": "staging",
                        "DEBUG_MODE": False,
                    },
                },
            }

            finish_scenario_record(scenario_mock)

            # Verify custom_data was stored correctly
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, custom_data FROM scenarios WHERE scenario_run_id = ?",
                    ("scenario_custom_001",),
                )
                result = cursor.fetchone()

                assert result is not None
                scenario_name, custom_data_json = result
                assert scenario_name == "Scenario with Custom Data"
                assert custom_data_json is not None

                # Parse and verify the JSON content
                import json

                custom_data = json.loads(custom_data_json)
                assert (
                    custom_data["test_data"]["expected_outcome"]
                    == "successful_login"
                )
                assert (
                    custom_data["performance_metrics"]["response_time_ms"]
                    == 1250
                )
                assert custom_data["browser_info"]["viewport"]["width"] == 1920
                assert (
                    custom_data["execution_metadata"]["worker_id"]
                    == "worker_001"
                )
                assert (
                    custom_data["execution_metadata"]["environment_variables"][
                        "TEST_ENV"
                    ]
                    == "staging"
                )


def test_scenario_empty_custom_data():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/test_scenario_empty_custom_data.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )

            create_database_file(db_filepath)
            record_cucu_run()

            # Create feature first
            feature_mock = _create_feature_mock(
                "feature_empty_scenario_001",
                "Feature for Empty Scenario Custom Data",
                "empty_scenario.feature",
                "Testing empty scenario custom data",
                ["empty"],
            )
            record_feature(feature_mock)

            # Create scenario context
            ctx_mock = _create_scenario_context_mock(
                "scenario_empty_001",
                "feature_empty_scenario_001",
                "Scenario with Empty Custom Data",
                ["empty"],
                "2024-01-01T10:00:00",
                line_number=5,
            )
            record_scenario(ctx_mock)

            # Create scenario finish mock with empty custom_data
            scenario_mock = _create_scenario_finish_mock(
                "scenario_empty_001",
                "passed",
                "2024-01-01T10:00:00",
                "2024-01-01T10:00:30",
            )
            # custom_data already set to {} in _create_scenario_finish_mock

            finish_scenario_record(scenario_mock)

            # Verify custom_data is NULL
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT custom_data FROM scenarios WHERE scenario_run_id = ?",
                    ("scenario_empty_001",),
                )
                result = cursor.fetchone()

                assert result is not None
                custom_data_json = result[0]
                assert custom_data_json == "{}"


def test_custom_data_with_various_data_types():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/test_custom_data_types.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )

            create_database_file(db_filepath)
            record_cucu_run()

            # Test feature with various data types
            feature_mock = _create_feature_mock(
                "feature_types_001",
                "Feature with Various Data Types",
                "types.feature",
                "Testing various data types",
                ["types"],
            )
            feature_mock.custom_data = {
                "string_value": "test_string",
                "integer_value": 42,
                "float_value": 3.14159,
                "boolean_true": True,
                "boolean_false": False,
                "null_value": None,
                "list_value": [1, "two", 3.0, True, None],
                "nested_object": {
                    "inner_string": "nested",
                    "inner_number": 123,
                    "inner_list": ["a", "b", "c"],
                },
                "empty_list": [],
                "empty_object": {},
            }

            record_feature(feature_mock)
            from cucu.db import finish_feature_record

            finish_feature_record(feature_mock)

            # Create scenario with similar data types
            ctx_mock = _create_scenario_context_mock(
                "scenario_types_001",
                "feature_types_001",
                "Scenario with Various Data Types",
                ["types"],
                "2024-01-01T10:00:00",
            )
            record_scenario(ctx_mock)

            scenario_mock = _create_scenario_finish_mock(
                "scenario_types_001",
                "passed",
                "2024-01-01T10:00:00",
                "2024-01-01T10:00:15",
            )
            scenario_mock.custom_data = {
                "unicode_string": "Hello 世界 🌍",
                "large_number": 9223372036854775807,  # Max int64
                "scientific_notation": 1.23e-10,
                "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?",
                "multiline_string": "Line 1\nLine 2\nLine 3",
                "deeply_nested": {
                    "level1": {"level2": {"level3": "deep_value"}}
                },
            }

            finish_scenario_record(scenario_mock)

            # Verify both feature and scenario data
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()

                # Check feature custom_data
                cursor.execute(
                    "SELECT custom_data FROM features WHERE feature_run_id = ?",
                    ("feature_types_001",),
                )
                feature_result = cursor.fetchone()
                assert feature_result is not None

                import json

                feature_data = json.loads(feature_result[0])
                assert feature_data["string_value"] == "test_string"
                assert feature_data["integer_value"] == 42
                assert feature_data["float_value"] == 3.14159
                assert feature_data["boolean_true"] is True
                assert feature_data["boolean_false"] is False
                assert feature_data["null_value"] is None
                assert feature_data["list_value"] == [
                    1,
                    "two",
                    3.0,
                    True,
                    None,
                ]
                assert (
                    feature_data["nested_object"]["inner_string"] == "nested"
                )

                # Check scenario custom_data
                cursor.execute(
                    "SELECT custom_data FROM scenarios WHERE scenario_run_id = ?",
                    ("scenario_types_001",),
                )
                scenario_result = cursor.fetchone()
                assert scenario_result is not None

                scenario_data = json.loads(scenario_result[0])
                assert scenario_data["unicode_string"] == "Hello 世界 🌍"
                assert scenario_data["large_number"] == 9223372036854775807
                assert scenario_data["scientific_notation"] == 1.23e-10
                assert (
                    scenario_data["multiline_string"]
                    == "Line 1\nLine 2\nLine 3"
                )
                assert (
                    scenario_data["deeply_nested"]["level1"]["level2"][
                        "level3"
                    ]
                    == "deep_value"
                )


def test_custom_data_in_consolidated_database():
    with tempfile.TemporaryDirectory() as temp_dir:
        results_path = Path(temp_dir)

        # Create multiple database files with custom_data
        db_files = []
        for i in range(3):
            with mock.patch("cucu.db.CONFIG") as config_mock:
                db_filepath = results_path / f"run_run_{i}_worker_{i}.db"
                db_files.append(db_filepath)
                _setup_config_mock(
                    config_mock, f"run_{i}", f"worker_{i}", str(db_filepath)
                )

                create_database_file(str(db_filepath))
                record_cucu_run()

                # Create feature with custom_data
                feature_mock = _create_feature_mock(
                    f"feature_{i}",
                    f"Feature {i}",
                    f"feature_{i}.feature",
                    f"Description {i}",
                    [f"tag{i}"],
                )
                feature_mock.custom_data = {
                    "feature_index": i,
                    "feature_name": f"Feature {i}",
                    "batch_info": {
                        "batch_id": f"batch_{i}",
                        "created_at": f"2024-01-0{i + 1}",
                    },
                }
                record_feature(feature_mock)

                # Create scenario with custom_data
                ctx_mock = _create_scenario_context_mock(
                    f"scenario_{i}",
                    f"feature_{i}",
                    f"Scenario {i}",
                    [f"scenario_tag{i}"],
                    f"2024-01-0{i + 1}T10:00:00",
                )
                record_scenario(ctx_mock)

                scenario_mock = _create_scenario_finish_mock(
                    f"scenario_{i}",
                    "passed",
                    f"2024-01-0{i + 1}T10:00:00",
                    f"2024-01-0{i + 1}T10:01:00",
                )
                scenario_mock.custom_data = {
                    "scenario_index": i,
                    "scenario_name": f"Scenario {i}",
                    "execution_info": {
                        "worker": f"worker_{i}",
                        "duration_ms": (i + 1) * 1000,
                    },
                }

                finish_scenario_record(scenario_mock)

                from cucu.db import finish_feature_record

                finish_feature_record(feature_mock)

        # Create target database first
        consolidated_db = results_path / "run.db"
        create_database_file(str(consolidated_db))

        # Consolidate databases
        consolidate_database_files(str(results_path))

        # Verify consolidated data
        assert consolidated_db.exists()

        with sqlite3.connect(str(consolidated_db)) as conn:
            cursor = conn.cursor()

            # Check features custom_data
            cursor.execute(
                "SELECT feature_run_id, custom_data FROM features ORDER BY feature_run_id"
            )
            feature_results = cursor.fetchall()
            assert len(feature_results) == 3

            import json

            for i, (feature_id, custom_data_json) in enumerate(
                feature_results
            ):
                assert feature_id == f"feature_{i}"
                assert custom_data_json is not None
                custom_data = json.loads(custom_data_json)
                assert custom_data["feature_index"] == i
                assert custom_data["feature_name"] == f"Feature {i}"
                assert custom_data["batch_info"]["batch_id"] == f"batch_{i}"

            # Check scenarios custom_data
            cursor.execute(
                "SELECT scenario_run_id, custom_data FROM scenarios ORDER BY scenario_run_id"
            )
            scenario_results = cursor.fetchall()
            assert len(scenario_results) == 3

            for i, (scenario_id, custom_data_json) in enumerate(
                scenario_results
            ):
                assert scenario_id == f"scenario_{i}"
                assert custom_data_json is not None
                custom_data = json.loads(custom_data_json)
                assert custom_data["scenario_index"] == i
                assert custom_data["scenario_name"] == f"Scenario {i}"
                assert custom_data["execution_info"]["worker"] == f"worker_{i}"

        # Verify original files were cleaned up
        for db_file in db_files:
            assert not db_file.exists()


def test_step_text_and_table_recording():
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("cucu.db.CONFIG") as config_mock:
            db_filepath = f"{temp_dir}/test_step_text_table.db"
            _setup_config_mock(
                config_mock, "run_123", "worker_456", db_filepath
            )

            create_database_file(db_filepath)
            record_cucu_run()

            # Create feature and scenario
            feature_mock = _create_feature_mock(
                "feature_text",
                "Text Feature",
                "text.feature",
                "Test text and table functionality",
                ["text", "table"],
            )
            record_feature(feature_mock)

            ctx_mock = _create_scenario_context_mock(
                "scenario_text",
                "feature_text",
                "Text scenario",
                ["test"],
                "2024-01-01T10:00:00",
            )
            ctx_mock.step_index = 0
            record_scenario(ctx_mock)

            # Test step with text content
            step_with_text = _create_step_mock(
                "step_with_text",
                "Given",
                "I have a step with text",
                "text.feature:10",
                "2024-01-01T10:00:00",
                has_substeps=False,
                is_substep=False,
                text="This is some text content\nWith multiple lines\nAnd more text",
            )
            start_step_record(ctx_mock, step_with_text)

            # Test step with table data
            table_mock = mock.MagicMock()
            table_mock.headings = ["header1", "header2", "header3"]
            table_mock.rows = [
                mock.MagicMock(cells=["value1", "value2", "value3"]),
                mock.MagicMock(cells=["data1", "data2", "data3"]),
            ]

            ctx_mock.step_index = 1
            step_with_table = _create_step_mock(
                "step_with_table",
                "When",
                "I have a step with table",
                "text.feature:15",
                "2024-01-01T10:01:00",
                has_substeps=True,
                is_substep=False,
                table=table_mock,
            )
            start_step_record(ctx_mock, step_with_table)

            # Test substep
            ctx_mock.step_index = 2
            substep = _create_step_mock(
                "substep_001",
                "And",
                "I am a substep",
                "text.feature:20",
                "2024-01-01T10:02:00",
                has_substeps=False,
                is_substep=True,
            )
            start_step_record(ctx_mock, substep)

            # Verify the data was recorded correctly
            with sqlite3.connect(db_filepath) as conn:
                cursor = conn.cursor()

                # Check step with text
                cursor.execute(
                    "SELECT name, text, table_data, is_substep, has_substeps FROM steps WHERE step_run_id = ?",
                    ("step_with_text",),
                )
                result = cursor.fetchone()
                assert result is not None
                name, text, table_data, is_substep, has_substeps = result
                assert name == "I have a step with text"
                assert (
                    text
                    == "This is some text content\nWith multiple lines\nAnd more text"
                )
                assert table_data is None
                assert is_substep == 0  # SQLite stores False as 0
                assert has_substeps == 0  # SQLite stores False as 0

                # Check step with table
                cursor.execute(
                    "SELECT name, text, table_data, is_substep, has_substeps FROM steps WHERE step_run_id = ?",
                    ("step_with_table",),
                )
                result = cursor.fetchone()
                assert result is not None
                name, text, table_data, is_substep, has_substeps = result
                assert name == "I have a step with table"
                assert text is None
                assert table_data is not None

                import json

                table_data_parsed = json.loads(table_data)
                assert table_data_parsed == [
                    ["header1", "header2", "header3"],
                    ["value1", "value2", "value3"],
                    ["data1", "data2", "data3"],
                ]
                assert is_substep == 0  # SQLite stores False as 0
                assert has_substeps == 1  # SQLite stores True as 1

                # Check substep
                cursor.execute(
                    "SELECT name, text, table_data, is_substep, has_substeps FROM steps WHERE step_run_id = ?",
                    ("substep_001",),
                )
                result = cursor.fetchone()
                assert result is not None
                name, text, table_data, is_substep, has_substeps = result
                assert name == "I am a substep"
                assert text is None
                assert table_data is None
                assert is_substep == 1  # SQLite stores True as 1
                assert has_substeps == 0  # SQLite stores False as 0

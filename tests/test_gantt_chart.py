from datetime import datetime, timedelta

from cucu.reporter.html import build_gantt_chart, format_gantt_duration

T0 = datetime(2026, 9, 18, 12, 0, 0)


def _feature(
    name,
    scenarios,
    worker_id="w1",
    worker_start=T0,
    run_id="r1",
    run_file=None,
):
    return {
        "name": name,
        "folder_name": name,
        "worker": {
            "worker_run_id": worker_id,
            "start_at": worker_start,
            "cucu_run": {
                "cucu_run_id": run_id,
                "filepath": run_file or f"features/{run_id}",
                "full_arguments": ["cucu", "run", run_file or run_id],
            },
        },
        "scenarios": scenarios,
    }


def _scenario(name, status, start, end, keyword=None):
    return {
        "name": name,
        "status": status,
        "start_at": start,
        "end_at": end,
        "duration": (end - start).total_seconds() if start and end else None,
        "folder_name": name,
        "keyword": keyword,
    }


def test_build_gantt_chart_positions_bars_and_skips_background():
    t0 = datetime(2026, 9, 18, 12, 0, 0)
    features = [
        {
            "name": "Feature A",
            "folder_name": "Feature A",
            "scenarios": [
                _scenario(
                    "Background",
                    "passed",
                    t0,
                    t0 + timedelta(seconds=1),
                    "Background",
                ),
                _scenario("First", "passed", t0, t0 + timedelta(seconds=10)),
                _scenario(
                    "Second",
                    "failed",
                    t0 + timedelta(seconds=10),
                    t0 + timedelta(seconds=20),
                ),
                _scenario("Untimed", "skipped", None, None),
            ],
        }
    ]

    gantt = build_gantt_chart(features)

    names = [row["name"] for row in gantt["rows"]]
    assert names == ["First", "Second"]
    assert gantt["rows"][0]["left_pct"] == 0.0
    assert gantt["rows"][0]["width_pct"] == 50.0
    assert gantt["rows"][1]["left_pct"] == 50.0
    assert gantt["rows"][1]["width_pct"] == 50.0
    assert gantt["rows"][1]["status"] == "failed"
    assert gantt["rows"][0]["duration_label"] == "10s"
    assert gantt["rows"][1]["duration_label"] == "10s"
    assert (
        gantt["rows"][0]["bar_title"]
        == "passed — 2026-09-18 12:00:00 – 2026-09-18 12:00:10 — 10s — Worker 1"
    )
    assert gantt["untimed_count"] == 1
    assert gantt["span_s"] == 20.0
    assert gantt["run_start_clock_s"] == 12 * 3600
    assert gantt["status_counts"] == {
        "passed": 1,
        "failed": 1,
        "error": 0,
        "skipped": 0,
        "untested": 0,
    }
    assert [(w["key"], w["label"]) for w in gantt["workers"]] == [
        ("1.1", "Worker 1")
    ]
    assert len(gantt["runs"]) == 1


def test_build_gantt_chart_keeps_bars_inside_timeline():
    t0 = datetime(2026, 9, 18, 12, 0, 0)
    features = [
        {
            "name": "Feature A",
            "folder_name": "Feature A",
            "scenarios": [
                _scenario("First", "passed", t0, t0 + timedelta(seconds=10)),
                _scenario(
                    "Instant at end",
                    "passed",
                    t0 + timedelta(seconds=10),
                    t0 + timedelta(seconds=10),
                ),
            ],
        }
    ]

    gantt = build_gantt_chart(features)

    for row in gantt["rows"]:
        assert row["width_pct"] >= 0
        assert row["left_pct"] + row["width_pct"] <= 100


def test_format_gantt_duration():
    assert format_gantt_duration(0) == "0s"
    assert format_gantt_duration(0.039) == "39ms"
    assert format_gantt_duration(3) == "3s"
    assert format_gantt_duration(123) == "2m 3s"
    assert format_gantt_duration(271.9) == "4m 32s"
    assert format_gantt_duration(3600) == "1h"
    assert format_gantt_duration(3723) == "1h 2m 3s"


def test_build_gantt_chart_empty():
    gantt = build_gantt_chart([])
    assert gantt["rows"] == []
    assert gantt["status_counts"] == {}
    assert gantt["untimed_count"] == 0


def test_build_gantt_chart_numbers_workers_by_start_time():
    later = T0 + timedelta(seconds=5)
    features = [
        _feature(
            "Late worker",
            [_scenario("B", "error", later, later + timedelta(seconds=5))],
            worker_id="zzz",
            worker_start=later,
        ),
        _feature(
            "Early worker",
            [
                _scenario("A", "passed", T0, T0 + timedelta(seconds=3)),
                _scenario("C", "terminated", T0, T0 + timedelta(seconds=10)),
            ],
            worker_id="aaa",
        ),
    ]

    gantt = build_gantt_chart(features)

    workers = {row["name"]: row["worker"] for row in gantt["rows"]}
    assert workers == {"A": 1, "C": 1, "B": 2}
    assert [w["key"] for w in gantt["workers"]] == ["1.1", "1.2"]
    assert gantt["status_counts"]["terminated"] == 1
    assert gantt["status_counts"]["error"] == 1


def test_build_gantt_chart_duration_label_matches_bar():
    scenario = _scenario("A", "passed", T0, T0 + timedelta(seconds=61))
    scenario["duration"] = 3.0
    gantt = build_gantt_chart([_feature("F", [scenario])])
    assert gantt["rows"][0]["duration_label"] == "1m 1s"


def test_build_gantt_chart_numbers_runs_and_workers_within_runs():
    later = T0 + timedelta(hours=2)
    features = [
        _feature(
            "Second run",
            [_scenario("B", "failed", later, later + timedelta(seconds=20))],
            worker_id="w-b",
            worker_start=later,
            run_id="run-b",
            run_file="b.feature",
        ),
        _feature(
            "First run",
            [_scenario("A", "passed", T0, T0 + timedelta(seconds=10))],
            worker_id="w-a",
            run_id="run-a",
            run_file="a.feature",
        ),
    ]

    gantt = build_gantt_chart(features)

    rows = {row["name"]: row for row in gantt["rows"]}
    assert (rows["A"]["run"], rows["A"]["worker_key"]) == (1, "1.1")
    assert (rows["B"]["run"], rows["B"]["worker_key"]) == (2, "2.1")
    assert [(r["number"], r["label"]) for r in gantt["runs"]] == [
        (1, "a.feature"),
        (2, "b.feature"),
    ]
    assert [w["label"] for w in gantt["workers"]] == ["R1-W1", "R2-W1"]
    assert rows["B"]["bar_title"].endswith("— R2-W1 — b.feature")


def test_build_gantt_chart_aligns_runs_at_their_own_start():
    later = T0 + timedelta(hours=1)
    features = [
        _feature(
            "First run",
            [_scenario("A", "passed", T0, T0 + timedelta(seconds=10))],
            run_id="run-a",
        ),
        _feature(
            "Second run",
            [
                _scenario("B", "passed", later, later + timedelta(seconds=5)),
                _scenario(
                    "C",
                    "passed",
                    later + timedelta(seconds=15),
                    later + timedelta(seconds=20),
                ),
            ],
            worker_id="w2",
            worker_start=later,
            run_id="run-b",
        ),
    ]

    gantt = build_gantt_chart(features)

    rows = {row["name"]: row for row in gantt["rows"]}
    assert gantt["span_s"] == 3620.0
    assert gantt["aligned_span_s"] == 20.0
    assert rows["A"]["aligned_left_pct"] == 0.0
    assert rows["A"]["aligned_width_pct"] == 50.0
    assert rows["B"]["aligned_left_pct"] == 0.0
    assert rows["C"]["aligned_left_pct"] == 75.0
    assert rows["C"]["aligned_width_pct"] == 25.0


def test_build_gantt_chart_disambiguates_duplicate_run_labels():
    later = T0 + timedelta(minutes=5)
    features = [
        _feature(
            "F1",
            [_scenario("A", "passed", T0, T0 + timedelta(seconds=1))],
            run_id="run-a",
            run_file="same.feature",
        ),
        _feature(
            "F2",
            [_scenario("B", "passed", later, later + timedelta(seconds=1))],
            run_id="run-b",
            run_file="same.feature",
        ),
    ]

    labels = [run["label"] for run in build_gantt_chart(features)["runs"]]

    assert labels == ["same.feature @ 12:00:00", "same.feature @ 12:05:00"]

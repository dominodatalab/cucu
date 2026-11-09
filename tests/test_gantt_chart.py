from datetime import datetime, timedelta

from cucu.reporter.html import build_gantt_chart, format_gantt_duration

T0 = datetime(2026, 9, 18, 12, 0, 0)


def _feature(name, scenarios, worker_id="w1", worker_start=T0):
    return {
        "name": name,
        "folder_name": name,
        "worker": {"worker_run_id": worker_id, "start_at": worker_start},
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
        == "passed — 2026-09-18 12:00:00 – 2026-09-18 12:00:10 — 10s — worker 1"
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
    assert gantt["worker_counts"] == {1: 2}


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
    assert gantt["worker_counts"] == {1: 2, 2: 1}
    assert gantt["status_counts"]["terminated"] == 1
    assert gantt["status_counts"]["error"] == 1


def test_build_gantt_chart_duration_label_matches_bar():
    scenario = _scenario("A", "passed", T0, T0 + timedelta(seconds=61))
    scenario["duration"] = 3.0
    gantt = build_gantt_chart([_feature("F", [scenario])])
    assert gantt["rows"][0]["duration_label"] == "1m 1s"

from datetime import datetime, timedelta

from cucu.reporter.html import build_gantt_chart, format_gantt_duration


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
        == "passed — 2026-09-18 12:00:00 – 2026-09-18 12:00:10 — 10s"
    )
    assert len(gantt["ticks"]) == 6


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
    assert format_gantt_duration(3) == "3s"
    assert format_gantt_duration(123) == "2m 3s"
    assert format_gantt_duration(271.9) == "4m 32s"
    assert format_gantt_duration(3600) == "1h"
    assert format_gantt_duration(3723) == "1h 2m 3s"


def test_build_gantt_chart_empty():
    gantt = build_gantt_chart([])
    assert gantt["rows"] == []
    assert gantt["ticks"] == []

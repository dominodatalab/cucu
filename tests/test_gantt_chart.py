from datetime import datetime, timedelta

import pytest
import pytest_check as check

from cucu.reporter.html import build_gantt_chart, format_gantt_duration

T0 = datetime(2026, 9, 18, 12, 0, 0)


def at(seconds):
    return T0 + timedelta(seconds=seconds)


def scenario(name, status, start, end, steps=(), hooks=None):
    return {
        "scenario_run_id": f"id-{name}",
        "name": name,
        "status": status,
        "start_at": start,
        "end_at": end,
        "folder_name": name,
        "steps": list(steps),
        "after_hooks": hooks,
    }


def feature(
    name, scenarios, worker="w1", worker_start=T0, run="r1", run_file=None
):
    return {
        "name": name,
        "folder_name": name,
        "worker": {
            "worker_run_id": worker,
            "start_at": worker_start,
            "cucu_run": {
                "cucu_run_id": run,
                "filepath": f"features/{run_file or run + '.feature'}",
                "full_arguments": ["cucu", "run", run],
            },
        },
        "scenarios": scenarios,
    }


def step(name, status, start, end, is_substep=False):
    return {
        "keyword": "Given",
        "name": name,
        "status": status,
        "is_substep": is_substep,
        "start_at": start,
        "end_at": end,
    }


def hook(name, status, start, end):
    return {
        "name": name,
        "status": status,
        "start_at": start.isoformat(),
        "end_at": end.isoformat(),
    }


def rows_by_name(gantt):
    return {row["name"]: row for row in gantt["rows"]}


@pytest.mark.parametrize(
    "seconds, expected",
    [
        pytest.param(0, "0s", id="zero"),
        pytest.param(0.039, "39ms", id="sub-second"),
        pytest.param(3, "3s", id="seconds"),
        pytest.param(123, "2m 3s", id="minutes"),
        pytest.param(271.9, "4m 32s", id="rounds"),
        pytest.param(3600, "1h", id="hour"),
        pytest.param(3723, "1h 2m 3s", id="all-units"),
    ],
)
def test_format_gantt_duration(seconds, expected):
    assert format_gantt_duration(seconds) == expected


def test_build_gantt_chart_empty():
    gantt = build_gantt_chart([])
    check.equal(gantt["rows"], [])
    check.equal(gantt["status_counts"], {})
    check.equal(gantt["untimed_count"], 0)


def test_build_gantt_chart_places_bars_and_counts():
    gantt = build_gantt_chart(
        [
            feature(
                "F",
                [
                    scenario("First", "passed", T0, at(10)),
                    scenario("Second", "failed", at(10), at(20)),
                    scenario("Untimed", "skipped", None, None),
                    scenario("Instant at end", "passed", at(20), at(20)),
                ],
            )
        ]
    )
    rows = rows_by_name(gantt)

    check.equal(
        [row["name"] for row in gantt["rows"]],
        ["First", "Second", "Instant at end"],
    )
    check.equal(
        (rows["First"]["left_pct"], rows["First"]["width_pct"]), (0.0, 50.0)
    )
    check.equal(
        (rows["Second"]["left_pct"], rows["Second"]["width_pct"]), (50.0, 50.0)
    )
    check.less_equal(
        rows["Instant at end"]["left_pct"]
        + rows["Instant at end"]["width_pct"],
        100,
    )
    check.equal(rows["First"]["duration_label"], "10s")
    check.equal(
        rows["First"]["bar_title"],
        "passed — 2026-09-18 12:00:00 – 2026-09-18 12:00:10 — 10s — R1-W1",
    )
    check.equal(gantt["untimed_count"], 1)
    check.equal(gantt["span_s"], 20.0)
    check.equal(gantt["run_start_clock_s"], 12 * 3600)
    check.equal(
        gantt["status_counts"],
        {"passed": 2, "failed": 1, "error": 0, "skipped": 0, "terminated": 0},
    )
    check.equal(
        [(w["key"], w["label"]) for w in gantt["workers"]], [("1.1", "R1-W1")]
    )
    check.is_false(gantt["multi_run"])


def test_build_gantt_chart_numbers_workers_and_runs_by_start_time():
    later = at(7200)
    gantt = build_gantt_chart(
        [
            feature(
                "Late worker",
                [scenario("B", "error", at(5), at(10))],
                worker="zzz",
                worker_start=at(5),
            ),
            feature(
                "Early worker",
                [scenario("A", "terminated", T0, at(3))],
                worker="aaa",
            ),
            feature(
                "Second run",
                [scenario("C", "failed", later, at(7220))],
                worker="w-c",
                worker_start=later,
                run="b",
            ),
        ]
    )
    rows = rows_by_name(gantt)

    check.equal(
        {name: row["worker_key"] for name, row in rows.items()},
        {"A": "1.1", "B": "1.2", "C": "2.1"},
    )
    check.equal(rows["C"]["worker_badge"], "R2-W1")
    check.equal(
        [(run["number"], run["label"]) for run in gantt["runs"]],
        [(1, "r1.feature"), (2, "b.feature")],
    )
    check.equal(
        [w["label"] for w in gantt["workers"]], ["R1-W1", "R1-W2", "R2-W1"]
    )
    check.is_true(rows["C"]["bar_title"].endswith("— R2-W1 — b.feature"))
    check.equal(gantt["status_counts"]["terminated"], 1)
    check.is_true(gantt["multi_run"])


def test_build_gantt_chart_aligns_runs_at_their_own_start():
    later = at(3600)
    gantt = build_gantt_chart(
        [
            feature(
                "First run", [scenario("A", "passed", T0, at(10))], run="a"
            ),
            feature(
                "Second run",
                [
                    scenario("B", "passed", later, at(3605)),
                    scenario("C", "passed", at(3615), at(3620)),
                ],
                worker="w2",
                worker_start=later,
                run="b",
            ),
        ]
    )
    rows = rows_by_name(gantt)

    check.equal(gantt["span_s"], 3620.0)
    check.equal(gantt["aligned_span_s"], 20.0)
    check.equal(
        (rows["A"]["aligned_left_pct"], rows["A"]["aligned_width_pct"]),
        (0.0, 50.0),
    )
    check.equal(rows["B"]["aligned_left_pct"], 0.0)
    check.equal(
        (rows["C"]["aligned_left_pct"], rows["C"]["aligned_width_pct"]),
        (75.0, 25.0),
    )


def test_build_gantt_chart_disambiguates_duplicate_run_labels():
    gantt = build_gantt_chart(
        [
            feature(
                "F1",
                [scenario("A", "passed", T0, at(1))],
                run="a",
                run_file="same.feature",
            ),
            feature(
                "F2",
                [scenario("B", "passed", at(300), at(301))],
                run="b",
                run_file="same.feature",
            ),
        ]
    )
    assert [run["label"] for run in gantt["runs"]] == [
        "same.feature @ 12:00:00",
        "same.feature @ 12:05:00",
    ]


def test_build_gantt_chart_builds_step_and_cleanup_segments():
    gantt = build_gantt_chart(
        [
            feature(
                "F",
                [
                    scenario(
                        "A",
                        "error",
                        T0,
                        at(10),
                        steps=[
                            step("I pass", "passed", at(1), at(3)),
                            step(
                                "I am nested",
                                "passed",
                                at(1),
                                at(2),
                                is_substep=True,
                            ),
                            step("I am skipped", "skipped", None, None),
                        ],
                        hooks=[hook("cleanup", "error", at(5), at(10))],
                    ),
                    scenario(
                        "B",
                        "passed",
                        at(10),
                        at(20),
                        hooks=[hook("late", "passed", at(20), at(30))],
                    ),
                ],
            )
        ]
    )
    rows = rows_by_name(gantt)
    segments = rows["A"]["segments"]

    check.equal(
        [(seg["status"], seg["cleanup"]) for seg in segments],
        [("passed", False), ("error", True)],
    )
    check.equal(
        (segments[0]["left_pct"], segments[0]["width_pct"]), (10.0, 20.0)
    )
    check.equal(segments[1]["left_pct"], 50.0)
    check.equal(rows["A"]["cleanup_ratio"], 2.0)
    check.equal(rows["A"]["duration_label"], "10s")
    check.equal(
        gantt["span_s"], 30.0, msg="bars extend to the last cleanup hook"
    )
    check.equal(rows["B"]["cleanup_ratio"], 2.0)

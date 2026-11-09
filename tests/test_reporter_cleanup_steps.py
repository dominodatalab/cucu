"""
Tests for build_cleanup_steps in cucu.reporter.html, which turns a scenario's
after_hooks results (selenium keep-alive, MHT download, user after_scenario/
after_this_scenario hooks, browser cleanup) into step-like dicts the replay view
places on the timeline after the last real step.
"""

from datetime import datetime, timezone

import pytest_check as check

from cucu.reporter.html import build_cleanup_steps

SCENARIO_START_AT = datetime(2026, 1, 1, 12, 0, 0)


def test_build_cleanup_steps_empty_after_hooks():
    check.equal(build_cleanup_steps([], SCENARIO_START_AT), [])
    check.equal(build_cleanup_steps(None, SCENARIO_START_AT), [])


def test_build_cleanup_steps_computes_offset_and_duration():
    after_hooks = [
        {
            "name": "cleanup_browsers",
            "status": "passed",
            "stdout": [],
            "stderr": [],
            "error_message": [],
            "start_at": "2026-01-01T12:00:01.000",
            "end_at": "2026-01-01T12:00:01.250",
        }
    ]

    [cleanup_step] = build_cleanup_steps(after_hooks, SCENARIO_START_AT)

    check.equal(cleanup_step["name"], "cleanup_browsers")
    check.equal(cleanup_step["status"], "passed")
    check.equal(cleanup_step["duration"], 0.25)
    check.equal(
        cleanup_step["time_offset"],
        datetime.fromtimestamp(1.0, timezone.utc),
    )


def test_build_cleanup_steps_missing_hook_timing_leaves_offset_blank():
    after_hooks = [
        {
            "name": "start_selenium_keep_alive",
            "status": "error",
            "error_message": ["boom"],
        }
    ]

    [cleanup_step] = build_cleanup_steps(after_hooks, SCENARIO_START_AT)

    check.equal(cleanup_step["status"], "error")
    check.equal(cleanup_step["error_message"], ["boom"])
    check.equal(cleanup_step["duration"], 0.0)
    check.equal(cleanup_step["time_offset"], "")


def test_build_cleanup_steps_missing_scenario_start_at_still_computes_duration():
    # the hook's own duration is derivable from its start_at/end_at alone, so a missing
    # scenario_start_at should only blank the offset, not the duration
    after_hooks = [
        {
            "name": "download_mht_data",
            "status": "passed",
            "start_at": "2026-01-01T12:00:01.000",
            "end_at": "2026-01-01T12:00:01.100",
        }
    ]

    [cleanup_step] = build_cleanup_steps(after_hooks, None)

    check.equal(cleanup_step["duration"], 0.1)
    check.equal(cleanup_step["time_offset"], "")


def test_build_cleanup_steps_clamps_negative_offset_to_zero():
    # a hook can start a hair before scenario_start_at due to timing, same as steps
    after_hooks = [
        {
            "name": "stop_selenium_keep_alive",
            "status": "passed",
            "start_at": "2026-01-01T11:59:59.900",
            "end_at": "2026-01-01T12:00:00.100",
        }
    ]

    [cleanup_step] = build_cleanup_steps(after_hooks, SCENARIO_START_AT)

    check.equal(
        cleanup_step["time_offset"],
        datetime.fromtimestamp(0.0, timezone.utc),
    )

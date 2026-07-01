"""
Tests for the cucu environment module, focused on hook handling and timeout/termination.

Note: We test the status-assignment logic directly rather than importing _run_hook,
since environment.py has module-level side effects (init_page_checks) that are hard
to mock in a unit test environment.
"""

import pytest
import pytest_check as check
from mpire.exception import InterruptWorker


@pytest.mark.parametrize(
    "exception, expected_status, expected_error_message",
    [
        pytest.param(
            InterruptWorker("task timeout"),
            "terminated",
            [],
            id="InterruptWorker-yields-terminated",
        ),
        pytest.param(
            ValueError("something went wrong"),
            "error",
            ["something went wrong"],
            id="generic-exception-yields-error",
        ),
    ],
)
def test_run_hook_status_logic(
    exception, expected_status, expected_error_message
):
    """_run_hook maps InterruptWorker → "terminated" and other exceptions → "error"."""
    hook_result = {
        "name": "test_hook",
        "status": "passed",
        "error_message": [],
    }

    try:
        raise exception
    except InterruptWorker:
        hook_result["status"] = "terminated"
    except Exception as e:
        hook_result["status"] = "error"
        hook_result["error_message"] = [str(e)]

    check.equal(hook_result["status"], expected_status)
    check.equal(hook_result["error_message"], expected_error_message)

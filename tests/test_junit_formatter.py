"""
Tests for the cucu JUnit formatter, focused on the per-<testcase> child element
that standard JUnit consumers use to classify results: <failure>, <error>,
<skipped>, or none (passed).
"""

import xml.etree.ElementTree as ET

import pytest
import pytest_check as check
from behave.formatter.base import StreamOpener
from behave.model_core import Status

from cucu.config import CONFIG
from cucu.formatter.junit import CucuJUnitFormatter


class StubStatus:
    """stand-in for the object returned by scenario.compute_status()"""

    def __init__(self, name):
        self.name = name


class StubFeature:
    def __init__(self, name, tags=None):
        self.name = name
        self.tags = tags or []


class StubScenario:
    def __init__(
        self,
        name,
        status="passed",
        hook_failed=False,
        terminated=False,
        tags=None,
        before_hook_results=None,
        after_hook_results=None,
    ):
        self.name = name
        self._status = status
        self.hook_failed = hook_failed
        self.terminated = terminated
        self.tags = tags or []
        self.before_hook_results = before_hook_results or []
        self.after_hook_results = after_hook_results or []

    def compute_status(self):
        return StubStatus(self._status)


class StubStep:
    def __init__(
        self,
        status,
        duration=0.1,
        keyword="When",
        name="I do a thing",
        exception=None,
        exc_traceback=None,
    ):
        self.status = status
        self.duration = duration
        self.keyword = keyword
        self.name = name
        self.exception = exception
        self.exc_traceback = exc_traceback


@pytest.fixture
def junit_env(tmp_path):
    """
    point the JUnit formatter at a temp dir and set the CONFIG keys it reads,
    restoring the originals afterward
    """
    keys = {
        "CUCU_JUNIT_DIR": str(tmp_path),
        "CUCU_SHOW_SKIPS": "true",
        "CUCU_JUNIT_WITH_STACKTRACE": "false",
        "__CUCU_CUSTOM_FAILURE_HANDLERS": [],
    }
    originals = {key: CONFIG[key] for key in keys}
    for key, value in keys.items():
        CONFIG[key] = value

    yield tmp_path

    for key, value in originals.items():
        CONFIG[key] = value


def _run_feature(tmp_path, feature, scenario, step=None):
    """
    drive the formatter through a single scenario and return the parsed
    <testsuite> element from the written XML
    """
    formatter = CucuJUnitFormatter(StreamOpener(filename="unused"), None)
    formatter.feature(feature)
    formatter.scenario(scenario)
    if step is not None:
        formatter.result(step)
    formatter.eof()

    output = (tmp_path / f"{feature.name}.xml").read_text()
    return ET.fromstring(output)


def test_passed_scenario_has_no_child_element(junit_env):
    feature = StubFeature("passing feature")
    scenario = StubScenario("a passing scenario", status="passed")
    step = StubStep(Status.passed)

    testsuite = _run_feature(junit_env, feature, scenario, step)
    testcase = testsuite.find("testcase")

    check.equal(testcase.get("status"), "passed")
    check.is_none(testcase.find("failure"), "passed must not emit <failure>")
    check.is_none(testcase.find("error"), "passed must not emit <error>")
    check.is_none(testcase.find("skipped"), "passed must not emit <skipped>")
    check.equal(testsuite.get("errors"), "0")
    check.equal(testsuite.get("failures"), "0")


def test_failed_scenario_emits_failure_only(junit_env):
    feature = StubFeature("failing feature")
    scenario = StubScenario("a failing scenario", status="failed")

    try:
        raise RuntimeError("assertion did not hold")
    except RuntimeError as error:
        step = StubStep(
            Status.failed, exception=error, exc_traceback=error.__traceback__
        )

    testsuite = _run_feature(junit_env, feature, scenario, step)
    testcase = testsuite.find("testcase")

    check.equal(testcase.get("status"), "failed")
    check.is_not_none(testcase.find("failure"), "failed must emit <failure>")
    check.is_none(testcase.find("error"), "failed must not emit <error>")
    check.is_in("assertion did not hold", testcase.find("failure").text)
    check.equal(testsuite.get("failures"), "1")
    check.equal(testsuite.get("errors"), "0")


def test_errored_scenario_emits_error_child(junit_env):
    # model the real path: a before-scenario hook failure with no step run
    feature = StubFeature("erroring feature")
    hook_message = [
        "HOOK-ERROR in before_scenario: ValueError: boom",
        "Traceback (most recent call last):",
        "  ...",
    ]
    scenario = StubScenario(
        "an erroring scenario",
        hook_failed=True,
        before_hook_results=[
            {"status": "error", "error_message": hook_message}
        ],
    )

    testsuite = _run_feature(junit_env, feature, scenario, step=None)
    testcase = testsuite.find("testcase")

    check.equal(testcase.get("status"), "error")
    error_element = testcase.find("error")
    check.is_not_none(error_element, "errored scenario must emit <error>")
    check.is_none(testcase.find("failure"), "errored must not emit <failure>")
    if error_element is not None:
        check.is_true(error_element.text.strip(), "<error> must not be empty")
        check.is_in("HOOK-ERROR in before_scenario", error_element.text)
    check.equal(testsuite.get("errors"), "1")
    check.equal(testsuite.get("failures"), "0")


def test_skipped_scenario_emits_skipped_only(junit_env):
    feature = StubFeature("skipping feature")
    scenario = StubScenario("a skipped scenario", status="skipped")

    testsuite = _run_feature(junit_env, feature, scenario, step=None)
    testcase = testsuite.find("testcase")

    check.equal(testcase.get("status"), "skipped")
    check.is_not_none(testcase.find("skipped"), "skipped must emit <skipped>")
    check.is_none(testcase.find("failure"), "skipped must not emit <failure>")
    check.is_none(testcase.find("error"), "skipped must not emit <error>")
    check.equal(testsuite.get("skipped"), "1")
    check.equal(testsuite.get("errors"), "0")


def test_terminated_scenario_has_terminated_status(junit_env):
    # model the real path: scenario terminated via InterruptWorker timeout
    feature = StubFeature("timing out feature")
    scenario = StubScenario(
        "a terminated scenario",
        status="passed",
        terminated=True,
        hook_failed=False,
    )

    testsuite = _run_feature(junit_env, feature, scenario, step=None)
    testcase = testsuite.find("testcase")

    check.equal(testcase.get("status"), "terminated")
    check.is_none(testcase.find("error"), "terminated must not emit <error>")
    check.is_none(testcase.find("failure"), "terminated must not emit <failure>")
    check.is_none(testcase.find("skipped"), "terminated must not emit <skipped>")

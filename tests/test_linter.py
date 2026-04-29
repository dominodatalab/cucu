import pytest
import pytest_check as check

from cucu.config import CONFIG
from cucu.lint import linter
from cucu.lint.linter import lint_line


@pytest.mark.parametrize(
    "rule_extras, scenario_tags, feature_tags, filepath, expect_violation",
    [
        pytest.param(
            {},
            set(),
            set(),
            "/tmp/foo.feature",
            True,
            id="rule fires when no exclusions configured",
        ),
        pytest.param(
            {"exclude_tags": ["@no-lint"]},
            {"@no-lint"},
            set(),
            "/tmp/foo.feature",
            False,
            id="scenario tag matching exclude_tags skips rule",
        ),
        pytest.param(
            {"exclude_tags": ["@no-lint"]},
            set(),
            {"@no-lint"},
            "/tmp/foo.feature",
            False,
            id="feature tag matching exclude_tags skips rule",
        ),
        pytest.param(
            {"exclude_tags": ["@no-lint"]},
            {"@other-tag"},
            set(),
            "/tmp/foo.feature",
            True,
            id="non-overlapping tags do not skip rule",
        ),
        pytest.param(
            {"exclude": ".*excluded.*"},
            set(),
            set(),
            "/tmp/excluded.feature",
            False,
            id="filepath exclude alone skips rule",
        ),
        pytest.param(
            {"exclude_tags": ["@skip"]},
            {"@skip"},
            set(),
            "/tmp/whatever.feature",
            False,
            id="exclude_tags alone skips rule",
        ),
    ],
)
def test_lint_line_rule_short_circuit(
    rule_extras, scenario_tags, feature_tags, filepath, expect_violation
):
    rule = {
        "type": "error",
        "message": "test rule fired",
        "current_line": {"match": "^trigger$"},
        **rule_extras,
    }
    rules = {"test_rule": rule}
    state = {
        "current_scenario_tags": scenario_tags,
        "current_feature_tags": feature_tags,
    }
    violations = lint_line(state, rules, {}, 0, ["trigger"], filepath)
    if expect_violation:
        check.equal(len(violations), 1, "expected exactly one violation")
    else:
        check.equal(violations, [], "expected no violations")


_CLICK_RULE = {
    "type": "error",
    "message": "click without wait",
    "exclude_tags": ["@allow-clicks"],
    "previous_line": {"match": ".* I click the (.*)"},
    "current_line": {"match": "^((?!wait to).)*$"},
}

_TAGGED_SCENARIO = (
    "Feature: foo\n"
    "\n"
    "  @allow-clicks\n"
    "  Scenario: tagged\n"
    "    Given I click the button\n"
    "    Then I click the button\n"
    "    Then I wait to see done\n"
)

_UNTAGGED_SCENARIO = (
    "Feature: foo\n"
    "\n"
    "  Scenario: untagged\n"
    "    Given I click the button\n"
    "    Then I click the button\n"
    "    Then I wait to see done\n"
)

_TAGGED_FEATURE = (
    "@allow-clicks\n"
    "Feature: foo\n"
    "\n"
    "  Scenario: any\n"
    "    Given I click the button\n"
    "    Then I click the button\n"
    "    Then I wait to see done\n"
)

_MIXED_SCENARIOS = (
    "Feature: foo\n"
    "\n"
    "  @allow-clicks\n"
    "  Scenario: tagged\n"
    "    Given I click the button\n"
    "    Then I click the button\n"
    "    Then I wait to see done\n"
    "\n"
    "  Scenario: untagged\n"
    "    Given I click the button\n"
    "    Then I click the button\n"
    "    Then I wait to see done\n"
)

_TAGGED_OUTLINE = (
    "Feature: foo\n"
    "\n"
    "  @allow-clicks\n"
    "  Scenario Outline: tagged outline\n"
    "    Given I click the button\n"
    "    Then I click the button\n"
    "    Then I wait to see done\n"
)


def _run_lint(tmp_path, monkeypatch, content):
    feature_path = tmp_path / "test.feature"
    feature_path.write_text(content)

    monkeypatch.setattr(
        linter, "load_cucu_steps", lambda filepath=None: ({}, None)
    )
    monkeypatch.setattr(
        linter,
        "load_builtin_lint_rules",
        lambda rules: rules.update({"test_rule": _CLICK_RULE}),
    )
    monkeypatch.setitem(CONFIG, "CUCU_LINT_RULES_PATH", None)

    return list(linter.lint(str(feature_path)))


@pytest.mark.parametrize(
    "content, expected_violation_lines",
    [
        pytest.param(
            _TAGGED_SCENARIO,
            [],
            id="scenario tagged with exclude tag suppresses violations",
        ),
        pytest.param(
            _UNTAGGED_SCENARIO,
            [4],
            id="untagged scenario reports violation",
        ),
        pytest.param(
            _TAGGED_FEATURE,
            [],
            id="feature-level tag suppresses violations in every scenario",
        ),
        pytest.param(
            _MIXED_SCENARIOS,
            [10],
            id="mixed feature reports only the untagged scenario",
        ),
        pytest.param(
            _TAGGED_OUTLINE,
            [],
            id="Scenario Outline participates in tag attribution",
        ),
    ],
)
def test_lint_attributes_tags_to_scope(
    tmp_path, monkeypatch, content, expected_violation_lines
):
    [violations] = _run_lint(tmp_path, monkeypatch, content)
    actual_lines = [v["location"]["line"] for v in violations]
    check.equal(
        actual_lines,
        expected_violation_lines,
        f"violation lines mismatch: got {actual_lines}",
    )

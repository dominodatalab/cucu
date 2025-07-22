import tempfile

import pytest
import pytest_check as check

import cucu
from cucu.config import CONFIG, Config, leaf_map


def test_config_lookup_for_inexistent_is_none():
    assert CONFIG["INEXISTENT"] is None


def test_config_lookup_env_works():
    assert CONFIG["HOME"] is not None


def test_config_lookup_env_precedes_internal_value():
    env_value = CONFIG["HOME"]
    CONFIG["HOME"] = "foo"
    assert CONFIG["HOME"] == env_value


def test_config_true_method():
    CONFIG["VAR1"] = "true"
    check.is_true(
        CONFIG.true("VAR1"), "Config should recognize 'true' as true"
    )
    check.is_false(
        CONFIG.true("INEXISTENT"), "Non-existent config should return False"
    )


def test_config_false_method():
    CONFIG["VAR1"] = "false"
    check.is_true(
        CONFIG.false("VAR1"), "Config should recognize 'false' as false"
    )
    CONFIG["VAR1"] = "true"
    check.is_false(
        CONFIG.false("VAR1"), "Config should not treat 'true' as false"
    )
    check.is_true(
        CONFIG.false("INEXISTENT"),
        "Non-existent config should return True for false()",
    )


def test_config_resolves_variables():
    CONFIG["VAR1"] = "foo"
    CONFIG["VAR2"] = "bar"
    assert CONFIG.resolve("{VAR1} and {VAR2}") == "foo and bar"


def test_config_resolve_leaves_unresolved_variables():
    assert CONFIG.resolve("{NOT_SET}") == ""


def test_config_push_and_pop_works():
    CONFIG["FOO"] = None
    CONFIG.snapshot()
    CONFIG["FOO"] = "bar"
    assert CONFIG["FOO"] == "bar"
    CONFIG.restore(with_pop=True)
    assert CONFIG["FOO"] is None


def test_config_can_load_an_empty_config():
    with tempfile.NamedTemporaryFile(suffix="cucurc") as temp_cucurc:
        CONFIG.load(temp_cucurc.name)


def test_config_validate_defined_variables():
    for variable in CONFIG.defined_variables:
        print(variable)


def test_config_resolves_nested_variables():
    CONFIG["FIZZ"] = "{BUZZ}"
    CONFIG["BUZZ"] = "boom"
    assert CONFIG.resolve("{FIZZ}") == "boom"


def test_config_resolves_wont_get_stuck_in_infinite_loop():
    CONFIG["FIZZ"] = "{BUZZ}"
    CONFIG["BUZZ"] = "{FIZZ}"

    with pytest.raises(
        RuntimeError, match="infinite replacement loop detected"
    ):
        assert CONFIG.resolve("{FIZZ}") == "boom"


def test_config_custom_variable_resolution():
    cucu.register_custom_variable_handling("FOO_.*", lambda x: "foo")
    CONFIG["FOO_BAR"] = "wassup"
    # if the custom resolution takes precedence then we'll never see the
    # "wassup" value
    assert CONFIG.resolve("{FOO_BAR}") == "foo"


def test_config_expand_variables_handles_existent_and_non_existent_variables():
    CONFIG["var1"] = "value1"

    result = CONFIG.expand("{var1} and {var2}")
    expected = {
        "var1": "value1",
        "var2": None,
    }
    check.equal(
        result,
        expected,
        "Expand should handle both existing and non-existing variables",
    )


def test_config_expand_variables_handles_recursive_variable_resolution():
    CONFIG["var1"] = "{var2}"
    CONFIG["var2"] = "value2"

    result = CONFIG.expand("{var1}")
    expected = {
        "var1": "value2",
    }
    check.equal(
        result, expected, "Expand should resolve recursive variable references"
    )


def test_config_expand_with_custom_variable_handling():
    cucu.register_custom_variable_handling("CUSTOM_.*", lambda x: "boom")
    CONFIG["CUSTOM_BAR"] = "wassup"
    # if the custom resolution takes precedence then we'll never see the
    # "wassup" value
    assert CONFIG.resolve("{CUSTOM_BAR}") == "boom"


def test_leaf_map():
    data = {
        "a": 1,
        "b": ["x", "k", "c", "d", {"one": "bee", "two": "straws"}],
    }

    def something(value, parent, key):
        if key in ["a", 3, "two"]:
            return "z"

        return value

    expected = {
        "a": "z",
        "b": ["x", "k", "c", "d", {"one": "bee", "two": "z"}],
    }
    actual = leaf_map(data, something)
    assert actual == expected


def test_config_push_pop_stack_behavior():
    config = Config()
    config["key1"] = "value1"
    config["key2"] = "value2"

    # Take first snapshot
    config.snapshot("first")
    config["key2"] = "modified"
    config["key3"] = "value3"

    # Take second snapshot
    config.snapshot("second")
    config["key1"] = "again_modified"

    # Test stack depth
    assert len(config.snapshots) == 2

    # Pop should restore to second snapshot
    config.restore(with_pop=True)
    assert config["key1"] == "value1"
    assert config["key2"] == "modified"
    assert config["key3"] == "value3"
    assert len(config.snapshots) == 1

    # Pop again should restore to first snapshot
    config.restore(with_pop=True)
    assert config["key1"] == "value1"
    assert config["key2"] == "value2"
    assert "key3" not in config
    assert len(config.snapshots) == 0


def test_config_restore_functionality():
    # Test that restore restores to top of stack without popping
    CONFIG["TEST"] = "initial"
    CONFIG.snapshot()

    CONFIG["TEST"] = "modified"
    assert CONFIG["TEST"] == "modified"

    CONFIG.restore()
    assert CONFIG["TEST"] == "initial"

    # Verify the stack still has the value (not popped)
    CONFIG["TEST"] = "modified_again"
    CONFIG.restore()
    assert CONFIG["TEST"] == "initial"


def test_config_empty_stack_operations_graceful():
    # Clear any existing stack
    CONFIG.snapshots = []

    # Restore on empty stack should not raise error
    CONFIG.restore()

    # Pop on empty stack should not raise error
    CONFIG.restore(with_pop=True)


def test_config_named_snapshots():
    config = Config()
    config["key1"] = "value1"

    # Take named snapshot
    config.snapshot("first_snapshot")
    config["key2"] = "value2"

    # Take another named snapshot
    config.snapshot("second_snapshot")
    config["key3"] = "value3"

    # Check snapshot names
    names = config.list_snapshots()
    assert names == ["first_snapshot", "second_snapshot"]

    # Pop should restore to second snapshot
    config.restore(with_pop=True)
    assert "key3" not in config
    assert config["key2"] == "value2"

    # Check snapshot names after pop
    names = config.list_snapshots()
    assert names == ["first_snapshot"]


def test_config_auto_generated_snapshot_names():
    config = Config()
    config["key1"] = "value1"

    # Take unnamed snapshots
    config.snapshot()  # should be snapshot_0
    config.snapshot()  # should be snapshot_1

    names = config.list_snapshots()
    assert names == ["snapshot_0", "snapshot_1"]


def test_config_empty_snapshots_list():
    config = Config()

    # Empty snapshots should return empty list
    names = config.list_snapshots()
    assert names == []

    # restore and pop should handle empty snapshots gracefully
    config.restore()  # should not raise
    config.restore(with_pop=True)  # should not raise

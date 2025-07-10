import tempfile

import pytest

import cucu
from cucu.config import CONFIG, leaf_map


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
    assert CONFIG.true("VAR1")
    assert CONFIG.true("INEXISTENT") is False


def test_config_false_method():
    CONFIG["VAR1"] = "false"
    assert CONFIG.false("VAR1")
    CONFIG["VAR1"] = "true"
    assert CONFIG.false("VAR1") is False
    assert CONFIG.false("INEXISTENT")


def test_config_resolves_variables():
    CONFIG["VAR1"] = "foo"
    CONFIG["VAR2"] = "bar"
    assert CONFIG.resolve("{VAR1} and {VAR2}") == "foo and bar"


def test_config_resolve_leaves_unresolved_variables():
    assert CONFIG.resolve("{NOT_SET}") == ""


def test_config_push_and_pop_works():
    CONFIG["FOO"] = None
    CONFIG.push()
    CONFIG["FOO"] = "bar"
    assert CONFIG["FOO"] == "bar"
    CONFIG.pop()
    assert CONFIG["FOO"] is None


def test_config_nested_push_and_pop():
    CONFIG["VAR1"] = "original1"
    CONFIG["VAR2"] = "original2"

    # First level
    CONFIG.push()
    CONFIG["VAR1"] = "level1_1"
    CONFIG["VAR2"] = "level1_2"
    assert CONFIG["VAR1"] == "level1_1"
    assert CONFIG["VAR2"] == "level1_2"

    # Second level
    CONFIG.push()
    CONFIG["VAR1"] = "level2_1"
    CONFIG["VAR3"] = "level2_3"
    assert CONFIG["VAR1"] == "level2_1"
    assert CONFIG["VAR2"] == "level1_2"  # Should maintain from previous level
    assert CONFIG["VAR3"] == "level2_3"

    # Pop back to first level
    CONFIG.pop()
    assert CONFIG["VAR1"] == "level1_1"
    assert CONFIG["VAR2"] == "level1_2"
    assert CONFIG["VAR3"] is None  # Should be cleared

    # Pop back to original
    CONFIG.pop()
    assert CONFIG["VAR1"] == "original1"
    assert CONFIG["VAR2"] == "original2"


def test_config_pop_empty_stack_raises_error():
    # Clear any existing stack
    while CONFIG.snapshot_stack:
        CONFIG.snapshot_stack.pop()

    with pytest.raises(
        RuntimeError, match="No config snapshots available to pop"
    ):
        CONFIG.pop()


def test_config_multiple_push_pop_operations():
    CONFIG["TEST"] = "initial"

    # Test multiple push/pop cycles
    for i in range(3):
        CONFIG.push()
        CONFIG["TEST"] = f"level_{i}"
        assert CONFIG["TEST"] == f"level_{i}"

    # Pop them all back
    for i in range(2, -1, -1):
        CONFIG.pop()
        if i > 0:
            assert CONFIG["TEST"] == f"level_{i - 1}"
        else:
            assert CONFIG["TEST"] == "initial"


def test_config_push_preserves_all_variables():
    # Set multiple variables
    CONFIG["A"] = "value_a"
    CONFIG["B"] = "value_b"
    CONFIG["C"] = "value_c"

    CONFIG.push()

    # Modify some, add new ones
    CONFIG["A"] = "new_a"
    CONFIG["D"] = "new_d"
    del CONFIG["B"]  # Remove one

    assert CONFIG["A"] == "new_a"
    assert CONFIG["B"] is None
    assert CONFIG["C"] == "value_c"
    assert CONFIG["D"] == "new_d"

    # Pop should restore everything
    CONFIG.pop()
    assert CONFIG["A"] == "value_a"
    assert CONFIG["B"] == "value_b"
    assert CONFIG["C"] == "value_c"
    assert CONFIG["D"] is None


def test_config_can_load_an_empty_config():
    with tempfile.NamedTemporaryFile(suffix="cucurc") as temp_cucurc:
        CONFIG.load(temp_cucurc.name)


def test_confi_validate_defined_variables():
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

    assert CONFIG.expand("{var1} and {var2}") == {
        "var1": "value1",
        "var2": None,
    }


def test_config_expand_variables_handles_recursive_variable_resolution():
    CONFIG["var1"] = "{var2}"
    CONFIG["var2"] = "value2"

    assert CONFIG.expand("{var1}") == {
        "var1": "value2",
    }


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

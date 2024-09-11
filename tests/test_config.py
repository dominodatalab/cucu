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


def test_config_snapshot_and_restore_works():
    CONFIG["FOO"] = None
    CONFIG.snapshot()
    CONFIG["FOO"] = "bar"
    assert CONFIG["FOO"] == "bar"
    CONFIG.restore()
    assert CONFIG["FOO"] is None


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

import cucu
from cucu.config import CONFIG


def test_hide_secrets_handles_string_with_no_secrets():
    assert CONFIG.hide_secrets("foobar") == "foobar"


def test_hide_secrets_handles_string_with_secret():
    CONFIG["CUCU_SECRETS"] = "foobar"
    CONFIG["foobar"] = "supersecret"
    result = CONFIG.hide_secrets("supersecret should not be seen")
    assert result == "*********** should not be seen"


def test_hide_secrets_handles_multiple_secrets():
    CONFIG["CUCU_SECRETS"] = "foobar,fizzbuzz"
    CONFIG["foobar"] = "supersecret"
    result = CONFIG.hide_secrets("supersecret should not be seen")
    assert result == "*********** should not be seen"


def test_hide_secrets_handles_secrets_with_custom_variables():
    cucu.register_custom_variable_handling("CUSTOM_.*", lambda x: "boom")
    CONFIG["CUCU_SECRETS"] = "foobar,CUSTOM_foobar"
    CONFIG["foobar"] = "supersecret"
    result = CONFIG.hide_secrets("supersecret should not be boom")
    assert result == "*********** should not be ****"

import cucu
import pytest

from cucu import behave_tweaks
from cucu.config import CONFIG


def test_hide_secrets_handles_string_with_no_secrets():
    assert behave_tweaks.hide_secrets("foobar") == "foobar"


def test_hide_secrets_handles_string_with_secret():
    CONFIG["CUCU_SECRETS"] = "foobar"
    CONFIG["foobar"] = "supersecret"
    assert (
        behave_tweaks.hide_secrets("supersecret should not be seen")
        is "*********** should not be seen"
    )


def test_hide_secrets_handles_multiple_secrets():
    CONFIG["CUCU_SECRETS"] = "foobar,fizzbuzz"
    CONFIG["foobar"] = "supersecret"
    assert (
        behave_tweaks.hide_secrets("supersecret should not be seen")
        is "*********** should not be seen"
    )


def test_hide_secrets_handles_secrets_with_custom_variables():
    cucu.register_custom_variable_handling("CUSTOM_.*", lambda x: "boom")
    CONFIG["CUCU_SECRETS"] = "foobar,CUSTOM_foobar"
    CONFIG["foobar"] = "supersecret"
    assert (
        behave_tweaks.hide_secrets("supersecret should not be boom")
        is "*********** should not be ****"
    )

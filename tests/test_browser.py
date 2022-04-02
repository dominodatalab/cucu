import pytest

from cucu.browser.core import Browser


def test_any_subclass_of_browser_gets_appropriate_error_from_unimplemented_class_method():
    browser = Browser()
    methods = [method for method in dir(browser) if not method.startswith("__")]

    for method_name in methods:
        with pytest.raises(RuntimeError, match="implement me"):
            method = browser.__getattribute__(method_name)
            print(method.__code__.co_argcount)
            args = [
                "fake argument"
                for _ in range(0, method.__code__.co_argcount - 1)
            ]
            # XXX: eventually need to pass keyword arguments
            method(*args)

from unittest.mock import patch

import pytest

from cucu import config
from cucu.browser.core import Browser
from cucu.browser.selenium import Selenium


def test_any_subclass_of_browser_gets_appropriate_error_from_unimplemented_class_method():
    ignore_methods = ["wait_for_page_to_load"]
    browser = Browser()
    methods = [
        method for method in dir(browser) if not method.startswith("__")
    ]

    for method_name in methods:
        if method_name in ignore_methods:
            continue

        with pytest.raises(RuntimeError, match="implement me"):
            method = browser.__getattribute__(method_name)
            print(method.__code__.co_argcount)
            args = [
                "fake argument"
                for _ in range(0, method.__code__.co_argcount - 1)
            ]
            # XXX: eventually need to pass keyword arguments
            method(*args)


@patch("cucu.browser.selenium.webdriver.Remote")
def test_edge_ignore_ssl_uses_w3c_capability_on_remote(remote):
    config.CONFIG.snapshot()
    try:
        config.CONFIG["CUCU_IGNORE_SSL_CERTIFICATE_ERRORS"] = "true"
        Selenium().open("edge", selenium_remote_url="http://localhost:4444")
    finally:
        config.CONFIG.restore()

    capabilities = remote.call_args.kwargs["options"].to_capabilities()
    assert capabilities["acceptInsecureCerts"] is True
    assert "acceptSslCerts" not in capabilities

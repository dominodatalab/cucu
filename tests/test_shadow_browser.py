import os
import urllib.parse

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from cucu.browser.shadow import (
    deep_query_selector_all,
    deep_query_selector_first,
)


def _remote_driver():
    if os.environ.get("CIRCLECI") != "true":
        pytest.skip("needs Selenium Grid (CircleCI browser matrix)")
    job = os.environ.get("CIRCLE_JOB", "").lower()
    if "chrome" in job:
        options = ChromeOptions()
    elif "firefox" in job:
        options = FirefoxOptions()
    elif "edge" in job:
        options = EdgeOptions()
    else:
        pytest.skip(f"unexpected CIRCLE_JOB {os.environ.get('CIRCLE_JOB')!r}")
    return webdriver.Remote(
        command_executor="http://localhost:4444", options=options
    )


@pytest.fixture
def remote_driver():
    driver = _remote_driver()
    try:
        yield driver
    finally:
        driver.quit()


def test_deep_query_selector_first_finds_open_shadow_host(remote_driver):
    html = """<!DOCTYPE html><html><body><div id="h"></div>
<script>
const h = document.getElementById("h");
h.attachShadow({mode: "open"}).innerHTML =
  '<span id="inner" data-cucu-shadow="1">x</span>';
</script></body></html>"""
    remote_driver.get(
        "data:text/html;charset=utf-8," + urllib.parse.quote(html, safe="")
    )
    el = deep_query_selector_first(remote_driver, "[data-cucu-shadow='1']")
    assert el is not None
    assert el.get_attribute("id") == "inner"


def test_deep_query_selector_all_collects_shadow_matches(remote_driver):
    html = """<!DOCTYPE html><html><body>
<div id="a"></div><div id="b"></div>
<script>
function host(id) {
  const el = document.getElementById(id);
  el.attachShadow({mode: "open"}).innerHTML =
    '<i class="hit">1</i>';
}
host("a");
host("b");
</script></body></html>"""
    remote_driver.get(
        "data:text/html;charset=utf-8," + urllib.parse.quote(html, safe="")
    )
    els = deep_query_selector_all(remote_driver, "i.hit")
    assert len(els) == 2

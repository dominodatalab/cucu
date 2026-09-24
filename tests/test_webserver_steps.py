import urllib.request

import pytest

from cucu import hooks
from cucu.config import CONFIG
from cucu.steps import webserver_steps


@pytest.fixture(autouse=True)
def clean_webserver_state():
    hooks.init_global_hook_variables()
    yield
    webserver_steps._shutdown_webservers(None)


def test_webserver_is_reused_for_same_directory(tmp_path):
    (tmp_path / "hello.txt").write_text("hi")
    webserver_steps.start_or_reuse_webserver(str(tmp_path), "PORT_A")
    webserver_steps.start_or_reuse_webserver(str(tmp_path), "PORT_B")

    assert CONFIG["PORT_A"] == CONFIG["PORT_B"]
    assert len(webserver_steps._webservers) == 1
    # only one run-end shutdown hook registered, not one per call
    shutdown_hooks = [
        h
        for h in CONFIG["__CUCU_AFTER_ALL_HOOKS"]
        if h is webserver_steps._shutdown_webservers
    ]
    assert len(shutdown_hooks) == 1

    body = urllib.request.urlopen(
        f"http://127.0.0.1:{CONFIG['PORT_A']}/hello.txt", timeout=5
    ).read()
    assert body == b"hi"


def test_webserver_distinct_directories_get_distinct_servers(tmp_path):
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()
    webserver_steps.start_or_reuse_webserver(str(dir_a), "PORT_A")
    webserver_steps.start_or_reuse_webserver(str(dir_b), "PORT_B")

    assert CONFIG["PORT_A"] != CONFIG["PORT_B"]
    assert len(webserver_steps._webservers) == 2


def test_shutdown_webservers_stops_servers_and_empties_cache(tmp_path):
    webserver_steps.start_or_reuse_webserver(str(tmp_path), "PORT")
    port = CONFIG["PORT"]

    webserver_steps._shutdown_webservers(None)

    assert webserver_steps._webservers == {}
    with pytest.raises(Exception):
        urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2)

import time
from unittest.mock import MagicMock

from selenium.common.exceptions import WebDriverException

from cucu.utils import SeleniumKeepAlive


def test_keep_alive_stop_returns_immediately_despite_long_interval():
    ka = SeleniumKeepAlive(MagicMock(), interval=30)
    ka.start()
    assert ka.active

    start = time.perf_counter()
    ka.stop()
    elapsed = time.perf_counter() - start

    assert not ka.active
    assert not ka.thread.is_alive()
    # the whole point of the Event: no waiting out the 30s interval or the
    # 5s join timeout
    assert elapsed < 1.0


def test_keep_alive_pings_browser_periodically():
    browser = MagicMock()
    ka = SeleniumKeepAlive(browser, interval=0.01)
    ka.start()
    time.sleep(0.2)
    ka.stop()
    assert browser.execute.call_count >= 2


def test_keep_alive_thread_exits_when_session_closed():
    browser = MagicMock()
    browser.execute.side_effect = WebDriverException("session deleted")
    ka = SeleniumKeepAlive(browser, interval=30)
    ka.start()

    ka.thread.join(timeout=2)
    assert not ka.thread.is_alive()
    assert not ka.active


def test_keep_alive_without_browser_never_starts():
    ka = SeleniumKeepAlive(None, interval=1)
    ka.start()
    assert not ka.active
    assert ka.thread is None
    ka.stop()  # must be a safe no-op


def test_keep_alive_restartable_after_stop():
    browser = MagicMock()
    ka = SeleniumKeepAlive(browser, interval=30)
    ka.start()
    ka.stop()
    ka.start()
    assert ka.active
    ka.stop()
    assert not ka.active

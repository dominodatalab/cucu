import logging

import chromedriver_autoinstaller
import geckodriver_autoinstaller
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.remote_connection import RemoteConnection

from cucu import config, edgedriver_autoinstaller, logger
from cucu.browser.core import Browser
from cucu.browser.frames import search_in_all_frames


class DisableLogger:
    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


def init():
    """
    initialize any selenium specific needs
    """
    if config.CONFIG["CUCU_BROWSER"] == "chrome":
        try:
            with DisableLogger():
                # auto install chromedriver if not present
                chromedriver_autoinstaller.install()
        except:  # noqa: E722
            logging.debug("unable to auto install chromedriver")

    if config.CONFIG["CUCU_BROWSER"] == "firefox":
        # https://github.com/mozilla/geckodriver/issues/330
        logger.warn("browser console logs not available on firefox")
        geckodriver_autoinstaller.install()

    if config.CONFIG["CUCU_BROWSER"] == "edge":
        edgedriver_autoinstaller.install()


class Selenium(Browser):
    def __init__(self):
        self.driver = None

    def open(
        self, browser, headless=False, selenium_remote_url=None, detach=False
    ):
        if selenium_remote_url is None:
            init()

        timeout = float(config.CONFIG["CUCU_SELENIUM_DEFAULT_TIMEOUT_S"])
        RemoteConnection.set_timeout(timeout)

        height = config.CONFIG["CUCU_BROWSER_WINDOW_HEIGHT"]
        width = config.CONFIG["CUCU_BROWSER_WINDOW_WIDTH"]
        cucu_downloads_dir = config.CONFIG["CUCU_BROWSER_DOWNLOADS_DIR"]
        ignore_ssl_certificate_errors = config.CONFIG[
            "CUCU_IGNORE_SSL_CERTIFICATE_ERRORS"
        ]

        if browser.startswith("chrome"):
            options = Options()
            options.add_experimental_option("detach", detach)

            prefs = {"download.default_directory": cucu_downloads_dir}
            options.add_experimental_option("prefs", prefs)

            options.add_argument(f"--window-size={width},{height}")
            options.add_argument("--disable-dev-shm-usage")

            if headless:
                options.add_argument("--headless")

            if ignore_ssl_certificate_errors:
                options.add_argument("ignore-certificate-errors")

            desired_capabilities = DesiredCapabilities.CHROME
            desired_capabilities["goog:loggingPrefs"] = {"browser": "ALL"}

            if selenium_remote_url is not None:
                logger.debug(f"webdriver.Remote init: {selenium_remote_url}")
                try:
                    self.driver = webdriver.Remote(
                        options=options,
                        command_executor=selenium_remote_url,
                        desired_capabilities=desired_capabilities,
                    )
                except urllib3.exceptions.ReadTimeoutError:
                    print("*" * 80)
                    print(
                        "* unable to connect to the remote selenium setup,"
                        " you may need to restart it"
                    )
                    print("*" * 80)
                    print("")
                    raise
            else:
                logger.debug("webdriver.Chrome init")
                self.driver = webdriver.Chrome(
                    chrome_options=options,
                    desired_capabilities=desired_capabilities,
                )

        elif browser.startswith("firefox"):
            options = webdriver.FirefoxOptions()
            profile = webdriver.FirefoxProfile()
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference(
                "browser.download.manager.showWhenStarting", False
            )
            profile.set_preference("browser.download.dir", cucu_downloads_dir)
            profile.set_preference(
                "browser.helperApps.neverAsk.saveToDisk",
                "images/jpeg, application/pdf, application/octet-stream, text/plain",
            )

            if ignore_ssl_certificate_errors:
                profile.accept_untrusted_certs = True

            options.add_argument(f"--width={width}")
            options.add_argument(f"--height={height}")

            desired_capabilities = DesiredCapabilities.FIREFOX
            desired_capabilities["loggingPrefs"] = {"browser": "ALL"}

            if headless:
                options.add_argument("--headless")

            if selenium_remote_url is not None:
                logger.debug(f"webdriver.Remote init: {selenium_remote_url}")
                try:
                    self.driver = webdriver.Remote(
                        command_executor=selenium_remote_url,
                        desired_capabilities=desired_capabilities,
                        browser_profile=profile,
                    )
                except urllib3.exceptions.ReadTimeoutError:
                    print("*" * 80)
                    print(
                        "* unable to connect to the remote selenium setup,"
                        " you may need to restart it"
                    )
                    print("*" * 80)
                    print("")
                    raise
            else:
                logger.debug("webdriver.Firefox init")
                self.driver = webdriver.Firefox(
                    firefox_profile=profile,
                    options=options,
                    desired_capabilities=desired_capabilities,
                )

        elif browser.startswith("edge"):
            options = webdriver.EdgeOptions()

            options.add_experimental_option(
                "prefs", {"download.default_directory": cucu_downloads_dir}
            )

            if headless:
                options.use_chromium = True
                options.add_argument("--headless")

            desired_capabilities = DesiredCapabilities.EDGE

            if ignore_ssl_certificate_errors:
                desired_capabilities["acceptSslCerts"] = True

            if selenium_remote_url is not None:
                logger.debug(f"webdriver.Remote init: {selenium_remote_url}")
                try:
                    self.driver = webdriver.Remote(
                        command_executor=selenium_remote_url,
                        desired_capabilities=desired_capabilities,
                        options=options,
                    )
                except urllib3.exceptions.ReadTimeoutError:
                    print("*" * 80)
                    print(
                        "* unable to connect to the remote selenium setup,"
                        " you may need to restart it"
                    )
                    print("*" * 80)
                    print("")
                    raise
            else:
                logger.debug("webdriver.Firefox init")
                edgedriver_filepath = (
                    edgedriver_autoinstaller.utils.download_edgedriver()
                )
                self.driver = webdriver.Edge(
                    executable_path=edgedriver_filepath,
                    options=options,
                    capabilities=desired_capabilities,
                )

        else:
            raise Exception(f"unknown browser {browser}")

        self.driver.set_window_size(width, height)
        self.wait_for_page_to_load()

    def get_log(self):
        if config.CONFIG["CUCU_BROWSER"] == "firefox":
            return []

        return self.driver.get_log("browser")

    def get_current_url(self):
        return self.driver.current_url

    def navigate(self, url):
        self.driver.get(url)
        self.wait_for_page_to_load()

    def switch_to_next_tab(self):
        window_handles = self.driver.window_handles
        window_handle = self.driver.current_window_handle
        window_handle_index = window_handles.index(window_handle)

        if window_handle_index == len(window_handles) - 1:
            raise RuntimeError("no next browser tab available")

        self.driver.switch_to.window(window_handles[window_handle_index + 1])

    def switch_to_previous_tab(self):
        window_handles = self.driver.window_handles
        window_handle = self.driver.current_window_handle
        window_handle_index = window_handles.index(window_handle)

        if window_handle_index == 0:
            raise RuntimeError("no previous browser tab available")

        self.driver.switch_to.window(window_handles[window_handle_index - 1])

    def back(self):
        self.driver.back()
        self.wait_for_page_to_load()

    def refresh(self):
        self.driver.refresh()
        self.wait_for_page_to_load()

    def title(self):
        return self.driver.title

    def css_find_elements(self, selector):
        def find_elements_in_frame():
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

            def visible(element):
                return element.is_displayed()

            return list(filter(visible, elements))

        return search_in_all_frames(self, find_elements_in_frame)

    def execute(self, javascript, *args):
        return self.driver.execute_script(javascript, *args)

    def click(self, element):
        element.click()
        # let cucu's own wait for page to load checks run
        self.wait_for_page_to_load()

    def switch_to_default_frame(self):
        self.driver.switch_to.default_content()
        logger.debug("switched browser to the default frame")

    def switch_to_frame(self, frame):
        self.driver.switch_to.frame(frame)
        logger.debug(f"switched browser to an iframe: {frame}")

    def screenshot(self, filepath):
        self.driver.get_screenshot_as_file(filepath)

    def close_window(self):
        window_handles = self.driver.window_handles
        window_handle = self.driver.current_window_handle
        window_handle_index = window_handles.index(window_handle)

        self.driver.close()
        self.driver.switch_to.window(window_handles[window_handle_index - 1])

    def quit(self):
        self.driver.quit()

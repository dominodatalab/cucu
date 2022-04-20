import chromedriver_autoinstaller
import logging
import os
import uuid

from cucu.browser.core import Browser
from cucu import config, logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options


class DisableLogger:
    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


def init():
    """
    initialize any selenium specific needs
    """
    utils = chromedriver_autoinstaller.utils
    chromedriver_autoinstaller_path = utils.get_chromedriver_path()
    chromedriver_filename = utils.get_chromedriver_filename()
    chrome_version = utils.get_chrome_version()
    chrome_major_version = utils.get_major_version(chrome_version)
    chromedriver_path = os.path.join(
        chromedriver_autoinstaller_path,
        chrome_major_version,
        chromedriver_filename,
    )

    # auto install chromedriver if not present
    if not os.path.exists(chromedriver_path):
        with DisableLogger():
            chromedriver_autoinstaller.install()


class Selenium(Browser):
    def __init__(self):
        self.driver = None

    def open(
        self, browser, headless=False, selenium_remote_url=None, detach=False
    ):

        if browser.startswith("chrome"):
            options = Options()
            options.add_experimental_option("detach", detach)

            cucu_downloads_path = config.CONFIG["CUCU_BROWSER_DOWNLOADS_DIR"]
            scenario_downloads_path = os.path.join(
                cucu_downloads_path, uuid.uuid1().hex
            )
            config.CONFIG["SCENARIO_DOWNLOADS_DIR"] = scenario_downloads_path
            logger.debug(f"scenario downloads path: {scenario_downloads_path}")

            prefs = {"download.default_directory": scenario_downloads_path}
            options.add_experimental_option("prefs", prefs)

            height = config.CONFIG["CUCU_BROWSER_WINDOW_HEIGHT"]
            width = config.CONFIG["CUCU_BROWSER_WINDOW_WIDTH"]
            options.add_argument(f"--window-size={width},{height}")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--ignore-certificate-errors")

            if headless:
                options.add_argument("--headless")

            desired_capabilities = DesiredCapabilities.CHROME
            desired_capabilities["goog:loggingPrefs"] = {"browser": "ALL"}

            if selenium_remote_url is not None:
                logger.debug(f"connecting to selenium: {selenium_remote_url}")
                self.driver = webdriver.Remote(
                    command_executor=selenium_remote_url,
                    desired_capabilities=desired_capabilities,
                )
            else:
                self.driver = webdriver.Chrome(
                    chrome_options=options,
                    desired_capabilities=desired_capabilities,
                )
        else:
            raise Exception(f"unknown browser {browser}")

        # we want the window to always maximize at start and use up the
        # available desktop space
        self.driver.maximize_window()

    def get_log(self):
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
        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

        def visible(element):
            return element.is_displayed()

        return list(filter(visible, elements))

    def execute(self, javascript):
        return self.driver.execute_script(javascript)

    def click(self, element):
        element.click()
        # let cucu's own wait for page to load checks run
        self.wait_for_page_to_load()

    def switch_to_default_frame(self):
        self.driver.switch_to.default_content()

    def switch_to_frame(self, frame):
        self.driver.switch_to.frame(frame)

    def screenshot(self, filepath):
        self.driver.get_screenshot_as_file(filepath)

    def close_window(self):
        window_handles = self.driver.window_handles
        window_handle = self.driver.current_window_handle
        window_handle_index = window_handles.index(window_handle)

        if window_handle_index == 0:
            raise RuntimeError("previous tab not available")

        self.driver.close()
        self.driver.switch_to.window(window_handles[window_handle_index - 1])

    def quit(self):
        self.driver.quit()

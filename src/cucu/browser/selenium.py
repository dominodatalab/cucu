import chromedriver_autoinstaller

from cucu.browser.core import Browser
from cucu import config, logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options


class Selenium(Browser):

    def __init__(self):
        self.driver = None

    def open(self,
             browser,
             headless=False,
             selenium_remote_url=None,
             detach=False):

        if browser.startswith('chrome'):
            options = Options()
            options.add_experimental_option('detach', detach)

            height = config.CONFIG['CUCU_BROWSER_WINDOW_HEIGHT']
            width = config.CONFIG['CUCU_BROWSER_WINDOW_WIDTH']
            options.add_argument(f'--window-size={width},{height}')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--ignore-certificate-errors')

            if headless:
                options.add_argument('--headless')

            if selenium_remote_url is not None:
                logger.debug(f'connecting to selenium: {selenium_remote_url}')
                self.driver = webdriver.Remote(
                    command_executor=selenium_remote_url,
                    desired_capabilities=DesiredCapabilities.CHROME,
                )
            else:
                # auto install chromedriver if not present
                chromedriver_autoinstaller.install()
                self.driver = webdriver.Chrome(chrome_options=options)
        else:
            raise Exception(f'unknown browser {browser}')

    def navigate(self, url):
        self.driver.get(url)

    def refresh(self):
        self.driver.refresh()

    def title(self):
        return self.driver.title

    def xpath_find_elements(self, xpath):
        return self.driver.find_elements(By.XPATH, xpath)

    def css_find_elements(self, selector):
        return self.driver.find_elements(By.CSS_SELECTOR, selector)

    def execute(self, javascript):
        return self.driver.execute_script(javascript)

    def screenshot(self, filepath):
        self.driver.get_screenshot_as_file(filepath)

    def quit(self):
        self.driver.quit()

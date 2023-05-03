from selenium.webdriver.remote import webelement

from cucu.browser.frames import search_in_all_frames
from cucu.config import CONFIG

# monkey patch some methods at the WebElement level
__ORIGINAL_FIND_ELEMENTS = webelement.WebElement.find_elements


def init():
    """
    initialize various selenium tweaks to change the behavior of the underlying
    selenium classes.
    """

    # intercept the find_elements calls and use the nifty frames method to allow
    # the expression to be executed against every visible frame to find the
    # desired element.
    def find_elements(self, by="id", value=None):
        ctx = CONFIG["__CUCU_CTX"]

        def find_elements_in_frame():
            return __ORIGINAL_FIND_ELEMENTS(self, by, value)

        return search_in_all_frames(ctx.browser, find_elements_in_frame)

    webelement.WebElement.find_elements = find_elements

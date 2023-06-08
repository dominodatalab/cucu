#
# cucu's browser implementatoin is an abstraction to allow us to easily
# run the same tests against a browser being managed by selenium, cypress or
# any other future browser testing framework
#
import time

from cucu import logger
from cucu.config import CONFIG


class Browser:
    def __init__(self):
        pass

    def open(self, *args, **kwargs):
        raise RuntimeError("implement me")

    def navigate(self, url):
        raise RuntimeError("implement me")

    def switch_to_next_tab(self):
        raise RuntimeError("implement me")

    def switch_to_previous_tab(self):
        raise RuntimeError("implement me")

    def back(self):
        raise RuntimeError("implement me")

    def refresh(self):
        raise RuntimeError("implement me")

    def get_current_url(self):
        raise RuntimeError("implement me")

    def title(self):
        raise RuntimeError("implement me")

    def execute(self, javascript, *args, **kwargs):
        raise RuntimeError("implement me")

    def click(self, element):
        raise RuntimeError("implement me")

    def switch_to_default_frame(self):
        raise RuntimeError("implement me")

    def switch_to_frame(self, frame):
        raise RuntimeError("implement me")

    def screenshot(self, filepath):
        raise RuntimeError("implement me")

    def close_window(self):
        raise RuntimeError("implement me")

    def quit(self):
        raise RuntimeError("implement me")

    # built in methods to be used by all browser implementations
    def wait_for_page_to_load(self):
        """
        this method is to be used by all browser implementations and called
        when after clicking something or refreshing the page and we'd like to
        make sure the is "loaded" and ready to be interacted with.

        this also gives us a place to fire off any additional page checks such
        as a console log checker, broken image checker, etc.
        """

        # run the page checks
        if CONFIG["__CUCU_PAGE_CHECK_HOOKS"]:
            for name, hook in CONFIG["__CUCU_PAGE_CHECK_HOOKS"].items():
                logger.debug(f'executing page check "{name}"')
                start = time.time()
                hook(self)
                logger.debug(
                    f'executed page check "{name}" in {round(time.time()-start, 3)}s'
                )

#
# cucu's browser implementatoin is an abstraction to allow us to easily
# run the same tests against a browser being managed by selenium, cypress or
# any other future browser testing framework
#

# WIP: thinking about how to abstract the browser in a way that would allow any
#      cucu matcher implementation to just work with any browser framework


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

    def execute(self, javascript):
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

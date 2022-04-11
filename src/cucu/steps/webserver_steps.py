from behave import step
from cucu import register_after_this_scenario_hook
from cucu.config import CONFIG
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread


class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


@step(
    'I start a webserver at directory "{directory}" and save the port to the variable "{variable}"'
)
def run_webserver_for_scenario(context, directory, variable):
    handler = partial(QuietHTTPRequestHandler, directory=directory)
    httpd = HTTPServer(("", 0), handler)
    thread = Thread(target=httpd.serve_forever)
    thread.start()

    _, port = httpd.server_address
    CONFIG[variable] = str(port)

    def shutdown_webserver(_):
        httpd.shutdown()
        thread.join()

    register_after_this_scenario_hook(shutdown_webserver)

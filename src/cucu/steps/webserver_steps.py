from behave import step
from cucu import register_after_scenario_hook
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread


class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


@step('I start a webserver on port "{port}" at directory "{directory}"')
def run_webserver_for_scenario(context, port, directory):
    handler = partial(QuietHTTPRequestHandler, directory=directory)
    httpd = HTTPServer(("", int(port)), handler)
    thread = Thread(target=httpd.serve_forever)
    thread.start()

    def shutdown_webserver(_):
        httpd.shutdown()
        thread.join()

    register_after_scenario_hook(shutdown_webserver)

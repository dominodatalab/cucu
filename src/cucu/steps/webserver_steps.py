from behave import step
from cucu import register_after_this_scenario_hook
from cucu.config import CONFIG
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread


class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


def start_webserver(directory, port=0):
    handler = partial(QuietHTTPRequestHandler, directory=directory)
    httpd = HTTPServer(("", int(port)), handler)

    thread = Thread(target=httpd.serve_forever)
    thread.start()
    _, port = httpd.server_address

    def shutdown_webserver(_):
        httpd.shutdown()
        thread.join()

    register_after_this_scenario_hook(shutdown_webserver)
    return port


@step(
    'I start a webserver at directory "{directory}" and save the port to the variable "{variable}"'
)
def run_webserver(ctx, directory, variable):
    """
    start a webserver with the root at the directory provided and save the
    port that the server is listening at to the variable name provided

    examples:
        Given I start webserver at directory "/some/path" and save the port to the variable "PORT"
          And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/somefile.html"
    """
    port = start_webserver(directory)
    CONFIG[variable] = str(port)


@step('I start a webserver at directory "{directory}" on port "{port}"')
def run_webserver_on_port(ctx, directory, port):
    """
    start a webserver with the root at the directory provided and on the port
    provided

    examples:
        Given I start webserver at directory "/some/path" on port "8888"
          And I open a browser at the url "http://{HOST_ADDRESS}:8888/somefile.html"
    """
    start_webserver(directory, port=port)

import socket
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread

from behave import step

from cucu import logger, register_after_all_hook
from cucu.config import CONFIG


class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


# resolved directory -> running HTTPServer, reused across scenarios; each
# worker process has its own cache. Shut down once at the end of the run.
_webservers = {}
_shutdown_hook_registered = False


def _shutdown_webservers(_):
    global _shutdown_hook_registered
    while _webservers:
        _, httpd = _webservers.popitem()
        httpd.shutdown()
        httpd.server_close()
    _shutdown_hook_registered = False


def start_or_reuse_webserver(directory, variable):
    """
    start a webserver serving the directory provided (reusing a running one
    for the same directory) and save its port to the variable name provided
    """
    global _shutdown_hook_registered
    key = str(Path(directory).resolve())
    httpd = _webservers.get(key)

    if httpd is None:
        handler = partial(QuietHTTPRequestHandler, directory=directory)
        httpd = HTTPServer(("", 0), handler)
        # daemon thread so a leaked server can never block process exit; the
        # after-all hook shuts it down cleanly in the normal case
        thread = Thread(target=httpd.serve_forever, daemon=True)
        thread.start()

        _, port = httpd.server_address
        with socket.create_connection(("localhost", port), timeout=5):
            logger.debug(f"Webserver is running at {port=}")

        _webservers[key] = httpd
        if not _shutdown_hook_registered:
            register_after_all_hook(_shutdown_webservers)
            _shutdown_hook_registered = True

    CONFIG[variable] = str(httpd.server_address[1])


@step(
    'I start a webserver at directory "{directory}" and save the port to the variable "{variable}"'
)
def run_webserver_for_scenario(ctx, directory, variable):
    """
    start a webserver with the root at the directory provided and save the
    port that the server is listening at to the variable name provided

    the server is started once per directory and reused for the rest of the
    run (starting and tearing down a server per scenario is measurably
    expensive); all servers are shut down in an after-all hook

    examples:
        Given I start a webserver at directory "/some/path" and save the port to the variable "PORT"
          And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/somefile.html"
    """
    start_or_reuse_webserver(directory, variable)

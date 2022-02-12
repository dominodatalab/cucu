from behave import step
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread


class HttpTask:

    def __init__(self, server, thread):
        self.server = server
        self.thread = thread

    def quit(self):
        self.server.shutdown()
        self.thread.join()


@step('I start a webserver on port "{port}" at directory "{directory}"')
def run_webserver_for_scenario(context, port, directory):
    handler = partial(SimpleHTTPRequestHandler, directory=directory)
    httpd = HTTPServer(('', int(port)), handler)
    thread = Thread(target=httpd.serve_forever)
    thread.start()
    context.scenario_tasks.append(HttpTask(httpd, thread))

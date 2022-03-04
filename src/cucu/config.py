import os
import socket
import yaml


class Config(dict):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        try:
            value = os.environ.get(key)

            if value is None:
                value = dict.__getitem__(self, key)

            return value
        except KeyError:
            return None

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs):
            self[k] = v

    def bool(self, key):
        return self[key] in [True, 'True', 'true', 'yes', 'enabled']

    def true(self, key):
        return self.bool(key)

    def false(self, key):
        return not self.true(key)

    def load(self, filepath):
        """
        loads configuration values from a YAML file at the filepath provided
        """
        config = yaml.safe_load(open(filepath, 'rb'))

        for key in config.keys():
            self[key] = config[key]

    def resolve(self, value):
        """
        resolve any variable references {...} in the string provided using
        the values currently stored in the config object.
        """
        if isinstance(value, str):
            return value.format_map(self)
        else:
            return value


# global config object
CONFIG = Config()


def get_local_address():
    google_dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    google_dns_socket.connect(('8.8.8.8', 80))
    return google_dns_socket.getsockname()[0]


# XXX: need a way to register these with description so that we can create a
#      `cucu vars` command which spits out the available variables, their
#      defaults and a description of their usage.
CONFIG['HOST_ADDRESS'] = get_local_address()
CONFIG['CUCU_STEP_WAIT_TIMEOUT_MS'] = 20000  # default of 20s to wait
CONFIG['CUCU_STEP_RETRY_AFTER_MS'] = 500     # default of 500ms to wait between retries
CONFIG['CUCU_KEEP_BROWSER_ALIVE'] = False

CONFIG['CUCU_BROWSER_WINDOW_HEIGHT'] = 1080
CONFIG['CUCU_BROWSER_WINDOW_WIDTH'] = 1920

# cucu internals
CONFIG['__CUCU_AFTER_SCENARIO_HOOKS'] = []

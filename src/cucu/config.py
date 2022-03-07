import os
import socket
import yaml

from cucu import logger


class Config(dict):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        try:
            # environment always takes precedence
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

    def load_cucurc_files(self, filepath):
        """
        load in order the ~/.cucurc.yml and then subsequent config files
        starting from the current working directory to the filepath provided
        """

        # load the ~/.cucurc.yml first
        home_cucurc_filepath = os.path.join(os.path.expanduser('~'), '.cucurc.yml')
        if os.path.exists(home_cucurc_filepath):
            logger.debug('loading configuration values from ~/.cucurc.yml')
            self.load(home_cucurc_filepath)

        filepath = os.path.abspath(filepath)
        if os.path.isfile(filepath):
            basename = os.path.dirname(filepath)
        else:
            basename = filepath

        # create the inverse list of the directories starting from cwd to the one
        # containing the feature file we want to run to load the cucrc.yml files in
        # the correct order
        dirnames = [os.getcwd()]
        while basename != os.getcwd():
            dirnames.append(basename)
            basename = os.path.dirname(basename)

        for dirname in dirnames:
            cucurc_filepath = os.path.join(dirname, 'cucurc.yml')
            if os.path.exists(cucurc_filepath):
                logger.debug(f'loading for {cucurc_filepath}')
                self.load(cucurc_filepath)

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

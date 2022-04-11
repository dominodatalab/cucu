import os
import socket
import yaml


class Config(dict):
    def __init__(self, **kwargs):
        self.update(**kwargs)
        self.resolving = False

    def __getitem__(self, key):
        try:
            # environment always takes precedence
            value = os.environ.get(key)

            if value is None:
                value = dict.__getitem__(self, key)

            if self.resolving and value is None:
                return ""

            return value
        except KeyError:
            if self.resolving:
                return ""
            else:
                return None

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v

    def bool(self, key):
        return self[key] in [True, "True", "true", "yes", "enabled"]

    def true(self, key):
        return self.bool(key)

    def false(self, key):
        return not self.true(key)

    def load(self, filepath):
        """
        loads configuration values from a YAML file at the filepath provided
        """
        config = yaml.safe_load(open(filepath, "rb"))

        for key in config.keys():
            self[key] = config[key]

    def load_cucurc_files(self, filepath):
        """
        load in order the ~/.cucurc.yml and then subsequent config files
        starting from the current working directory to the filepath provided
        """

        # load the ~/.cucurc.yml first
        home_cucurc_filepath = os.path.join(
            os.path.expanduser("~"), ".cucurc.yml"
        )
        if os.path.exists(home_cucurc_filepath):
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
            cucurc_filepath = os.path.join(dirname, "cucurc.yml")
            if os.path.exists(cucurc_filepath):
                self.load(cucurc_filepath)

    def resolve(self, value):
        """
        resolve any variable references {...} in the string provided using
        the values currently stored in the config object.
        """
        if isinstance(value, str):
            self.resolving = True
            try:
                return value.format_map(self)
            finally:
                self.resolving = False
        else:
            return value

    def snapshot(self):
        """
        make a shallow copy of the current config values which can later be
        restored using the `restore` method.
        """
        self.snapshot_data = self.copy()

    def restore(self):
        """
        restore a previous `snapshot`
        """
        self.clear()
        self.update(**self.snapshot_data)


# global config object
CONFIG = Config()


def get_local_address():
    google_dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    google_dns_socket.connect(("8.8.8.8", 80))
    return google_dns_socket.getsockname()[0]


# XXX: need a way to register these with description so that we can create a
#      `cucu vars` command which spits out the available variables, their
#      defaults and a description of their usage.
CONFIG["HOST_ADDRESS"] = get_local_address()
CONFIG["CWD"] = os.getcwd()

# coma separated list of variables that we should hide if their values are to
# be printed to the console
CONFIG["CUCU_SECRETS"] = ""

CONFIG["CUCU_STEP_WAIT_TIMEOUT_S"] = 20.0  # default of 20s to wait
CONFIG[
    "CUCU_STEP_RETRY_AFTER_S"
] = 0.5  # default of 500ms to wait between retries
CONFIG["CUCU_KEEP_BROWSER_ALIVE"] = False

CONFIG["CUCU_BROWSER_WINDOW_HEIGHT"] = 1080
CONFIG["CUCU_BROWSER_WINDOW_WIDTH"] = 1920

# cucu internals
CONFIG["__CUCU_AFTER_SCENARIO_HOOKS"] = []

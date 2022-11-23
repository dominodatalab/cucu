import os
import re
import socket
import yaml


class Config(dict):

    # only match variables {...}
    __VARIABLE_REGEX = re.compile(r"\{(?<!\\{)([^{}]+)\}(?<!\\})")

    def __init__(self, **kwargs):
        self.update(**kwargs)
        self.resolving = False
        self.defined_variables = {}
        self.variable_lookups = {}

    def define(self, name, description, default=None):
        """
        used to define variables and set their default so that we can then
        provide the info using the `cucu vars` command for test writers to know
        where and how to use various built-in variables.

        parameters:
            name(string): the name of the variable
            description(string): a succint description of variables purpose
            default(string): an optional default to set the variable to
        """
        self.defined_variables[name] = {
            "description": description,
            "default": default,
        }
        # set the default
        self.__setitem__(name, default)

    def escape(self, string):
        """
        utility method used to escape strings that would be otherwise problematic
        if the values were passed around as is in cucu steps.
        """
        if type(string) == str:
            string = string.replace("{", "\\{")
            string = string.replace("}", "\\}")

        return string

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
            for regex, lookup in self.variable_lookups.items():
                if regex.match(key):
                    return lookup(key)

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

        if config:
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

    def expand(self, string):
        """
        find any variable references and return an dictionary of all of the
        variable names and values within the string provided.

        returns:
            a dictionary of all of the variable names found in the string
            provided with the exact value of the variable at runtime.
        """
        references = {}

        variables = re.findall("{([^{}]+)}", string)

        for variable in variables:
            value = self.resolve(f"{{{variable}}}")

            # if it didn't resolve to anything then
            if value:
                value = str(value).replace("\n", "\\n")
                value = value[:80] + "..." * (len(value) > 80)
            else:
                value = None

            references[variable] = value

        return references

    def resolve(self, string):
        """
        resolve any variable references {...} in the string provided using
        the values currently stored in the config object. We also unescape any
        characters preceding by a backslash as to allow for test writers to
        escape special characters
        """
        if isinstance(string, str):
            previouses = [None]
            while previouses[-1] != string:
                # if any of the previous iterations of replacing variables looks
                # like the exact string we have now then break out of the loop
                # as there's an infinite recursion of variable replacing values
                if string in previouses:
                    raise RuntimeError("infinite replacement loop detected")

                previouses.append(string)

                for var_name in Config.__VARIABLE_REGEX.findall(string):
                    value = self.get(var_name)

                    if value is None:
                        value = ""
                        print(f'WARNING variable "{var_name}" is undefined')

                    string = string.replace("{" + var_name + "}", str(value))

            # we are only going to allow escaping of { and " characters for the
            # time being as they're part of the language:
            #
            #   * " are used around step arguments
            #   * {} are used by variable references
            #
            # regex below uses negative lookbehind to assert we're not replacing
            # any escapes that have the backslash itself escaped.
            #
            string = re.sub(r"(?<!\\)\\{", "{", string)
            string = re.sub(r"(?<!\\)\\}", "}", string)
            string = re.sub(r'(?<!\\)\\"', '"', string)

        return string

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

    def register_custom_variable_handling(self, regex, lookup):
        """
        register a regex to match variable names on and allow the lookup
        function provided to do the handling of the resolution of the variable
        name.

        parameters:
            regex(string): regular expression to match on any config variable
                           name when doing lookups
            lookup(func): a function that accepts a variable name to return its
                          value at runtime.

                          def lookup(name):
                            return [value of the variable at runtime]
        """
        self.variable_lookups[re.compile(regex)] = lookup


# global config object
CONFIG = Config()


def get_local_address():
    """
    internal method to get the current host address
    """
    google_dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    google_dns_socket.connect(("8.8.8.8", 80))
    return google_dns_socket.getsockname()[0]


CONFIG.define(
    "HOST_ADDRESS",
    "host address of the current machine cucu is running on",
    default=get_local_address(),
)
CONFIG.define(
    "CWD",
    "the current working directory of the cucu process",
    default=os.getcwd,
)
CONFIG.define(
    "CUCU_SECRETS",
    "a comma separated list of VARIABLE names that we want to hide "
    "their values in the various outputs of cucu by replacing with asterisks",
    default="",
)
CONFIG.define(
    "CUCU_STEP_WAIT_TIMEOUT_S",
    "the total amount of wait time in seconds `wait for` steps",
    default=20.0,
)
CONFIG.define(
    "CUCU_STEP_RETRY_AFTER_S",
    "the amount of time to wait between retries in `wait for` steps",
    default=0.5,
)
CONFIG.define(
    "CUCU_KEEP_BROWSER_ALIVE",
    "when set to true we'll reuse the browser between scenario runs",
    default=False,
)
CONFIG.define(
    "CUCU_BROWSER_WINDOW_HEIGHT",
    "the browser window height when running browser tests",
    default=768,
)
CONFIG.define(
    "CUCU_BROWSER_WINDOW_WIDTH",
    "the browser window width when running browser tests",
    default=1366,
)
CONFIG.define(
    "CUCU_BROWSER_DOWNLOADS_DIR",
    "the browser download directory when running browser tests",
    default="/tmp/cucu-browser-downloads",
)
CONFIG.define(
    "CUCU_SOCKET_DEFAULT_TIMEOUT_S",
    "the default timeout (seconds) for socket connect/read in cucu",
    default=60,
)
CONFIG.define(
    "CUCU_SELENIUM_DEFAULT_TIMEOUT_S",
    "the default timeout (seconds) for selenium connect/read in selenium",
    default=60,
)
CONFIG.define(
    "CUCU_MONITOR_PNG",
    "when set to a filename `cucu` will update the image to match "
    "the exact image step at runtime.",
    default=None,
)
CONFIG.define(
    "CUCU_LINT_RULES_PATH",
    "comma separated list of paths to load cucu lint rules from .yaml files",
    default="",
)

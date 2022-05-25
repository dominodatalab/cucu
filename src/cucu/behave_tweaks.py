#
# XXX: a lot of convoluted logic to handle capturing per step stdou/stderr
#      writing while not interfering with the way behave does its own log
#      capturing
#
import behave
import warnings
import sys

from behave.model import Table
from cucu.config import CONFIG
from functools import wraps


def init_step_hooks(stdout, stderr):
    #
    # wrap the given, when, then, step decorators from behave so we can intercept
    # the step arguments and do things such as replacing variable references that
    # are wrapped with curly braces {...}.
    #
    for decorator_name in ["given", "when", "then", "step"]:
        decorator = behave.__dict__[decorator_name]

        def inner_step_func(func, *args, variable_passthru=False, **kwargs):
            #
            # replace the variable references in the args and kwargs passed to the
            # step
            #
            # TODO: for tables and multiline strings there's a bit more
            #       work to be done here.
            #
            if not variable_passthru:
                args = [CONFIG.resolve(value) for value in args]
                kwargs = {
                    key: CONFIG.resolve(val) for (key, val) in kwargs.items()
                }

                # resolve variables in text and table data
                ctx = args[0]

                # we know what we're doing modifying this ctx value and so lets
                # avoid the unnecessary warning int he logs
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")

                    # resolve variables in the multiline string arguments
                    ctx.text = CONFIG.resolve(ctx.text)

                    # resolve variables in the table values
                    if ctx.table is not None:
                        ctx.table.original = Table(
                            ctx.table.headings, rows=ctx.table.rows
                        )
                        new_rows = []
                        for row in ctx.table.rows:
                            new_row = []

                            for value in row:
                                new_row.append(CONFIG.resolve(value))

                            new_rows.append(new_row)

                        ctx.table.rows = new_rows

            # intercept the current stdout and stderr that behave is capturing
            # and attach it to the captured output
            sys.stdout = CucuStream(sys.stdout, parent=stdout)
            sys.stderr = CucuStream(sys.stderr, parent=stderr)
            func(*args, **kwargs)

        def new_decorator(
            step_text, fix_inner_step=lambda x: x, variable_passthru=False
        ):
            """
            the new @step decorator

            parameters:
              step_text(string): the actual step string definition.
              fix_inner_step(function): a function used to fix the inner_step
                                        function code location and other
                                        properties.
              variable_passthru(bool): when set to true the variables are not
                                       replaced in the arguments of the step
                                       text and so variable references such as
                                       {FOO} are passed as such so they can
                                       be handled further down in `run_steps`
                                       for example.
            """

            #
            # IMPORTANT: if you add any additional line from the `wrapper`
            #            function name to the `inner_step` name then you HAVE to
            #            update the `src/cucu/helpers.py` fix_inner_step
            #            so it subtracts the lines between wrapper and
            #            inner_step functions (lines of code). More details
            #            at the `src/cucu/helpers.py` location.
            #
            def wrapper(func):
                @decorator(step_text)
                @wraps(func)
                def inner_step(*args, **kwargs):
                    inner_step_func(
                        func,
                        *args,
                        variable_passthru=variable_passthru,
                        **kwargs
                    )

                fix_inner_step(inner_step)

            return wrapper

        behave.__dict__[decorator_name] = new_decorator


def hide_secrets(line):
    secrets = CONFIG["CUCU_SECRETS"]

    # here's where we can hide secrets
    for secret in secrets.split(","):
        if secret is not None:
            value = CONFIG[secret]
            if value is not None:
                line = line.replace(value, "*" * len(value))

    return line


class CucuStream:
    def __init__(self, stream, parent=None):
        self.captured_data = []
        self.stream = stream
        self.parent = parent
        self.encoding = stream.encoding

    def __getattr__(self, item):
        return self.stream.__getattribute__(item)

    def fileno(self):
        return self.stream.fileno()

    def write(self, byte):
        byte = hide_secrets(byte)

        self.captured_data.append(byte)

        if type(byte) == bytes:
            self.stream.write(byte.decode("utf8"))
        else:
            self.stream.write(byte)

        if self.parent:
            self.parent.write(byte)

    def writelines(self, lines):
        lines = [hide_secrets(line) for line in lines]

        for line in lines:
            self.captured_data.append(line)

        if self.parent:
            self.parent.writelines(lines)

        self.stream.writelines(lines)

    def captured(self):
        captured_data = self.captured_data
        self.captured_data = []
        return captured_data

    def isatty(self):
        return self.stream.isatty()

    def flush(self):
        self.stream.flush()

#
# XXX: a lot of convoluted logic to handle capturing per step stdou/stderr
#      writing while not interfering with the way behave does its own log
#      capturing
#
import sys
import warnings
from functools import wraps

import behave
from behave.__main__ import main as original_behave_main
from behave.model import Table

from cucu.config import CONFIG


def behave_main(args):
    return original_behave_main(args)


def init_outputs(stdout, stderr):
    # capturing stdout and stderr output to record in reporting
    sys.stdout = CucuOutputStream(sys.stdout)
    sys.stderr = CucuOutputStream(sys.stderr)


def init_step_hooks(stdout, stderr):
    init_outputs(stdout, stderr)
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
                        **kwargs,
                    )

                fix_inner_step(inner_step)

            return wrapper

        behave.__dict__[decorator_name] = new_decorator


_stdout = sys.stdout


class CucuOutputStream:
    """
    encapsulates a lot of the logic to handle capturing step by step console
    logging but also redirecting logging at runtime to another stream


    FYI: in order to print to the screen you must use directly the sys.stdout object
         and write to it here as doing something like `print(...)` will result
         in an infinite recursive loop and break
    """

    def __init__(self, stream, other_stream=None):
        self.captured_data = []
        self.stream = stream
        self.encoding = stream.encoding
        self.other_stream = other_stream

    def set_other_stream(self, other):
        self.other_stream = other

    def __getattr__(self, item):
        return self.stream.__getattribute__(item)

    def isatty(self, *args, **kwargs):
        return self.stream.isatty(*args, **kwargs)

    def fileno(self):
        return self.stream.fileno()

    def flush(self):
        self.stream.flush()

        if self.other_stream:
            self.other_stream.flush()

    def write(self, byte):
        byte = CONFIG.hide_secrets(byte)

        self.captured_data.append(byte)

        if isinstance(byte, bytes):
            self.stream.write(byte.decode("utf8"))

            if self.other_stream:
                self.other_stream.write(byte.decode("utf8"))
        else:
            self.stream.write(byte)

            if self.other_stream:
                self.other_stream.write(byte)

    def writelines(self, lines):
        lines = [CONFIG.hide_secrets(line) for line in lines]

        for line in lines:
            self.captured_data.append(line)

        self.stream.writelines(lines)
        if self.other_stream:
            self.other_stream.writelines(lines)

    def captured(self):
        """
        returns the data captured thus far to the stream and resets the internal
        buffer to empty.
        """
        captured_data = self.captured_data
        self.captured_data = []
        return captured_data

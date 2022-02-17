#
# XXX: a lot of convoluted logic to handle capturing per step stdou/stderr
#      writing while not interfering with the way behave does its own log
#      capturing
#
import behave
import warnings
import sys

from cucu.config import CONFIG

from functools import wraps


def init_step_hooks(stdout, stderr):
    #
    # wrap the given, when, then, step decorators from behave so we can intercept
    # the step arguments and do things such as replacing variable references that
    # are wrapped with curly braces {...}.
    #
    for decorator_name in ['given', 'when', 'then', 'step']:
        decorator = behave.__dict__[decorator_name]

        def inner_step_func(func, *args, **kwargs):
            #
            # replace the variable references in the args and kwargs passed to the
            # step
            #
            # TODO: for tables and multiline strings there's a bit more
            #       work to be done here.
            #

            args = [CONFIG.resolve(value) for value in args]
            kwargs = {
                key: CONFIG.resolve(val) for (key, val) in kwargs.items()
            }

            # resolve variables in text and table data
            context = args[0]

            # we know what we're doing modifying this context value and so lets
            # avoid the unnecessary warning int he logs
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                context.text = CONFIG.resolve(context.text)

            init_output_streams(stdout, stderr)
            func(*args, **kwargs)

        def new_decorator(step_text, wait_for=False):
            def wrapper(func):
                @decorator(step_text)
                def inner_step(*args, **kwargs):
                    inner_step_func(func, *args, **kwargs)

                wraps(func, inner_step)
            return wrapper

        behave.__dict__[decorator_name] = new_decorator


def init_output_streams(parent_stdout, parent_stderr):
    # intercept all stdout/stderr writes for capturing of output but also so we
    # can tell the formatter when there was output produced within a step
    class CucuStream:

        def __init__(self, stream, parent_stream):
            self.captured_data = []
            self.stream = stream
            self.parent_stream = parent_stream

        def write(self, byte):
            self.captured_data.append(byte)
            self.stream.write(byte)
            self.parent_stream.write(byte)
            CONFIG['CUCU_WROTE_TO_CONSOLE'] = True

        def writelines(self, lines):
            for line in lines:
                self.captured_data.append(line)

            self.stream.writelines(lines)
            self.parent_stream.writelines(lines)
            CONFIG['CUCU_WROTE_TO_CONSOLE'] = True

        def captured(self):
            captured_data = self.captured_data
            self.captured_data = []
            return captured_data

        def isatty(self):
            return self.stream.isatty()

        def flush(self):
            self.stream.flush()

    sys.original_stdout = sys.stdout
    sys.original_stderr = sys.stderr

    sys.stdout = CucuStream(sys.stdout, parent_stdout)
    sys.stderr = CucuStream(sys.stderr, parent_stderr)


def uninit_output_streams():
    sys.stdout = sys.original_stdout
    sys.stderr = sys.original_stderr

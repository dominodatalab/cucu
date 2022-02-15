import behave
import functools
import os
import sys
import warnings
import uuid

from cucu import config, logger
from cucu.config import CONFIG
from functools import wraps
from retrying import retry

# load the ~/.cucurc.yml first
home_cucurc_filepath = os.path.join(os.path.expanduser('~'), '.cucurc.yml')
if os.path.exists(home_cucurc_filepath):
    logger.debug('loading configuration values from ~/.cucurc.yml')
    CONFIG.load(home_cucurc_filepath)

# override any global values with local values in cucurc.yml
local_cucurc_filepath = os.path.join(os.getcwd(), 'cucurc.yml')
if os.path.exists(local_cucurc_filepath):
    logger.debug('loading configuration values from cucurc.yml')
    CONFIG.load(local_cucurc_filepath)

#
# wrap the given, when, then, step decorators from behave so we can intercept
# the step arguments and do things such as replacing variable references that
# are wrapped with curly braces {...}.
#
for decorator_name in ['given', 'when', 'then', 'step']:
    decorator = behave.__dict__[decorator_name]

    ui_wait_timeout_ms = int(config.CONFIG['CUCU_WEB_WAIT_TIMEOUT_MS'])
    ui_wait_before_retry_ms = int(config.CONFIG['CUCU_WEB_WAIT_BEFORE_RETRY_MS'])

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

        func(*args, **kwargs)

    def new_decorator(step_text, wait_for=False):
        def wrapper(func):
            if wait_for:
                @decorator(step_text)
                @retry(stop_max_delay=ui_wait_timeout_ms,
                       wait_fixed=ui_wait_before_retry_ms)
                def inner_step(*args, **kwargs):
                    inner_step_func(func, *args, **kwargs)

                wraps(func, inner_step)
            else:
                @decorator(step_text)
                def inner_step(*args, **kwargs):
                    inner_step_func(func, *args, **kwargs)

                wraps(func, inner_step)
        return wrapper

    behave.__dict__[decorator_name] = new_decorator


def escape_filename(string):
    """
    escape string so it can be used as a filename safely.
    """
    return string.replace('/', '_')


def cucu_print(context, value):
    """
    cucu's own print method which allows you to cleanly print to the console
    log within your own step definitions.
    """
    context.stdout.write(f'{value}\n')
    config.CONFIG['CUCU_WROTE_TO_STDOUT'] = True


def before_all(context):
    pass
#    logging_level = config.CONFIG['CUCU_LOGGING_LEVEL'].upper()
#    logger.init_logging(logging_level)


def before_feature(context, feature):
    context.print = functools.partial(cucu_print, context)


def after_feature(context, feature):
    pass


def before_scenario(context, scenario):
    scenario_dir = os.path.join(config.CONFIG['CUCU_RESULTS_DIR'],
                                scenario.feature.name,
                                scenario.name)
    os.makedirs(scenario_dir)
    context.scenario = scenario
    context.scenario_dir = scenario_dir
    context.step_index = 1
    context.browsers = []
    context.browser = None
    context.stdout = sys.stdout
    context.scenario_tasks = []

    # TODO: move this into a pre-scenario hook which any module can use to
    #       register their own hooks and then you would just call of the
    #       specific hooks here
    config.CONFIG['SCENARIO_RUN_ID'] = uuid.uuid1().hex


def after_scenario(context, scenario):
    if CONFIG.true('CUCU_KEEP_BROWSER_ALIVE'):
        # TODO: need to create a logger for debug stuff like this
        pass

    else:
        # close the browser unless someone has set the keep browser alive
        # environment variable which allows tests to reuse the same browser
        # session
        for browser in context.browsers:
            browser.quit()

        context.browsers = []

    for task in context.scenario_tasks:
        task.quit()


def before_step(context, step):
    context.current_step = step


def after_step(context, step):
    if context.browser is not None:
        step_name = escape_filename(step.name)
        filepath = os.path.join(context.scenario_dir,
                                f'{context.step_index-1} - {step_name}.png')

        context.browser.screenshot(filepath)
        logger.debug(f'wrote screenshot {filepath}')

    context.step_index += 1

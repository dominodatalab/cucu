import os
import sys
import uuid

from cucu import behave_tweaks, config, logger
from cucu.config import CONFIG

behave_tweaks.init_step_hooks(sys.stdout, sys.stderr)


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


def escape_filename(string):
    """
    escape string so it can be used as a filename safely.
    """
    return string.replace('/', '_')


def before_all(context):
    pass


def before_feature(context, feature):
    pass


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
    step.stdout = []
    step.stderr = []
    context.current_step = step


def after_step(context, step):
    # grab the captured output during the step run and reset the wrappers
    step.stdout = sys.stdout.captured()
    step.stderr = sys.stderr.captured()
    behave_tweaks.uninit_output_streams()

    if context.browser is not None:
        step_name = escape_filename(step.name)
        filepath = os.path.join(context.scenario_dir,
                                f'{context.step_index-1} - {step_name}.png')

        context.browser.screenshot(filepath)
        logger.debug(f'wrote screenshot {filepath}')

    context.step_index += 1

    if CONFIG['CUCU_IPDB_ON_FAILURE'] == 'true' and step.status == 'failed':
        context._runner.stop_capture()
        import ipdb
        ipdb.post_mortem(step.exc_traceback)

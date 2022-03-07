import os
import sys
import uuid

from cucu import behave_tweaks, config, logger
from cucu.config import CONFIG

behave_tweaks.init_step_hooks(sys.stdout, sys.stderr)


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
    if config.CONFIG['CUCU_RESULTS_DIR'] is not None:
        scenario_dir = os.path.join(config.CONFIG['CUCU_RESULTS_DIR'],
                                    scenario.feature.name,
                                    scenario.name)
        os.makedirs(scenario_dir)
        context.scenario_dir = scenario_dir

    context.scenario = scenario
    context.step_index = 0
    context.browsers = []
    context.browser = None

    # internal cucu config variables
    config.CONFIG['SCENARIO_RUN_ID'] = uuid.uuid1().hex

    # internal cucu config objects
    CONFIG['__CUCU_AFTER_SCENARIO_HOOKS'] = []


def after_scenario(context, scenario):
    if CONFIG.true('CUCU_KEEP_BROWSER_ALIVE'):
        logger.debug('keeping browser alive between sessions')

    else:
        logger.debug('quitting browser between sessions')
        # close the browser unless someone has set the keep browser alive
        # environment variable which allows tests to reuse the same browser
        # session
        for browser in context.browsers:
            browser.quit()

        context.browsers = []

    for hook in CONFIG['__CUCU_AFTER_SCENARIO_HOOKS']:
        hook(context)

    CONFIG['__CUCU_AFTER_SCENARIO_HOOKS'] = []


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
                                f'{context.step_index} - {step_name}.png')

        context.browser.screenshot(filepath)
        logger.debug(f'wrote screenshot {filepath}')

    context.step_index += 1

    if CONFIG['CUCU_IPDB_ON_FAILURE'] == 'true' and step.status == 'failed':
        context._runner.stop_capture()
        import ipdb
        ipdb.post_mortem(step.exc_traceback)

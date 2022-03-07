import importlib
import os
import pkgutil
import sys

from cucu.config import CONFIG


def init_steps():
    """
    initialize cucu steps and load underlying
    """
    __all__ = []
    # trick to get the path of the script that called this function
    f_globals = sys._getframe(1).f_globals
    f_locals = sys._getframe(1).f_locals

    path = [os.path.dirname(f_globals['__file__'])]

    for loader, module_name, is_pkg in pkgutil.walk_packages(path):
        __all__.append(module_name)
        _module = loader.find_module(module_name).load_module(module_name)
        f_globals[module_name] = _module

    f_locals.update(importlib.import_module('cucu.steps').__dict__)


def init_environment():
    """
    initialize cucu internal environment hooks
    """
    f_locals = sys._getframe(1).f_locals
    f_locals.update(importlib.import_module('cucu.environment').__dict__)


def register_after_scenario_hook(after_scenario_func):
    """
    register an after scenario hook which is called with the current behave
    context object.
    """
    CONFIG['__CUCU_AFTER_SCENARIO_HOOKS'].append(after_scenario_func)


def run_steps(context, steps_text):
    """
    run sub steps within an existing step run by basically inserting those
    steps into the behave runtime.
    """
    context.feature.parser.variant = 'steps'
    steps = context.feature.parser.parse_steps(steps_text)

    # XXX: not pretty but we control both formatters so can make some
    #      assumptions
    for formatter in context._runner.formatters:
        step_index = formatter.steps.index(context.current_step)

        index = 1
        for step in steps:
            step.substep = True
            formatter.insert_step(step, index=step_index + index)
            index += 1

    try:
        step_index = context.scenario.background.steps.index(context.current_step)

        index = 1
        for step in steps:
            context.scenario.background.steps.insert(step_index + index, step)
            index += 1
    except Exception:
        step_index = context.scenario.steps.index(context.current_step)

        index = 1
        for step in steps:
            context.scenario.steps.insert(step_index + index, step)
            index += 1

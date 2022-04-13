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

    path = [os.path.dirname(f_globals["__file__"])]

    importlib.import_module("cucu.steps")

    for loader, module_name, is_pkg in pkgutil.walk_packages(path):
        __all__.append(module_name)
        _module = loader.find_module(module_name).load_module(module_name)
        f_globals[module_name] = _module


def init_environment():
    """
    initialize cucu internal environment hooks
    """
    f_locals = sys._getframe(1).f_locals
    f_locals.update(importlib.import_module("cucu.environment").__dict__)


def init_hook_variables():
    CONFIG["__CUCU_BEFORE_SCENARIO_HOOKS"] = []
    CONFIG["__CUCU_AFTER_SCENARIO_HOOKS"] = []
    CONFIG["__CUCU_BEFORE_THIS_SCENARIO_HOOKS"] = []
    CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"] = []

    CONFIG["__CUCU_BEFORE_STEP_HOOKS"] = []
    CONFIG["__CUCU_AFTER_STEP_HOOKS"] = []

    CONFIG["__CUCU_PAGE_CHECK_HOOKS"] = {}
    CONFIG["CUCU_BROKEN_IMAGES_PAGE_CHECK"] = "enabled"
    CONFIG["CUCU_READY_STATE_PAGE_CHECK"] = "enabled"


def register_before_all_scenario_hook(hook_func):
    """
    register a before scenario hook that will execute before eery scenario has
    executed and we will pass the current behave context object as the only
    argument to the hook_func provided.
    """
    CONFIG["__CUCU_BEFORE_SCENARIO_HOOKS"].append(hook_func)


def register_after_all_scenario_hook(hook_func):
    """
    register an after scenario hook that will execute after every scenario has
    executed and we will pass the current behave context object as the only
    argument to the hook_func provided.
    """
    CONFIG["__CUCU_AFTER_SCENARIO_HOOKS"].append(hook_func)


def register_before_this_scenario_hook(hook_func):
    """
    register a before scenario hook that will only once before the next scenario
    has executed and we will pass the current behave context object as the only
    argument to the hook_func provided.
    """
    CONFIG["__CUCU_BEFORE_THIS_SCENARIO_HOOKS"].append(hook_func)


def register_after_this_scenario_hook(hook_func):
    """
    register an after scenario hook that will only once after the next scenario
    has executed and we will pass the current behave context object as the only
    argument to the hook_func provided.
    """
    CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"].append(hook_func)


def register_page_check_hook(name, hook_func):
    """
    register a hook to run after every "page load", a "page load" event isn't
    accurate but we try to simply check the page after every interaction such as
    clicking or navigating.

    parameters:
        name(string):        name used when logging for the page check
        hook_func(function): function called with the current
                             `cucu.browser.Browser` instance
    """
    CONFIG["__CUCU_PAGE_CHECK_HOOKS"][name] = hook_func

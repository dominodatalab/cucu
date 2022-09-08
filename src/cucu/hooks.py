import re

from cucu.config import CONFIG

CONFIG.define(
    "CUCU_BROKEN_IMAGES_PAGE_CHECK",
    "enable/disable the broken image page checker",
    default="enabled",
)
CONFIG.define(
    "CUCU_READY_STATE_PAGE_CHECK",
    "enable/disable the ready state page checker",
    default="enabled",
)


def init_global_hook_variables():
    CONFIG["__CUCU_BEFORE_SCENARIO_HOOKS"] = []
    CONFIG["__CUCU_AFTER_SCENARIO_HOOKS"] = []

    CONFIG["__CUCU_BEFORE_STEP_HOOKS"] = []
    CONFIG["__CUCU_AFTER_STEP_HOOKS"] = []

    CONFIG["__CUCU_PAGE_CHECK_HOOKS"] = {}

    CONFIG["__CUCU_HTML_REPORT_TAG_HANDLERS"] = {}


def init_scenario_hook_variables():
    CONFIG["__CUCU_BEFORE_THIS_SCENARIO_HOOKS"] = []
    CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"] = []


def register_before_scenario_hook(hook_func):
    """
    register a before scenario hook that will execute before eery scenario has
    executed and we will pass the current behave context object as the only
    argument to the hook_func provided.
    """
    CONFIG["__CUCU_BEFORE_SCENARIO_HOOKS"].append(hook_func)


def register_after_scenario_hook(hook_func):
    """
    register an after scenario hook that will execute after every scenario has
    executed and we will pass the current behave context object as the only
    argument to the hook_func provided.
    """
    CONFIG["__CUCU_AFTER_SCENARIO_HOOKS"].append(hook_func)


def register_after_this_scenario_hook(hook_func):
    """
    register an after scenario hook that will only once after the next scenario
    has executed and we will pass the current behave context object as the only
    argument to the hook_func provided.
    """
    CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"].append(hook_func)


def register_before_step_hook(hook_func):
    """
    register a before step hook that will execute before every step is executed
    and we will pass the current behave context object as the only argument to
    the hook_func provided.
    """
    CONFIG["__CUCU_BEFORE_STEP_HOOKS"].append(hook_func)


def register_after_step_hook(hook_func):
    """
    register an after step hook that will execute after every step executes and
    we will pass the current behave context object as the only argument to the
    hook_func provided.
    """
    CONFIG["__CUCU_AFTER_STEP_HOOKS"].append(hook_func)


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


def register_custom_variable_handling(regex, lookup):
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
    CONFIG.register_custom_variable_handling(regex, lookup)


def register_custom_tags_in_report_handling(regex, handler):
    """
    register a regex to match tag names when generating the HTML test report
    and the function provided will process the exact tag found and return
    the HTML/text to place in the report when a tag that matches the provided
    regex is found.

    parameters:
        regex(string): regular expression to match on any tag name in the HTML
                       test report.
        handler(func): a function that accepts the complete tag name (ie @foo)
                       and returns the exact value to put in the HTMl test
                       report (HTML/text).

                      def handle(tag):
                        return "<a href="...">{tag}</a>"
    """
    CONFIG["__CUCU_HTML_REPORT_TAG_HANDLERS"][re.compile(regex)] = handler

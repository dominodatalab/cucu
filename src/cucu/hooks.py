import re
from collections import OrderedDict

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
    CONFIG["__CUCU_BEFORE_ALL_HOOKS"] = []
    CONFIG["__CUCU_AFTER_ALL_HOOKS"] = []

    CONFIG["__CUCU_BEFORE_SCENARIO_HOOKS"] = []
    CONFIG["__CUCU_AFTER_SCENARIO_HOOKS"] = []

    CONFIG["__CUCU_BEFORE_STEP_HOOKS"] = []
    CONFIG["__CUCU_AFTER_STEP_HOOKS"] = []

    CONFIG["__CUCU_PAGE_CHECK_HOOKS"] = OrderedDict()
    CONFIG["__CUCU_HTML_REPORT_TAG_HANDLERS"] = {}
    CONFIG["__CUCU_HTML_REPORT_SCENARIO_SUBHEADER_HANDLER"] = []

    CONFIG["__CUCU_CUSTOM_FAILURE_HANDLERS"] = []
    CONFIG["__CUCU_BEFORE_RETRY_HOOKS"] = []
    CONFIG["__CUCU_CTX"] = None


def init_scenario_hook_variables():
    CONFIG["__CUCU_BEFORE_THIS_SCENARIO_HOOKS"] = []
    CONFIG["__CUCU_AFTER_THIS_SCENARIO_HOOKS"] = []


def register_before_all_hook(hook_func):
    """
    register a before all hook that will execute once before anything is
    executed and we will pass the current behave context object as the only
    argument to the hook_func provided.
    """
    CONFIG["__CUCU_BEFORE_ALL_HOOKS"].append(hook_func)


def register_after_all_hook(hook_func):
    """
    register an after all hook that will execute once after everything is
    executed and we will pass the current behave context object as the only
    argument to the hook_func provided.
    """
    CONFIG["__CUCU_AFTER_ALL_HOOKS"].append(hook_func)


def register_before_scenario_hook(hook_func):
    """
    register a before scenario hook that will execute before every scenario has
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


def register_custom_scenario_subheader_in_report_handling(handler):
    """
    register a handler to add HTML content under the scenario header.

    parameters:
        handler(func): a function that accepts the scenario and returns a HTML to
                       go below the scenario header

                      def handle(scenario):
                        return f"<div>this is below the {scenario['name']}'s header</div>"
    """
    CONFIG["__CUCU_HTML_REPORT_SCENARIO_SUBHEADER_HANDLER"].append(handler)


def register_custom_junit_failure_handler(handler):
    """
    register a callback function to call when there is a test failure and
    we want to augment the failure output message in the junit results
    files.

    parameters:
        handler(feature, scenario):
          where feature and scenario are the following behave model
          objects:

            * https://behave.readthedocs.io/en/stable/api.html#behave.model.Feature
            * https://behave.readthedocs.io/en/stable/api.html#behave.model.Scenario

          You must return a string that will be appended to the top of the
          failure message in the JUnit XML results files.
    """
    CONFIG["__CUCU_CUSTOM_FAILURE_HANDLERS"].append(handler)


def register_before_retry_hook(hook_func):
    """
    register an before retry hook that will execute before retrying
    cucu.utils.retry function call. The arguments passed to the provided hook
    are only the current behave context object.

    parameters:
        handler(ctx): a method that accepts the current behave context and
                      executes whatever it needs to before a retryable call is
                      about to be retried.

                      def handle(ctx):
                        ctx.do_something()
    """
    CONFIG["__CUCU_BEFORE_RETRY_HOOKS"].append(hook_func)

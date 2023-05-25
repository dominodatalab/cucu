# -*- coding: utf-8 -*-
__version__ = "0.1.0"

import sys
from cucu import behave_tweaks
from cucu.browser import selenium_tweaks

# intercept the stdout/stderr so we can do things such as hiding secrets in logs
behave_tweaks.init_step_hooks(sys.stdout, sys.stderr)
selenium_tweaks.init()

from cucu.hooks import (
    init_global_hook_variables,
    init_scenario_hook_variables,
    register_after_all_hook,
    register_before_all_hook,
    register_after_this_scenario_hook,
    register_before_scenario_hook,
    register_after_scenario_hook,
    register_before_step_hook,
    register_after_step_hook,
    register_page_check_hook,
    register_custom_variable_handling,
    register_custom_tags_in_report_handling,
    register_custom_scenario_subheader_in_report_handling,
    register_custom_junit_failure_handler,
    register_before_retry_hook,
)

from cucu.utils import (
    format_gherkin_table,
    run_steps,
    retry,
    StopRetryException,
)

from cucu import helpers
from behave import step

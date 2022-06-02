# -*- coding: utf-8 -*-
__version__ = "0.1.0"

import sys
from cucu import behave_tweaks

# intercept the stdout/stderr so we can do things such as hiding secrets in logs
behave_tweaks.init_step_hooks(sys.stdout, sys.stderr)

from cucu.hooks import (
    init_global_hook_variables,
    init_scenario_hook_variables,
    register_after_this_scenario_hook,
    register_before_scenario_hook,
    register_after_scenario_hook,
    register_before_step_hook,
    register_after_step_hook,
    register_page_check_hook,
)

from cucu.utils import (
    run_steps,
    retry,
)

from cucu import helpers
from behave import step

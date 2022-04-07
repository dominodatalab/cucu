# -*- coding: utf-8 -*-
__version__ = "0.1.0"

import sys
from cucu import behave_tweaks

# intercept the stdout/stderr so we can do things such as hiding secrets in logs
behave_tweaks.init_step_hooks(sys.stdout, sys.stderr)

sys.stdout = behave_tweaks.CucuStream(sys.stdout)
sys.stderr = behave_tweaks.CucuStream(sys.stderr)

from cucu.hooks import (
    init_environment,
    init_steps,
    register_before_this_scenario_hook,
    register_after_this_scenario_hook,
    register_before_all_scenario_hook,
    register_after_all_scenario_hook,
)

from cucu.utils import (
    run_steps,
    retry,
)

from cucu import helpers
from behave import step

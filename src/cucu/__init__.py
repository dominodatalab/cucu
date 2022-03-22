# -*- coding: utf-8 -*-
__version__ = "0.1.0"

import sys
from cucu import behave_tweaks

# intercept the stdout/stderr so we can do things such as hiding secrets in logs
behave_tweaks.init_step_hooks(sys.stdout, sys.stderr)

sys.stdout = behave_tweaks.CucuStream(sys.stdout)
sys.stderr = behave_tweaks.CucuStream(sys.stderr)

# flake8: noqa
# we only expose the exact hooks we want to the outside world here.
from cucu.hooks import (
    init_environment,
    init_steps,
    register_after_scenario_hook,
    run_steps,
    retry,
)
from behave import step

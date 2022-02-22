from cucu.config import CONFIG


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

    index = 1
    for step in steps:
        step_index = context.scenario.steps.index(context.current_step)
        context.scenario.steps.insert(step_index + index, step)
        index += 1

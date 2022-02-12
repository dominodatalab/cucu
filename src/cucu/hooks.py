
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

    context.scenario.steps += steps

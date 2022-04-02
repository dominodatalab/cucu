import humanize
import inspect

from cucu import retry


class step(object):
    """
    Only to be used in this file as we're redefining the @step decorator in
    order to fix the code location of the @step() usage.

    Basically when you use any of the `define_xxx` steps below internally they
    call @step() and when that decorator executes in behave it will take the
    location of the function provided to the decorator and use that to both
    report as the location of the step's "source"
    (ie poetry run behave --no-summary --format steps.doc --dry-run). Now that
    would be confusing as the step is likely defined somewhere under
    `src/cucu/steps` but the location in the behave steps output would be wrong
    and then at runtime if there's an exception throw from one of the other
    functions inside the `define_xxx` method that trace would also not originate
    from the `src/cucu/steps` location where the `define_xxx` was called.

    So this redefinitino of @step will basically use a hook in the existing
    @step definition in `src/cucu/behave_tweaks.py` and provide a function
    to "fix" the inner_step function so its own code location now points back
    to the location where the `define_xxx` was called from.
    """

    def __init__(self, step_text):
        self.step_text = step_text
        frame = inspect.stack()[2].frame

        def fix_inner_step(func):
            #
            # Here is where we "fix" the code location for the function being
            # passed to the step() decorator. We are basically realigning the
            # filename and line location so it points to the original caller
            # of the `define_xxx` method. To do this alignment though we have
            # to subtract from the original file line number the number of code
            # lines in the `src/cucu/behave_tweaks.py` between the functions
            # wrapper and inner_step as that is the "actual code location" at
            # runtime and below we can only set the `firstlineno` which is the
            # "first line" of our __code__ point and by the time those N lines
            # execute the line number python would print would be N lines ahead
            # of the original location of the code we're trying to link to.
            #
            func.__code__ = func.__code__.replace(
                co_filename=frame.f_code.co_filename,
                co_firstlineno=frame.f_lineno - 3,
                co_name=frame.f_code.co_name,
            )

        self.fix_inner_step = fix_inner_step

    def __call__(self, func):
        from behave import step

        @step(self.step_text, fix_inner_step=self.fix_inner_step)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper


def nth_to_ordinal(index):
    return "" if index == 0 else f'"{humanize.ordinal(index + 1)}" '


def define_should_see_thing_with_name_steps(thing, find_func, with_nth=False):
    """
    defines steps with with the following signatures:

      I should see the {thing} "{name}"
      I should not see the {thing} "{name}"
      I wait to see the {thing} "{name}"
      I wait to not see the {thing} "{name}"
      I wait up to "{seconds}" seconds to see the {thing} "{name}"
      I wait up to "{seconds}" seconds to not see the {thing} "{name}"

      when with_nth=True we also define:

      I should see the "{nth}" {thing} "{name}"
      I should not see the "{nth}" {thing} "{name}"
      I wait to see the "{nth}" {thing} "{name}"
      I wait to not see the "{nth}" {thing} "{name}"
      I wait up to "{seconds}" seconds to see the "{nth}" {thing} "{name}"
      I wait up to "{seconds}" seconds to not see the "{nth}" {thing} "{name}"

    parameters:
        thing(string):       name of the thing we're creating the steps for such
                             as button, dialog, etc.
        find_func(function): function that returns the desired element:

                             def find_func(ctx, name, index=):
                                '''
                                ctx(object):  behave context object
                                name(string): name of the thing to find
                                index(int):   when there are multiple elements
                                              with the same name and you've
                                              specified with_nth=True
                                '''
        with_nth(bool):     when set to True we'll define the expanded set of
                            "nth" steps. default: False
    """

    def should_see(ctx, thing, name, index=0):
        prefix = nth_to_ordinal(index)
        element = find_func(ctx, name, index=index)

        if element is None:
            raise RuntimeError(f'unable to find the {prefix}{thing} "{name}"')

    def should_not_see(ctx, thing, name, index=0):
        prefix = nth_to_ordinal(index)
        element = find_func(ctx, name, index=index)

        if element is not None:
            raise RuntimeError(f'able to find the {prefix}{thing} "{name}"')

    @step(f'I should see the {thing} "{{name}}"')
    def should_see_the(ctx, name):
        should_see(ctx, thing, name)

    @step(f'I should not see the {thing} "{{name}}"')
    def should_not_see_the(ctx, name):
        should_not_see(ctx, thing, name)

    @step(f'I wait to see the {thing} "{{name}}"')
    def wait_to_see_the(ctx, name):
        retry(should_see)(ctx, thing, name)

    @step(f'I wait up to "{{seconds}}" seconds to see the {thing} "{{name}}"')
    def wait_up_to_seconds_to_see_the(ctx, seconds, name):
        milliseconds = float(seconds)
        retry(should_see, wait_up_to_s=milliseconds)(ctx, thing, name)

    if with_nth:

        @step(f'I should see the "{{nth:nth}}" {thing} "{{name}}"')
        def should_see_the_nth(ctx, nth, name):
            should_see(ctx, thing, name, index=nth)

        @step(f'I should not see the "{{nth:nth}}" {thing} "{{name}}"')
        def should_not_see_the_nth(ctx, nth, name):
            should_not_see(ctx, thing, name, index=nth)

        @step(f'I wait to see the "{{nth:nth}}" {thing} "{{name}}"')
        def wait_to_see_the_nth(ctx, nth, name):
            retry(should_see)(ctx, thing, name, index=nth)

        @step(
            f'I wait up to "{{seconds}}" seconds to see the "{{nth:nth}}" {thing} "{{name}}"'
        )
        def wait_up_to_seconds_to_see_the_nth(ctx, seconds, nth, name):
            seconds = float(seconds)
            retry(should_see, wait_up_to_s=seconds)(ctx, thing, name, index=nth)


def define_action_on_thing_with_name_steps(
    thing, action, find_func, action_func, with_nth=False
):
    """
    defines steps with with the following signatures:

      I {action} the {thing} "{name}"
      I wait to {action} the {thing} "{name}"
      I wait up to "{seconds}" seconds to {action} the {thing} "{name}"

      when with_nth=True we also define:

      I {action} the "{nth}" {thing} "{name}"
      I wait to {action} the "{nth}" {thing} "{name}"
      I wait up to "{seconds}" seconds to "{nth}" {action} the {thing} "{name}"

    parameters:
        thing(string):       name of the thing we're creating the steps for such
                             as button, dialog, etc.
        action(stirng):      the name of the action being performed, such as:
                             click, disable, etc.
        find_func(function): function that returns the desired element:

                             def find_func(ctx, name, index=):
                                '''
                                ctx(object):  behave context object
                                name(string): name of the thing to find
                                index(int):   when there are multiple elements
                                              with the same name and you've
                                              specified with_nth=True
                                '''
        action_func(function): function that performs the desired action:

                               def action_func(element):
                                  '''
                                  element(object): the element found
                                  '''
        with_nth(bool):     when set to True we'll define the expanded set of
                            "nth" steps. default: False
    """

    def action_it(ctx, thing, name, index=0):
        prefix = nth_to_ordinal(index)
        element = find_func(ctx, name, index=index)

        if element is None:
            raise RuntimeError(f'unable to find the {prefix}{thing} "{name}"')

        action_func(element)

    @step(f'I {action} the {thing} "{{name}}"')
    def action_the(ctx, name):
        action_it(ctx, thing, name)

    @step(f'I wait to {action} the {thing} "{{name}}"')
    def wait_to_action_the(ctx, name):
        retry(action_it)(ctx, thing, name)

    @step(
        f'I wait up to "{{seconds}}" seconds to {action} the {thing} "{{name}}"'
    )
    def wait_up_to_seconds_to_action_the(ctx, seconds, name):
        seconds = float(seconds)
        retry(action_it, wait_up_to_s=seconds)(ctx, thing, name)

    if with_nth:

        @step(f'I {action} the "{{nth:nth}}" {thing} "{{name}}"')
        def action_the_nth(ctx, nth, name):
            action_it(ctx, thing, name, index=nth)

        @step(f'I wait to {action} the "{{nth:nth}}" {thing} "{{name}}"')
        def action_the_nth(ctx, nth, name):
            retry(action_it)(ctx, thing, name, index=nth)

        @step(
            f'I wait up to "{{seconds}}" seconds to {action} the "{{nth:nth}}" {thing} "{{name}}"'
        )
        def action_the_nth(ctx, seconds, nth, name):
            seconds = float(seconds)
            retry(action_it, wait_up_to_s=seconds)(ctx, thing, name, index=nth)


def define_thing_with_name_in_state_steps(
    thing, state, find_func, is_in_state_func, with_nth=False
):
    """
    defines steps with with the following signatures:

      I should see the {thing} "{name}" is {state_name}
      I wait to see the {thing} "{name}" is {state_name}
      I wait up to "{seconds}" seconds to see the {thing} "{name}" is {state_name}

      when with_nth=True we also define:

      I should see the "{nth}" {thing} "{name}" is {state_name}
      I wait to see the "{nth}" {thing} "{name}" is {state_name}
      I wait up to "{seconds}" seconds to see the "{nth}" {thing} "{name}" is {state_name}

    parameters:
        thing(string):             name of the thing we're creating the steps for such
                                   as button, dialog, etc.
        state(stirng):             the name of the state being verified, such as:
                                   selected, checked, disabled, etc.
        find_func(function):       function that returns the desired element:

                                   def find_func(ctx, name, index=):
                                      '''
                                      ctx(object):  behave context object
                                      name(string): name of the thing to find
                                      index(int):   when there are multiple elements
                                                    with the same name and you've
                                                    specified with_nth=True
                                      '''
        is_int_state_func(function): function that verifies the element is in
                                     the desired state:

                                     def is_in_state_func(element):
                                        '''
                                        element(object): the element found
                                        returns(bool): returns True if in
                                                       expected state
                                        '''
        with_nth(bool):     when set to True we'll define the expanded set of
                            "nth" steps. default: False

    """

    def should_see_thing_in_state(ctx, thing, name, index=0):
        prefix = nth_to_ordinal(index)
        element = find_func(ctx, name, index=index)

        if element is None:
            raise RuntimeError(f'unable to find the {prefix}{thing} "{name}"')

        if not is_in_state_func(element):
            raise RuntimeError(f'{thing} "{name}" is not {state}')

    @step(f'I should see the {thing} "{{name}}" is {state}')
    def should_see_the_in_state(ctx, name):
        should_see_thing_in_state(ctx, thing, name)

    @step(f'I wait to see the {thing} "{{name}}" is {state}')
    def wait_to_see_the_in_state(ctx, name):
        retry(should_see_thing_in_state)(ctx, thing, name)

    @step(
        f'I wait up to "{{seconds}}" seconds to see the {thing} "{{name}}" is {state}'
    )
    def wait_up_to_seconds_to_see_the_in_state(ctx, seconds, name):
        seconds = float(seconds)
        retry(should_see_thing_in_state, wait_up_to_s=seconds)(ctx, thing, name)

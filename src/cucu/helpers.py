import sys

import humanize

from cucu import logger, retry, run_steps
from cucu.config import CONFIG


class step(object):
    """
    Only to be used in this file as we're redefining the @step decorator in
    order to fix the code location of the @step() usage.

    Basically when you use any of the `define_xxx` steps below internally they
    call @step() and when that decorator executes in behave it will take the
    location of the function provided to the decorator and use that to both
    report as the location of the step's "source"
    (ie uv run behave --no-summary --format steps.doc --dry-run). Now that
    would be confusing as the step is likely defined somewhere under
    `src/cucu/steps` but the location in the behave steps output would be wrong
    and then at runtime if there's an exception throw from one of the other
    functions inside the `define_xxx` method that trace would also not originate
    from the `src/cucu/steps` location where the `define_xxx` was called.

    So this redefinition of @step will basically use a hook in the existing
    @step definition in `src/cucu/behave_tweaks.py` and provide a function
    to "fix" the inner_step function so its own code location now points back
    to the location where the `define_xxx` was called from.
    """

    def __init__(self, step_text):
        self.step_text = step_text
        frame = sys._getframe(1).f_back

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

      I should immediately see the {thing} "{name}"
      I should see the {thing} "{name}"
      I wait to see the {thing} "{name}"
      I wait up to "{seconds}" seconds to see the {thing} "{name}"

      when with_nth=True we also define:
      I should immediately see the "{nth}" {thing} "{name}"
      I should see the "{nth}" {thing} "{name}"
      I wait to see the "{nth}" {thing} "{name}"
      I wait up to "{seconds}" seconds to see the "{nth}" {thing} "{name}"

      I should immediately not see the {thing} "{name}"
      I should not see the {thing} "{name}"
      I wait to not see the {thing} "{name}"
      I wait up to "{seconds}" seconds to not see the {thing} "{name}"

      when with_nth=True we also define:
      I should immediately not see the "{nth}" {thing} "{name}"
      I should not see the "{nth}" {thing} "{name}"
      I wait to not see the "{nth}" {thing} "{name}"
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

    # should see
    # undecorated def for reference below
    def base_should_see_the(ctx, thing, name, index=0):
        prefix = nth_to_ordinal(index)
        element = find_func(ctx, name, index=index)

        if element is None:
            raise RuntimeError(f'unable to find the {prefix}{thing} "{name}"')
        logger.debug(f'Success: saw {prefix}{thing} "{name}"')

    @step(f'I should immediately see the {thing} "{{name}}"')
    def should_immediately_see_the(ctx, thing, name):
        base_should_see_the(ctx, thing, name)

    @step(f'I should see the {thing} "{{name}}"')
    def should_see_the(ctx, name):
        retry(
            base_should_see_the,
            retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
            wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
        )(ctx, thing, name)

    @step(f'I wait to see the {thing} "{{name}}"')
    def wait_to_see_the(ctx, name):
        retry(base_should_see_the)(ctx, thing, name)

    @step(f'I wait up to "{{seconds}}" seconds to see the {thing} "{{name}}"')
    def wait_up_to_seconds_to_see_the(ctx, seconds, name):
        milliseconds = float(seconds)
        retry(base_should_see_the, wait_up_to_s=milliseconds)(ctx, thing, name)

    if with_nth:

        @step(f'I should immediately see the "{{nth:nth}}" {thing} "{{name}}"')
        def base_should_see_the_nth(ctx, nth, name):
            base_should_see_the(ctx, thing, name, index=nth)

        @step(f'I should see the "{{nth:nth}}" {thing} "{{name}}"')
        def should_see_the_nth(ctx, nth, name):
            retry(
                base_should_see_the,
                retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
                wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
            )(ctx, thing, name, index=nth)

        @step(f'I wait to see the "{{nth:nth}}" {thing} "{{name}}"')
        def wait_to_see_the_nth(ctx, nth, name):
            retry(base_should_see_the)(ctx, thing, name, index=nth)

        @step(
            f'I wait up to "{{seconds}}" seconds to see the "{{nth:nth}}" {thing} "{{name}}"'
        )
        def wait_up_to_seconds_to_see_the_nth(ctx, seconds, nth, name):
            seconds = float(seconds)
            retry(base_should_see_the, wait_up_to_s=seconds)(
                ctx, thing, name, index=nth
            )

    # should not see
    # undecorated def for reference below
    def base_should_not_see_the(ctx, thing, name, index=0):
        prefix = nth_to_ordinal(index)
        element = find_func(ctx, name, index=index)

        if element is not None:
            raise RuntimeError(f'able to find the {prefix}{thing} "{name}"')
        logger.debug(f'Success: did not see {prefix}{thing} "{name}"')

    @step(f'I should immediately not see the {thing} "{{name}}"')
    def should_immediately_not_see_the(ctx, thing, name):
        base_should_not_see_the(ctx, thing, name)

    @step(f'I should not see the {thing} "{{name}}"')
    def should_not_see_the(ctx, name):
        retry(
            base_should_not_see_the,
            retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
            wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
        )(ctx, thing, name)

    @step(f'I wait to not see the {thing} "{{name}}"')
    def wait_to_not_see_the(ctx, name):
        retry(base_should_not_see_the)(ctx, thing, name)

    @step(
        f'I wait up to "{{seconds}}" seconds to not see the {thing} "{{name}}"'
    )
    def wait_up_to_seconds_to_not_see_the(ctx, seconds, name):
        milliseconds = float(seconds)
        retry(base_should_not_see_the, wait_up_to_s=milliseconds)(
            ctx, thing, name
        )

    if with_nth:

        @step(
            f'I should immediately not see the "{{nth:nth}}" {thing} "{{name}}"'
        )
        def should_immediately_not_see_the_nth(ctx, nth, name):
            base_should_not_see_the(ctx, thing, name, index=nth)

        @step(f'I should not see the "{{nth:nth}}" {thing} "{{name}}"')
        def should_not_see_the_nth(ctx, nth, name):
            retry(
                base_should_not_see_the,
                retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
                wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
            )(ctx, thing, name, index=nth)

        @step(f'I wait to not see the "{{nth:nth}}" {thing} "{{name}}"')
        def wait_to_not_see_the_nth(ctx, nth, name):
            retry(base_should_not_see_the)(ctx, thing, name, index=nth)

        @step(
            f'I wait up to "{{seconds}}" seconds to not see the "{{nth:nth}}" {thing} "{{name}}"'
        )
        def wait_up_to_seconds_to_not_see_the_nth(ctx, seconds, nth, name):
            seconds = float(seconds)
            retry(base_should_not_see_the, wait_up_to_s=seconds)(
                ctx, thing, name, index=nth
            )


def define_action_on_thing_with_name_steps(
    thing, action, find_func, action_func, with_nth=False
):
    """
    defines steps with with the following signatures:

      I {action} the {thing} "{name}"
      I wait to {action} the {thing} "{name}"
      I wait up to "{seconds}" seconds to {action} the {thing} "{name}"
      ...
      I {action} the {thing} "{name}" if it exists

      when with_nth=True we also define:

      I {action} the "{nth}" {thing} "{name}"
      I wait to {action} the "{nth}" {thing} "{name}"
      I wait up to "{seconds}" seconds to "{nth}" {action} the {thing} "{name}"
      ...
      I {action} the "{nth}" {thing} "{name}" if it exists

    parameters:
        thing(string):       name of the thing we're creating the steps for such
                             as button, dialog, etc.
        action(string):      the name of the action being performed, such as:
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

                               def action_func(ctx, element):
                                  '''
                                  ctx(object):  behave context object
                                  element(object): the element found
                                  '''
        with_nth(bool):     when set to True we'll define the expanded set of
                            "nth" steps. default: False
    """

    # undecorated def for reference below
    def base_action_the(ctx, thing, name, index=0, must_exist=True):
        prefix = nth_to_ordinal(index)
        element = find_func(ctx, name, index=index)

        if element is None:
            if must_exist:
                raise RuntimeError(
                    f'unable to find the {prefix}{thing} "{name}"'
                )
        else:
            action_func(ctx, element)
            logger.debug(
                f'Successfully executed {action} {prefix}{thing} "{name}"'
            )

    @step(f'I immediately {action} the {thing} "{{name}}"')
    def immediately_action_the(ctx, name):
        base_action_the(ctx, thing, name)

    @step(f'I {action} the {thing} "{{name}}"')
    def action_the(ctx, name):
        retry(
            base_action_the,
            retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
            wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
        )(ctx, thing, name)

    @step(f'I immediately {action} the {thing} "{{name}}" if it exists')
    def immediately_action_the_if_it_exists(ctx, name):
        base_action_the(ctx, thing, name, must_exist=False)

    @step(f'I {action} the {thing} "{{name}}" if it exists')
    def action_the_if_it_exists(ctx, name):
        retry(
            base_action_the,
            retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
            wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
        )(ctx, thing, name, must_exist=False)

    @step(f'I wait to {action} the {thing} "{{name}}"')
    def wait_to_action_the(ctx, name):
        retry(base_action_the)(ctx, thing, name)

    @step(f'I wait to {action} the {thing} "{{name}}" if it exists')
    def wait_to_action_the_if_it_exists(ctx, name):
        retry(base_action_the)(ctx, thing, name, must_exist=False)

    @step(
        f'I wait up to "{{seconds}}" seconds to {action} the {thing} "{{name}}"'
    )
    def wait_up_to_seconds_to_action_the(ctx, seconds, name):
        seconds = float(seconds)
        retry(base_action_the, wait_up_to_s=seconds)(ctx, thing, name)

    if with_nth:

        @step(f'I immediately {action} the "{{nth:nth}}" {thing} "{{name}}"')
        def immediately_action_the_nth(ctx, nth, name):
            base_action_the(ctx, thing, name, index=nth)

        @step(f'I {action} the "{{nth:nth}}" {thing} "{{name}}"')
        def action_the_nth(ctx, nth, name):
            retry(
                base_action_the,
                retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
                wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
            )(ctx, thing, name, index=nth)

        @step(
            f'I immediately {action} the "{{nth:nth}}" {thing} "{{name}}" if it exists'
        )
        def immediately_action_the_nth_if_it_exists(ctx, nth, name):
            base_action_the(ctx, thing, name, index=nth, must_exist=False)

        @step(f'I {action} the "{{nth:nth}}" {thing} "{{name}}" if it exists')
        def action_the_nth_if_it_exists(ctx, nth, name):
            retry(
                base_action_the,
                retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
                wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
            )(ctx, thing, name, index=nth, must_exist=False)

        @step(f'I wait to {action} the "{{nth:nth}}" {thing} "{{name}}"')
        def wait_to_action_the_nth(ctx, nth, name):
            retry(base_action_the)(ctx, thing, name, index=nth)

        @step(
            f'I wait up to "{{seconds}}" seconds to {action} the "{{nth:nth}}" {thing} "{{name}}"'
        )
        def wait_up_to_action_the_nth(ctx, seconds, nth, name):
            seconds = float(seconds)
            retry(base_action_the, wait_up_to_s=seconds)(
                ctx, thing, name, index=nth
            )


def define_ensure_state_on_thing_with_name_steps(
    thing, state, find_func, state_func, action_func, with_nth=False
):
    """
    defines steps with with the following signatures:

      I ensure the {thing} "{name}" is {state}
      I wait to ensure the {thing} "{name}" is {state}
      I wait up to "{seconds}" seconds to ensure the {thing} "{name}" is {state}

      when with_nth=True we also define:

      I ensure the "{nth}" {thing} "{name}" is {state}
      I wait to ensure the "{nth}" {thing} "{name}" is {state}
      I wait up to "{seconds}" seconds to ensure the "{nth}" {thing} "{name}" is {state}

    parameters:
        thing(string):       name of the thing we're creating the steps for such
                             as button, dialog, etc.
        state(stirng):       the name of the state we want to ensure, such as:
                             filled, checked, empty, not empty, etc.
        find_func(function): function that returns the desired element:

                             def find_func(ctx, name, index=):
                                '''
                                ctx(object):  behave context object
                                name(string): name of the thing to find
                                index(int):   when there are multiple elements
                                              with the same name and you've
                                              specified with_nth=True
                                '''
        state_func(function): function that returns True if the element is in
                              the desired state and False otherwise:

                               def state_func(element):
                                  '''
                                  element(object): the element found
                                  '''
        action_func(function): action that will set the desired state on the
                               element if state_func returns False:
                               def action_func(ctx, element):
                                  '''
                                  ctx(object):  behave context object
                                  element(object): the element found
                                  '''
        with_nth(bool):     when set to True we'll define the expanded set of
                            "nth" steps. default: False
    """

    # undecorated def for reference below
    def base_ensure_the(ctx, thing, name, index=0):
        prefix = nth_to_ordinal(index)
        element = find_func(ctx, name, index=index)

        if element is None:
            raise RuntimeError(f'unable to find the {prefix}{thing} "{name}"')

        if not state_func(element):
            action_func(ctx, element)

    @step(f'I immediately ensure the {thing} "{{name}}" is {state}')
    def immediately_ensure_the(ctx, name, state):
        base_ensure_the(ctx, thing, name)

    @step(f'I ensure the {thing} "{{name}}" is {state}')
    def ensure_the(ctx, name):
        retry(
            base_ensure_the,
            retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
            wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
        )(ctx, thing, name)

    @step(f'I wait to ensure the {thing} "{{name}}" is {state}')
    def wait_to_ensure_the(ctx, name):
        retry(base_ensure_the)(ctx, thing, name)

    @step(
        f'I wait up to "{{seconds}}" seconds to ensure the {thing} "{{name}}" is {state}'
    )
    def wait_up_to_seconds_to_ensure_the(ctx, seconds, name):
        seconds = float(seconds)
        retry(base_ensure_the, wait_up_to_s=seconds)(ctx, thing, name)

    if with_nth:

        @step(
            f'I immediately ensure the "{{nth:nth}}" {thing} "{{name}}" is {state}'
        )
        def immediately_ensure_the_nth(ctx, nth, name):
            base_ensure_the(ctx, thing, name, index=nth)

        @step(f'I ensure the "{{nth:nth}}" {thing} "{{name}}"')
        def ensure_the_nth(ctx, nth, name):
            retry(
                base_ensure_the,
                retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
                wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
            )(ctx, thing, name, index=nth)

        @step(
            f'I wait to ensure the "{{nth:nth}}" {thing} "{{name}}" is {state}'
        )
        def wait_to_ensure_the_nth(ctx, nth, name):
            retry(base_ensure_the)(ctx, thing, name, index=nth)

        @step(
            f'I wait up to "{{seconds}}" seconds to ensure the "{{nth:nth}}" {thing} "{{name}}" is {state}'
        )
        def wait_up_to_ensure_the_nth(ctx, seconds, nth, name):
            seconds = float(seconds)
            retry(base_ensure_the, wait_up_to_s=seconds)(
                ctx, thing, name, index=nth
            )


def define_thing_with_name_in_state_steps(
    thing, state, find_func, is_in_state_func, with_nth=False
):
    """
    defines steps with with the following signatures:

      I should immediately see the {thing} "{name}" is {state_name}
      I should see the {thing} "{name}" is {state_name}
      I wait to see the {thing} "{name}" is {state_name}
      I wait up to "{seconds}" seconds to see the {thing} "{name}" is {state_name}

      when with_nth=True we also define:

      I should immediately see the "{nth}" {thing} "{name}" is {state_name}
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

    # undecorated def for reference below
    def base_should_see_the_in_state(ctx, thing, name, index=0):
        prefix = nth_to_ordinal(index)
        element = find_func(ctx, name, index=index)

        if element is None:
            raise RuntimeError(f'unable to find the {prefix}{thing} "{name}"')

        if not is_in_state_func(element):
            raise RuntimeError(f'{thing} "{name}" is not {state}')
        logger.debug(f'{thing} {name} was in desired state "{state}"')

    @step(f'I should immediately see the {thing} "{{name}}" is {state}')
    def should_immediately_see_the_in_state(ctx, name, index=0):
        base_should_see_the_in_state(ctx, thing, name, index=0)

    @step(f'I should see the {thing} "{{name}}" is {state}')
    def should_see_the_in_state(ctx, name):
        retry(
            base_should_see_the_in_state,
            retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
            wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
        )(ctx, thing, name)

    @step(f'I wait to see the {thing} "{{name}}" is {state}')
    def wait_to_see_the_in_state(ctx, name):
        retry(base_should_see_the_in_state)(ctx, thing, name)

    @step(
        f'I wait up to "{{seconds}}" seconds to see the {thing} "{{name}}" is {state}'
    )
    def wait_up_to_seconds_to_see_the_in_state(ctx, seconds, name):
        seconds = float(seconds)
        retry(base_should_see_the_in_state, wait_up_to_s=seconds)(
            ctx, thing, name
        )

    if with_nth:

        @step(
            f'I should immediately see the "{{nth:nth}}" {thing} "{{name}}" is {state}'
        )
        def base_should_see_the_nth_in_state(ctx, nth, name):
            base_should_see_the_in_state(ctx, thing, name, index=nth)

        @step(f'I should see the "{{nth:nth}}" {thing} "{{name}}" is {state}')
        def should_see_the_nth_in_state(ctx, nth, name):
            retry(
                base_should_see_the_in_state,
                retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
                wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
            )(ctx, thing, name, index=nth)

        @step(f'I wait to see the "{{nth:nth}}" {thing} "{{name}}" is {state}')
        def wait_to_see_the_nth_in_state(ctx, nth, name):
            retry(base_should_see_the_in_state)(ctx, thing, name, index=nth)

        @step(
            f'I wait up to "{{seconds}}" seconds to see the "{{nth:nth}}" {thing} "{{name}}" is {state}'
        )
        def wait_up_to_seconds_to_see_the_nth_in_state(
            ctx, seconds, nth, name
        ):
            seconds = float(seconds)
            retry(base_should_see_the_in_state, wait_up_to_s=seconds)(
                ctx, thing, name, index=nth
            )


def define_run_steps_if_I_can_see_element_with_name_steps(thing, find_func):
    """
    defines steps with with the following signatures:

      I run the following steps if I can immediately see the {thing} "{name}"
      I run the following steps if I can see the {thing} "{name}"

      I run the following steps if I can immediately not see the {thing} "{name}"
      I run the following steps if I can not see the {thing} "{name}"

    parameters:
        thing(string):       name of the thing we're creating the steps for such
                             as button, dialog, etc.
        find_func(function): function that returns the element that matches the
                             name provided and is visible

                             def find_func(ctx, name):
                                '''
                                ctx(object):  behave context object
                                name(string): name of the thing to find
                                '''
    """

    # undecorated def for reference below
    def base_run_if_visibile(ctx, name):
        element = find_func(ctx, name)

        if element is not None:
            run_steps(ctx, ctx.text)

    @step(
        f'I run the following steps if I can immediately see the {thing} "{{name}}"'
    )
    def run_if_immediately_visibile(ctx, name):
        base_run_if_visibile(ctx, name)

    @step(f'I run the following steps if I can see the {thing} "{{name}}"')
    def run_if_visibile(ctx, name):
        retry(
            base_run_if_visibile,
            retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
            wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
        )(ctx, name)

    def base_run_if_not_visibile(ctx, name):
        element = find_func(ctx, name)

        if element is None:
            run_steps(ctx, ctx.text)

    @step(
        f'I immediately run the following steps if I can not see the {thing} "{{name}}"'
    )
    def immediately_run_if_not_visibile(ctx, name):
        base_run_if_not_visibile(ctx, name)

    @step(f'I run the following steps if I can not see the {thing} "{{name}}"')
    def run_if_not_visibile(ctx, name):
        retry(
            base_run_if_not_visibile,
            retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
            wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
        )(ctx, name)


def define_two_thing_interaction_steps(
    action: str,
    action_func,
    thing_1,
    thing_1_find_func,
    preposition: str,
    thing_2,
    thing_2_find_func,
    with_nth=False,
):
    """
    defines steps with with the following signatures:
      I {action} the {thing_1} "{name_1}" {preposition} the {thing_2} "{name_2}"
      I wait to {action} the {thing_1} "{name_1}" {preposition} the {thing_2} "{name_2}"
      I wait up to "{seconds}" seconds to {action} the {thing_1} "{name_1}" {preposition} the {thing_2} "{name_2}"
      ...
      I {action} the {thing_1} "{name_1}" {preposition} the {thing_2} "{name_2}" if they both exist


      when with_nth=True we also define:

      I {action} the "{nth_1}" {thing_1} "{name_1}" {preposition} the "{nth_2}" {thing_2} "{name_2}"
      I wait to {action} the "{nth_1}" {thing_1} "{name_1}" {preposition} the "{nth_2}" {thing_2} "{name_2}"
      I wait up to "{seconds}" seconds to {action} the "{nth_1}" {thing_1} "{name_1}" {preposition} the "{nth_2}" {thing_2} "{name_2}"
      ...
      I {action} the "{nth_1}" {thing_1} "{name_1}" {preposition} the "{nth_2}" {thing_2} "{name_2}" if they both exist

    parameters:
        action(string):      the name of the action being performed, such as:
                             click, disable, etc.
        action_func(function):      function that performs the desired action:

                                    def action_func(ctx, element, ):
                                        '''
                                        ctx(object):  behave context object
                                        element(object): the element found
                                        '''
        thing_1(string):     name of the thing we're creating the steps for such
                             as button, dialog, etc.
        thing_1_find_func(function): function that returns the desired element:

                                     def thing_1_find_func(ctx, name_1, index_1=):
                                        '''
                                        ctx(object):   behave context object
                                        name_1(string):name of the thing to find
                                        index_1(int):    when there are multiple elements
                                                    with the same name and you've
                                                    specified with_nth=True
                                        '''
        preposition(string):    preposition to help with readability as there are
                                many different prepositions that would be valid for
                                a desired action
        thing_2(string):     name of the thing that is being interacted with
                             from the defined action
        thing_2_find_func(function): function that returns the interacted element:

                                     def thing_2_find_func(ctx, name_2, index_2=):
                                        '''
                                        ctx(object):    behave context object
                                        name_2(string): name of the thing to find
                                        index_1(int):     when there are multiple elements
                                                    with the same name and you've
                                                    specified with_nth=True
                                        '''
        with_nth(bool):      when set to True we'll define the expanded set of
                             "nth" steps. default: False
    """

    # undecorated def for reference below
    def base_action_the(
        ctx,
        thing_1,
        name_1,
        thing_2,
        name_2,
        index_1=0,
        index_2=0,
    ):
        prefix_1 = nth_to_ordinal(index_1)
        prefix_2 = nth_to_ordinal(index_2)

        element_1 = thing_1_find_func(ctx, name_1, index_1)
        element_2 = thing_2_find_func(ctx, name_2, index_2)

        if element_1 is None or element_2 is None:
            error_message = []
            if element_1 is None:
                error_message.append(
                    f'Unable to find the {prefix_1}{thing_1} "{name_1}"'
                )
            if element_2 is None:
                error_message.append(
                    f'Unable to find the {prefix_2}{thing_2} "{name_2}"'
                )

            raise RuntimeError(", ".join(error_message))

        else:
            action_func(ctx, element_1, element_2)
            logger.debug(
                f'Successfully executed {action} {prefix_1}{thing_1} "{name_1}" {preposition} {prefix_2}{thing_2} "{name_2}"'
            )

    @step(
        f'I immediately {action} the {thing_1} "{{name_1}}" {preposition} the {thing_2} "{{name_2}}"'
    )
    def immediately_action_the(ctx, name_1, name_2):
        base_action_the(ctx, thing_1, name_1, thing_2, name_2)

    @step(
        f'I {action} the {thing_1} "{{name_1}}" {preposition} the {thing_2} "{{name_2}}"'
    )
    def action_the(ctx, name_1, name_2):
        retry(
            base_action_the,
            retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
            wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
        )(ctx, thing_1, name_1, thing_2, name_2)

    @step(
        f'I wait to {action} the {thing_1} "{{name_1}}" {preposition} the {thing_2} "{{name_2}}"'
    )
    def wait_to_action_the(ctx, name_1, name_2):
        retry(base_action_the)(ctx, thing_1, name_1, thing_2, name_2)

    @step(
        f'I wait up to "{{seconds}}" seconds to {action} the {thing_1} "{{name_1}}" {preposition} the {thing_2} "{{name_2}}"'
    )
    def wait_up_to_seconds_to_action_the(ctx, seconds, name_1, name_2):
        seconds = float(seconds)
        retry(base_action_the, wait_up_to_s=seconds)(
            ctx, thing_1, name_1, thing_2, name_2
        )

    if with_nth:

        @step(
            f'I immediately {action} the "{{nth_1:nth}}" {thing_1} "{{name_1}}" {preposition} the "{{nth_2:nth}}" {thing_2} "{{name_2}}"'
        )
        def immediately_action_the_nth_i_nth(
            ctx, nth_1, name_1, nth_2, name_2
        ):
            base_action_the(
                ctx,
                thing_1,
                name_1,
                thing_2,
                name_2,
                index_1=nth_1,
                index_2=nth_2,
            )

        @step(
            f'I {action} the "{{nth_1:nth}}" {thing_1} "{{name_1}}" {preposition} the "{{nth_2:nth}}" {thing_2} "{{name_2}}"'
        )
        def action_the_nth_i_nth(ctx, nth_1, name_1, nth_2, name_2):
            retry(
                base_action_the,
                retry_after_s=float(CONFIG["CUCU_SHORT_UI_RETRY_AFTER_S"]),
                wait_up_to_s=float(CONFIG["CUCU_SHORT_UI_WAIT_TIMEOUT_S"]),
            )(
                ctx,
                thing_1,
                name_1,
                thing_2,
                name_2,
                index_1=nth_1,
                index_2=nth_2,
            )

        @step(
            f'I wait to {action} the "{{nth_1:nth}}" {thing_1} "{{name_1}}" {preposition} the "{{nth_2:nth}}" {thing_2} "{{name_2}}"'
        )
        def wait_to_action_the_nth_ith(ctx, nth_1, name_1, nth_2, name_2):
            retry(base_action_the)(
                ctx,
                thing_1,
                name_1,
                thing_2,
                name_2,
                index_1=nth_1,
                index_2=nth_2,
            )

        @step(
            f'I wait up to "{{seconds}}" seconds to {action} the "{{nth_1:nth}}" {thing_1} "{{name_1}}" {preposition} the "{{nth_2:nth}}" {thing_2} "{{name_2}}"'
        )
        def wait_up_to_action_the_nth_i_nth(
            ctx, seconds, nth_1, name_1, nth_2, name_2
        ):
            seconds = float(seconds)
            retry(base_action_the, wait_up_to_s=seconds)(
                ctx,
                thing_1,
                name_1,
                thing_2,
                name_2,
                index_1=nth_1,
                index_2=nth_2,
            )

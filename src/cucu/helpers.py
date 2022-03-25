import humanize

from behave import step
from cucu import retry


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
        prefix = "" if index == 0 else f"{humanize.ordinal(index)} "
        element = find_func(ctx, name, index=index)

        if element is None:
            raise RuntimeError(f'unable to find the {prefix}{thing} "{name}"')

    def should_not_see(ctx, thing, name, index=0):
        prefix = "" if index == 0 else f"{humanize.ordinal(index)} "
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
        prefix = "" if index == 0 else f"{humanize.ordinal(index)} "
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
    def wait_up_to_seconds_to_action_the(ctx, name):
        seconds = float(seconds)
        retry(action_it, wait_up_to_s=seconds)(ctx, thing, name)

    if with_nth:

        @step(f'I {action} the "{{nth:nth}}" {thing} "{{name}}"')
        def action_the(ctx, nth, name):
            action_it(ctx, thing, name, index=nth)

        @step(f'I wait to {action} the "{{nth:nth}}" {thing} "{{name}}"')
        def action_the(ctx, nth, name):
            retry(action_it)(ctx, thing, name, index=nth)

        @step(
            f'I wait up to "{{seconds}}" seconds to {action} the "{{nth:nth}}" {thing} "{{name}}"'
        )
        def action_the(ctx, seconds, nth, name):
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
        prefix = "" if index == 0 else f"{humanize.ordinal(index)} "
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

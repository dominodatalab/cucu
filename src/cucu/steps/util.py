from behave import step
from cucu.config import CONFIG
from tenacity import Retrying, stop_after_delay, wait_fixed


def define_should_see_steps(thing, find_func):
    """
    defines behave steps with with the following signatures:

      I should see the "{thing}"
      I should not see the "{thing}"
      I wait to see the "{thing}"
      I wait to not see the "{thing}"
      I wait up to "{seconds}" seconds to see the "{thing}"
      I wait up to "{seconds}" seconds to not see the "{thing}"

    """

    def should_see(context, thing, name):
        element = find_func(context, name)

        if element is None:
            raise RuntimeError(f'unable to find {thing} "{name}"')

    def should_not_see(context, thing, name):
        element = find_func(context, name)

        if element is not None:
            raise RuntimeError(f'able to find {thing} "{name}"')

    @step(f'I should see the {thing} "{{name}}"')
    def should_see_the(context, name):
        should_see(context, thing, name)

    @step(f'I should not see the {thing} "{{name}}"')
    def should_not_see_the(context, name):
        should_not_see(context, thing, name)

    wait_timeout_s = float(CONFIG["CUCU_STEP_WAIT_TIMEOUT_MS"]) / 1000.0
    retry_after_s = float(CONFIG["CUCU_STEP_RETRY_AFTE_RMS"]) / 1000.0

    @step(f'I wait to see the {thing} "{{name}}"')
    def wait_to_see_the(context, name):
        retry_if = wait_fixed(wait_timeout_s) | stop_after_delay(retry_after_s)
        for attempt in Retrying(retry_if):
            with attempt:
                should_see(context, thing, name)

    @step(f'I wait up to "{{seconds}}" seconds to see the {thing} "{{name}}"')
    def wait_up_to_seconds_to_see_the(context, seconds, name):
        retry_if = wait_fixed(seconds) | stop_after_delay(retry_after_s)
        for attempt in Retrying(retry_if):
            with attempt:
                should_see(context, thing, name)


def define_action_steps(thing, action, func):
    """
    defines behave steps with with the following signatures:

      I {action} the {thing} "{thing}"
      I wait to {action} the {thing} "{thing}"
      I wait up to "{seconds}" seconds to {action} the {thing} "{thing}"

    """

    @step(f'I {action} the {thing} "{{name}}"')
    def action_the_thing(context, name):
        func(name)

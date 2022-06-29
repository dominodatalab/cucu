import re

from behave import step
from cucu import config


@step('I set the variable "{variable}" to "{value}"')
def set_variable_to(_, variable, value):
    config.CONFIG[variable] = value


@step('I set the variable "{variable}" to the following')
def set_variable_to_the_following(ctx, variable):
    config.CONFIG[variable] = ctx.text


@step('I should see "{this}" is empty')
def should_see_is_empty(_, this):
    if this or len(this) != 0:
        raise RuntimeError(f"{this} is not empty")


@step('I should see "{this}" is equal to "{that}"')
def should_see_is_equal(_, this, that):
    if this != that:
        raise RuntimeError(f"{this} is not equal to {that}")


@step('I should see "{this}" is not equal to "{that}"')
def should_see_is_equal(_, this, that):
    if this == that:
        raise RuntimeError(f"{this} is equal to {that}")


@step('I should see "{this}" contains "{that}"')
def should_see_it_contains(_, this, that):
    if that not in this:
        raise RuntimeError(f"{this} does not contain {that}")


@step('I should see "{this}" contains the following')
def should_see_it_contains_the_following(ctx, this):
    if ctx.text not in this:
        raise RuntimeError(f"{this} does not contain {ctx.text}")


@step('I should see "{this}" does not contain "{that}"')
def should_see_it_doest_not_contain(_, this, that):
    if that in this:
        raise RuntimeError(f"{this} contains {that}")


@step('I should see "{this}" does not contain the following')
def should_see_it_does_not_contain(ctx, this):
    if ctx.text in this:
        raise RuntimeError(f"{this} contain {ctx.text}")


@step('I should see "{this}" is equal to the following')
def should_see_is_equal_to_the_following(ctx, this):
    that = ctx.text

    if this != that:
        raise RuntimeError(f"{this} is not equal to {that}")


@step('I should see "{this}" matches "{that}"')
def should_see_matches(_, this, that):
    if re.match(that, this) is None:
        raise RuntimeError(f"{this} does not match {that}")


@step('I should see "{this}" matches the following')
def should_see_matches_the_following(ctx, this):
    that = ctx.text

    if re.match(that, this) is None:
        raise RuntimeError(f"{this}\ndoes not match:\n{that}")


@step('I should see "{this}" does not match the following')
def should_does_not_see_matches_the_following(ctx, this):
    that = ctx.text

    if re.match(that, this) is not None:
        raise RuntimeError(f"{this}\nmatches:\n{that}")


def extract_and_save(regex, value, name, variable):
    match = re.match(regex, value)

    if match is None:
        raise RuntimeError(
            f'regex "{regex}" did not match anything in the value "{value}"'
        )

    groups = match.groupdict()

    if name in groups:
        config.CONFIG[variable] = groups[name]

    else:
        raise RuntimeError(
            f'group "{name}" not found when applying regex "{regex}" to "{value}"'
        )


@step(
    'I apply the regex "{regex}" to "{value}" and save the group "{name}" to the variable "{variable}"'
)
def apply_regex_and_save(ctx, regex, value, name, variable):
    extract_and_save(regex, value, name, variable)


@step(
    'I apply the following regex to "{value}" and save the group "{name}" to the variable "{variable}"'
)
def apply_the_following_regex_and_save(ctx, value, name, variable):
    extract_and_save(ctx.text, value, name, variable)

import re

from cucu import config


def search(regex, value):
    """
    search for a matching regex within the value provided.
    """
    match = re.search(regex, value)

    if match is None:
        raise RuntimeError(f'"{regex}" did not match anything in "{value}"')


def search_and_save(regex, value, name, variable):
    """
    search for a matching regex within the value provided and then save the value
    of the group name provided to the variable name provided.
    """
    match = re.search(regex, value)

    if match is None:
        raise RuntimeError(f'"{regex}" did not match anything in "{value}"')

    groups = match.groupdict()

    if name in groups:
        config.CONFIG[variable] = groups[name]

    else:
        raise RuntimeError(
            f'group "{name}" not found when searching for regex "{regex}" in "{value}"'
        )


def match_and_save(regex, value, name, variable):
    """
    match the regex in the value provided and then save the value of the group
    name provided to the variable name provided.
    """
    match = re.match(regex, value)

    if match is None:
        raise RuntimeError(f'"{regex}" did not match "{value}"')

    groups = match.groupdict()

    if name in groups:
        config.CONFIG[variable] = groups[name]

    else:
        raise RuntimeError(
            f'group "{name}" not found when matching regex "{regex}" to "{value}"'
        )

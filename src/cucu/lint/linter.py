import glob
import importlib
import os
import re
import yaml

from cucu import logger
from cucu.cli.steps import load_cucu_steps


def load_lint_rules(filepath):
    """
    load all of the lint rules from the filepath provided

    Returns:
        hashmap of of lint rules
    """
    all_rules = {}
    filepath = os.path.abspath(filepath)

    if os.path.isdir(filepath):
        basepath = os.path.join(filepath, "**/*.yaml")
        lint_rule_filepaths = glob.iglob(basepath, recursive=True)

    else:
        lint_rule_filepaths = [filepath]

    for lint_rule_filepath in lint_rule_filepaths:
        logger.debug(f"loading lint rules from {lint_rule_filepath}")

        with open(lint_rule_filepath, "r", encoding="utf8") as _input:
            rules = yaml.safe_load(_input.read())

        for (rule_name, rule) in rules.items():
            if rule_name in all_rules:
                raise RuntimeError(
                    f"found duplicate rule names {rule_name}, please correct one of the locations."
                )

            all_rules[rule_name] = rule

    return all_rules


def parse_matcher(name, rule_name, rule, line, state):
    """
    parses the "matcher" from the rule provided and then returns the tuple:
    (matched, extra_matcher_message) where matched is a boolean indicating that
    the rule name matcher name and rule matched on the line provided and the
    extra_matcher_message is used when reporting the linting failure upstream.
    """
    if name not in rule:
        # when the name provided isn't in the rule then we simply have a no-op
        # where this specific matcher name wasn't even used.
        return (True, "")

    if "match" in rule[name]:
        if line is None:
            return (False, "")

        match = re.match(rule[name]["match"], line)

        if match is None:
            # no match on the specified rule means there's not violation to
            # report
            return (False, "")

        cwd = f"{os.getcwd()}/"
        if "unique_group_per_feature" in rule[name]:
            value = match.groups()[0]
            feature_filepath = state["current_feature_filepath"]
            # make the path relative to the current working directory
            feature_filepath = feature_filepath.replace(cwd, "")

            if rule_name not in state["unique_per_feature"]:
                state["unique_per_feature"][rule_name] = {}

            if value in state["unique_per_feature"][rule_name]:
                # we have another feature which already has this value in use.
                other_filepath = state["unique_per_feature"][rule_name][value]
                # make the path relative to the current working directory
                other_filepath = other_filepath.replace(cwd, "")
                return (
                    True,
                    f', "{value}" used in "{feature_filepath}" and "{other_filepath}"',
                )

            state["unique_per_feature"][rule_name][value] = feature_filepath
            return (False, "")

        return (True, "")
    else:
        raise RuntimeError(f"unsupported matcher for {name}")


def lint_line(state, rules, steps, line_number, lines, filepath):
    """ """
    if line_number >= 1:
        previous_line = lines[line_number - 1]

    else:
        previous_line = None

    current_line = lines[line_number]

    if line_number + 1 < len(lines):
        next_line = lines[line_number + 1]
    else:
        next_line = None

    logger.debug(f'linting line "{current_line}"')

    violations = []
    for rule_name in rules.keys():
        logger.debug(f' * checking against rule "{rule_name}"')
        rule = rules[rule_name]
        (current_matcher, current_message) = parse_matcher(
            "current_line",
            rule_name,
            rule,
            current_line,
            state,
        )
        (previous_matcher, previous_message) = parse_matcher(
            "previous_line",
            rule_name,
            rule,
            previous_line,
            state,
        )
        (next_matcher, next_message) = parse_matcher(
            "next_line",
            rule_name,
            rule,
            next_line,
            state,
        )

        logger.debug(
            f"previous matcher {previous_matcher} current matcher {current_matcher} next matcher {next_matcher}"
        )

        if current_matcher and previous_matcher and next_matcher:
            type = rule["type"][0].upper()
            message = rule["message"]

            if "fix" in rule:
                fix = rule["fix"]
            else:
                fix = None

            violations.append(
                {
                    "location": {
                        "filepath": os.path.relpath(filepath),
                        "line": line_number,
                    },
                    "type": type,
                    "message": f"{message}{previous_message}{current_message}{next_message}",
                    "fix": fix,
                }
            )

    # find any undefined steps and mark them as an unfixable violation
    current_line = current_line.strip()
    for step_name in steps:
        # step with no location/type/etc is an undefined step
        if steps[step_name] is None:
            if current_line.find(step_name) != -1:
                violations.append(
                    {
                        "location": {
                            "filepath": os.path.relpath(filepath),
                            "line": line_number,
                        },
                        "type": "error",
                        "message": f'undefined step "{step_name}"',
                        "fix": None,
                    }
                )

    return violations


def fix(violations):
    """
    fix the violations found in a set of violations relating to a single
    feature file.
    """
    if not violations:
        return

    deletions = []
    filepath = violations[0]["location"]["filepath"]
    lines = open(filepath, "r").read().split("\n")

    for violation in violations:
        if violation["fix"] is None:
            violation["fixed"] = False

        else:
            line_number = violation["location"]["line"]
            line_to_fix = lines[line_number]

            if "delete" in violation["fix"]:
                # store the deletions to do at the end
                deletions.append(violation)

            elif "match" in violation["fix"]:
                match = violation["fix"]["match"]
                replace = violation["fix"]["replace"]
                fixed_line = re.sub(match, replace, line_to_fix)
                lines[line_number] = fixed_line
                violation["fixed"] = True

            else:
                raise RuntimeError(f"unknown fix type in {violation}")

    # sort the deletions from bottom to the top of the file and then perform
    # the deletions
    deletions.sort(key=lambda x: x["location"]["line"], reverse=True)
    for violation in deletions:
        del lines[violation["location"]["line"]]
        violation["fixed"] = True

    with open(filepath, "w") as output:
        output.write("\n".join(lines))

    return violations


def load_builtin_lint_rules():
    """
    load internal builtin lint rules and used primarily for unit testing
    """
    cucu_path = os.path.dirname(importlib.util.find_spec("cucu").origin)
    lint_rules_path = os.path.join(cucu_path, "lint", "rules")
    return load_lint_rules(lint_rules_path)


def lint(filepath):
    """
    lint the filepath provided which could be a base directory where many
    feature files exists and we must traverse recursively or a specific file.

    Params:
        filepath(string): path to a directory or feature file to lint

    Returns:
        a generator of violations per file, so each value yielded to the
        generator is a list of violations within the same file
    """
    # load the base lint rules
    rules = load_builtin_lint_rules()
    steps, steps_error = load_cucu_steps(filepath=filepath)

    # state object used to carry state from the top level linting function down
    # to the functions handling the lint rules and reporting on lint failures
    state = {"unique_per_feature": {}}

    if steps_error:
        yield [
            {
                "type": "steps_error",
                "message": steps_error,
            }
        ]

    filepath = os.path.abspath(filepath)

    if os.path.isdir(filepath):
        basepath = os.path.join(filepath, "**/*.feature")
        # XXX: for now sorted by name... we could expose some options for other
        #      sorting orders if it makes sense
        feature_filepaths = sorted(glob.iglob(basepath, recursive=True))

    else:
        feature_filepaths = [filepath]

    for feature_filepath in feature_filepaths:
        state["current_feature_filepath"] = feature_filepath

        lines = open(feature_filepath).read().split("\n")
        line_number = 0

        violations = []
        in_docstring = {
            '"""': False,
            "'''": False,
        }

        for line in lines:
            feature_match = re.match(".*Feature: (.*)", line)
            if feature_match is not None:
                state["current_feature_name"] = feature_match.groups(0)

            scenario_match = re.match("  Scenario: (.*)", line)
            if scenario_match is not None:
                state["current_scenario_name"] = scenario_match.groups(0)

            # maintain state of if we're inside a docstring and if we are then
            # do not apply any linting rules as its a freeform space for text
            if line.strip() == '"""':
                in_docstring['"""'] = not in_docstring['"""']

            if line.strip() == "'''":
                in_docstring["'''"] = not in_docstring["'''"]

            if not (in_docstring['"""'] or in_docstring["'''"]):
                for violation in lint_line(
                    state, rules, steps, line_number, lines, feature_filepath
                ):
                    violations.append(violation)

            line_number += 1

        yield violations

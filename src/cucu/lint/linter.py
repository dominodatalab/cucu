import os
import glob
import importlib
import re
import yaml

from cucu import logger


def load_lint_rules(filepath):
    """
    load all of the lint rules from the filepath provided

    Returns:
        hashmap of of lint rules
    """
    all_rules = {}
    filepath = os.path.abspath(filepath)

    if os.path.isdir(filepath):
        basepath = os.path.join(filepath, '**/*.yaml')
        lint_rule_filepaths = glob.iglob(basepath, recursive=True)

    else:
        lint_rule_filepaths = [filepath]

    for lint_rule_filepath in lint_rule_filepaths:
        logger.debug(f'loading lint rules from {lint_rule_filepath}')
        rules = yaml.safe_load(open(lint_rule_filepath, 'r').read())

        for (rule_name, rule) in rules.items():
            # XXX: check for duplicate rule names
            all_rules[rule_name] = rule

    return all_rules


def lint_line(rules, line_number, lines, filepath):
    """
    """
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

        current_matcher = True
        previous_matcher = True
        next_matcher = True

        if 'current_line' in rule:
            if 'match' in rule['current_line']:
                current_matcher = re.match(rule['current_line']['match'], current_line)
            else:
                raise RuntimeError('unsupported matcher for current_line')

        if 'previous_line' in rule and previous_line is not None:
            if 'match' in rule['previous_line']:
                previous_matcher = re.match(rule['previous_line']['match'], previous_line)
            else:
                raise RuntimeError('unsupported matcher for previous_line')

        if 'next_line' in rule and next_line is not None:
            if 'match' in rule['next_line']:
                next_matcher = re.match(rule['next_line']['match'], next_line)
            else:
                raise RuntimeError('unsupported matcher for next_line')

        logger.debug(f'previous matcher {previous_matcher} current matcher {current_matcher} next matcher {next_matcher}')

        if current_matcher and previous_matcher and next_matcher:
            type = rule['type'][0].upper()
            message = rule['message']

            if 'fix' in rule:
                fix = rule['fix']
            else:
                fix = None

            violations.append({
                'location': {
                    'filepath': os.path.relpath(filepath),
                    'line': line_number
                },
                'type': type,
                'message': message,
                'fix': fix,
            })

    return violations


def fix(violations):
    """
    fix the violations found in a set of violations relating to a single
    feature file.
    """
    if not violations:
        return

    deletions = []
    filepath = violations[0]['location']['filepath']
    lines = open(filepath, 'r').read().split('\n')

    for violation in violations:
        line_number = violation['location']['line']
        line_to_fix = lines[line_number]

        if 'delete' in violation['fix']:
            # store the deletions to do at the end
            deletions.append(violation)

        elif 'match' in violation['fix']:
            match = violation['fix']['match']
            replace = violation['fix']['replace']
            fixed_line = re.sub(match, replace, line_to_fix)
            lines[line_number] = fixed_line
            violation['fixed'] = True

        else:
            raise RuntimeError(f'unknown fix type in {violation}')

    # sort the deletions from bottom to the top of the file and then perform
    # the deletions
    deletions.sort(key=lambda x: x['location']['line'], reverse=True)
    for violation in deletions:
        del lines[violation['location']['line']]
        violation['fixed'] = True

    with open(filepath, 'w') as output:
        output.write('\n'.join(lines))

    return violations


def load_builtin_lint_rules():
    """
    load internal builtin lint rules and used primarily for unit testing
    """
    cucu_path = os.path.dirname(importlib.util.find_spec('cucu').origin)
    lint_rules_path = os.path.join(cucu_path, 'lint', 'rules')
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

    filepath = os.path.abspath(filepath)

    if os.path.isdir(filepath):
        basepath = os.path.join(filepath, '**/*.feature')
        feature_filepaths = glob.iglob(basepath, recursive=True)

    else:
        feature_filepaths = [filepath]

    for feature_filepath in feature_filepaths:
        lines = open(feature_filepath).read().split('\n')
        line_number = 0

        violations = []
        in_docstring = False
        for line in lines:
            # maintain state of if we're inside a docstring and if we are then
            # do not apply any linting rules as its a freeform space for text
            if line.strip() == '"""' or line.strip() == "'''":
                in_docstring = not in_docstring

            if not in_docstring:
                for violation in lint_line(rules, line_number, lines, feature_filepath):
                    violations.append(violation)

            line_number += 1

        yield violations

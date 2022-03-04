import json
import re
import subprocess


from behave.__main__ import main as behave_main


def print_human_readable_steps():
    """
    print steps in a human readable format
    """
    args = ['--format=steps.doc', '--dry-run', '--no-summary']

    exit_code = behave_main(args)

    if exit_code != 0:
        raise RuntimeError('listing steps failed, see above for details')


def load_cucu_steps():
    """
    loads the cucu steps definition using behave and returns an array of
    hashmaps that have the following structure:

        {
            [step_name]: {
                "location": {
                    "filepath": "...",
                    "line": "...",
                }
            }
        }

    Returns:
        an array of hashmaps
    """
    steps_cache = {}
    cucu_steps_output = subprocess.check_output(['cucu', 'steps'])
    cucu_steps_output = cucu_steps_output.decode('utf8')

    for cucu_step in cucu_steps_output.split('\n\n'):
        # each blank line is a '\n\n' which is a split between two step
        # definitions in the output, like so:
        #
        #   @step('I should see "{this}" matches "{that}"')
        #     Function: inner_step()
        #     Location: src/cucu/behave_tweaks.py:64
        #
        #   @step('I should see "{this}" matches the following')
        #     Function: inner_step()
        #     Location: src/cucu/behave_tweaks.py:64
        #
        if cucu_step.strip() == '':
            continue

        step_name, _, location = cucu_step.split('\n')
        step_name = re.match(r"@step\('(.*)'\)", step_name).groups()[0]
        _, filepath, line_number = location.split(':')

        steps_cache[step_name] = {
            'location': {
                'filepath': filepath.strip(),
                'line': line_number.strip(),
            }
        }

    return steps_cache


def print_json_steps():
    """
    pretty print the steps in a JSON fart
    """
    steps = load_cucu_steps()
    print(json.dumps(steps, indent=2, sort_keys=True))

import json
import re
import subprocess


def load_cucu_steps(filepath=None):
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

    undefined steps are marked with a value of None instead of a location. ie:

        {
            [undefined_step_name]: None
        }

    Returns:
        an array of hashmaps
    """
    steps_cache = {}
    args = ["behave", "--dry-run", "--no-summary", "--format", "steps.doc"]

    if filepath is not None:
        args.append(filepath)

    process = subprocess.run(args, capture_output=True)

    if process.returncode != 0:
        print(process.stderr.decode("utf8"))
        raise RuntimeError("failed to load steps, see above for details")

    steps_doc_output = process.stdout.decode("utf8")
    for cucu_step in steps_doc_output.split("@step"):
        # Each line of a step definition looks like so:
        #
        #   @step('I should see "{this}" matches "{that}"')
        #     Function: inner_step()
        #     Location: src/cucu/behave_tweaks.py:64
        #      possibly a doc string here on the function that can be used
        #      to add a little documentation to each step definition
        #
        #   @step('I should see "{this}" matches the following')
        #     Function: inner_step()
        #     Location: src/cucu/behave_tweaks.py:64
        #
        if cucu_step.strip() == "":
            continue

        lines = cucu_step.split("\n")

        #
        # parts[1] is the function name while parts[3:] is the docstring
        # of the step which we can use for documenting usage of the step
        # in the language server
        #
        step_name = lines[0]
        location = lines[2]

        step_name = re.match(r"\('(.*)'\)", step_name).groups()[0]
        _, filepath, line_number = location.split(":")

        steps_cache[step_name] = {
            "location": {
                "filepath": filepath.strip(),
                "line": line_number.strip(),
            }
        }

    # collect any undefined steps
    steps_err_output = process.stderr.decode("utf8")
    for line in steps_err_output.split("\n"):
        # @when(u'I close the current browser caca')
        match = re.match(r"@[a-z]+\(u'([^']+)'\)", line)
        if match:
            step_name = match.group(1)
            steps_cache[step_name] = None

    return steps_cache


def print_json_steps(filepath=None):
    """
    pretty print the steps in a JSON fart
    """
    steps = load_cucu_steps(filepath=filepath)
    print(json.dumps(steps, indent=2, sort_keys=True))


def print_human_readable_steps(filepath=None):
    steps = load_cucu_steps(filepath=filepath)

    for step_name in steps:
        if steps[step_name] is not None:
            print(f"{step_name}")

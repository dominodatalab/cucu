import contextlib
import io
import json
import re

from cucu import behave_tweaks


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
    args = ["--dry-run", "--no-summary", "--format", "steps.doc"]

    if filepath is not None:
        args.append(filepath)

    error = None

    stdout = io.StringIO()
    stderr = io.StringIO()

    with contextlib.redirect_stderr(stderr):
        with contextlib.redirect_stdout(stdout):
            error = behave_tweaks.behave_main(args)

    stdout = stdout.getvalue()
    stderr = stderr.getvalue()

    if stdout.startswith("ParserError"):
        print(stdout)
        raise RuntimeError(
            "unable to parse feature files, see above for details"
        )

    for cucu_step in stdout.split("@step"):
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

        if not cucu_step.startswith("("):
            #
            # any block of lines between the `@step` that doesn't start with the
            # character ( is an error being reported behave when loading steps
            # and we'll ignore it when processing the step definitions and then
            # report the actual underlying trace reported in STDERR below
            #
            print("unable to parse some step lines")
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
    for line in stderr.split("\n"):
        # @when(u'I close the current browser caca')
        match = re.match(r"@[a-z]+\(u'([^']+)'\)", line)
        if match:
            step_name = match.group(1)
            steps_cache[step_name] = None

    if error == 0:
        return (steps_cache, None)

    else:
        return (steps_cache, stderr)


def print_json_steps(filepath=None):
    """
    pretty print the steps in a JSON fart
    """
    steps, steps_error = load_cucu_steps(filepath=filepath)
    print(json.dumps(steps, indent=2, sort_keys=True))


def print_human_readable_steps(filepath=None):
    steps, steps_error = load_cucu_steps(filepath=filepath)

    for step_name in steps:
        if steps[step_name] is not None:
            if filepath in steps[step_name]["location"]["filepath"]:
                print(f"custom: {step_name}")
            else:
                print(f"cucu:   {step_name}")

    if steps_error is not None:
        print(steps_error)
        raise RuntimeError("Failure loading some steps, see above for details")

import contextlib
import io

from cucu import behave_tweaks, init_global_hook_variables


def collect_cucu_tags(filepath=None, tags=tuple()):
    """
    Collects tests using behave and extracts the tags applied to them.

    Returns:
        A list of tags
    """
    args = [
        "--dry-run",
        "--no-summary",
        "--format",
        "cucu.formatter.tags:CucuTagCollectorFormatter",
    ]

    if len(tags) > 0:
        [args.extend(["--tags", tag]) for tag in tags]

    if filepath is not None:
        args.append(filepath)

    stdout = io.StringIO()
    stderr = io.StringIO()

    init_global_hook_variables()
    with contextlib.redirect_stderr(stderr):
        with contextlib.redirect_stdout(stdout):
            behave_tweaks.behave_main(args)

    stdout = [
        tag for tag in stdout.getvalue().split("\n") if len(tag.strip()) > 0
    ]

    if len(stdout) > 0 and stdout[0].startswith("USING RUNNER:"):
            # remove the first line of the output so that linter won't error out trying to parse it as a step
            stdout = stdout[1:]

    if len(stdout) > 0 and  stdout[0].startswith("ParserError"):
        raise RuntimeError(
            "Unable to parse feature files. Please double-check the syntax of your feature files."
            )
    return stdout

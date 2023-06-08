import atexit
import os
import shlex
import subprocess
import tempfile

from cucu import config, logger, step


def run_command(
    command,
    stdout_var=None,
    stderr_var=None,
    exit_code_var=None,
    check_exit_code=None,
):
    args = shlex.split(command)
    process = subprocess.run(args, capture_output=True)

    if exit_code_var:
        config.CONFIG[exit_code_var] = str(process.returncode)

    stdout = process.stdout.decode("utf8")
    stderr = process.stderr.decode("utf8")

    if stdout_var:
        config.CONFIG[stdout_var] = config.CONFIG.escape(stdout)

    if stderr_var:
        config.CONFIG[stderr_var] = config.CONFIG.escape(stderr)

    return_code = process.returncode
    if check_exit_code is not None and int(check_exit_code) != return_code:
        logger.error(f"STDOUT:\n{stdout}\n")
        logger.error(f"STDERR:\n{stderr}\n")
        raise RuntimeError(
            f"expected exit code {check_exit_code}, got {return_code}, see above for details"
        )

    else:
        logger.debug(f"STDOUT:\n{stdout}\n")
        logger.debug(f"STDERR:\n{stderr}\n")


def run_script(
    script,
    stdout_var=None,
    stderr_var=None,
    exit_code_var=None,
    check_exit_code=None,
):
    script_fd, script_filename = tempfile.mkstemp()
    os.close(script_fd)
    atexit.register(os.remove, script_filename)

    with open(script_filename, "wb") as script_file:
        script_file.write(script.encode())

    os.chmod(script_filename, 0o755)
    process = subprocess.run(
        [script_file.name],
        capture_output=True,
        shell=True,
    )  # nosec

    if exit_code_var:
        config.CONFIG[exit_code_var] = str(process.returncode)

    stdout = process.stdout.decode("utf8")
    stderr = process.stderr.decode("utf8")

    if stdout_var:
        config.CONFIG[stdout_var] = config.CONFIG.escape(stdout)

    if stderr_var:
        config.CONFIG[stderr_var] = config.CONFIG.escape(stderr)

    return_code = process.returncode
    if check_exit_code is not None and int(check_exit_code) != return_code:
        logger.error(f"STDOUT:\n{stdout}\n")
        logger.error(f"STDERR:\n{stderr}\n")
        raise RuntimeError(
            f"expected exit code {check_exit_code}, got {return_code}, see above for details"
        )
    else:
        logger.debug(f"STDOUT:\n{stdout}\n")
        logger.debug(f"STDERR:\n{stderr}\n")


@step(
    'I run the command "{command}" and save stdout to "{stdout_var}", stderr to "{stderr_var}", exit code to "{exit_code_var}"'
)
def runs_command_and_save_everything(
    context, command, stdout_var, stderr_var, exit_code_var
):
    run_command(
        command,
        stdout_var=stdout_var,
        stderr_var=stderr_var,
        exit_code_var=exit_code_var,
    )


@step(
    'I run the command "{command}" and save stdout to "{stdout_var}", stderr to "{stderr_var}" and expect exit code "{exit_code}"'
)
def runs_command_and_check_exit_code(
    context, command, stdout_var, stderr_var, exit_code
):
    run_command(
        command,
        stdout_var=stdout_var,
        stderr_var=stderr_var,
        check_exit_code=exit_code,
    )


@step(
    'I run the command "{command}" and save stdout to "{stdout_var}" and expect exit code "{exit_code}"'
)
def runs_command__and_save_stdout_and_check_exit_code(
    context, command, stdout_var, exit_code
):
    run_command(
        command,
        stdout_var=stdout_var,
        check_exit_code=exit_code,
    )


@step(
    'I run the command "{command}" and save stdout to "{stdout_var}", exit code to "{exit_code_var}"'
)
def run_command_and_save_stdout_and_exit_code(
    context, command, stdout_var, exit_code_var
):
    run_command(command, stdout_var=stdout_var, exit_code_var=exit_code_var)


@step('I run the command "{command}" and save exit code to "{exit_code_var}"')
def run_command_and_save_exit_code(context, command, exit_code_var):
    run_command(command, exit_code_var=exit_code_var)


@step('I run the command "{command}" and expect exit code "{exit_code}"')
def run_command_and_expect_exit_code(context, command, exit_code):
    run_command(command, check_exit_code=exit_code)


@step(
    'I run the following script and save stdout to "{stdout_var}", stderr to "{stderr_var}", exit code to "{exit_code_var}"'
)
def run_script_and_save_everything(
    context, stdout_var, stderr_var, exit_code_var
):
    run_script(
        context.text,
        stdout_var=stdout_var,
        stderr_var=stderr_var,
        exit_code_var=exit_code_var,
    )


@step(
    'I run the following script and save stdout to "{stdout_var}", stderr to "{stderr_var}" and expect exit code "{exit_code}"'
)
def run_script_and_check_exit_code(context, stdout_var, stderr_var, exit_code):
    run_script(
        context.text,
        stdout_var=stdout_var,
        stderr_var=stderr_var,
        check_exit_code=exit_code,
    )


@step('I run the following script and expect exit code "{exit_code}"')
def run_script_and_expect_exit_code(context, exit_code):
    run_script(
        context.text,
        check_exit_code=exit_code,
    )

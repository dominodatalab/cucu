import os
import shlex
import subprocess

from behave import step
from cucu import config, logger


def run_command(command, stdout_var=None, stderr_var=None, exit_code_var=None):
    args = shlex.split(command)
    process = subprocess.run(args, capture_output=True)

    if exit_code_var:
        config.CONFIG[exit_code_var] = str(process.returncode)

    stdout = process.stdout.decode("utf8")
    stderr = process.stderr.decode("utf8")

    if stdout_var:
        config.CONFIG[stdout_var] = stdout

    if stderr_var:
        config.CONFIG[stderr_var] = stderr

    logger.debug(f"STDOUT:\n{stdout}\n")
    logger.debug(f"STDERR:\n{stderr}\n")


def run_script(script, stdout_var=None, stderr_var=None, exit_code_var=None):
    shell_command = os.environ.get("SHELL", "/bin/sh")
    process = subprocess.run(
        [shell_command], capture_output=True, shell=True, input=script.encode()
    )

    if exit_code_var:
        config.CONFIG[exit_code_var] = str(process.returncode)

    stdout = process.stdout.decode("utf8")
    stderr = process.stderr.decode("utf8")

    if stdout_var:
        config.CONFIG[stdout_var] = stdout

    if stderr_var:
        config.CONFIG[stderr_var] = stderr

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
    'I run the command "{command}" and save stdout to "{stdout_var}", exit code to "{exit_code_var}"'
)
def run_command_and_save_stdout_and_exit_code(
    context, command, stdout_var, exit_code_var
):
    run_command(command, stdout_var=stdout_var, exit_code_var=exit_code_var)


@step('I run the command "{command}" and save exit code to "{exit_code_var}"')
def run_command_and_save_exit_code(context, command, exit_code_var):
    run_command(command, exit_code_var=exit_code_var)


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

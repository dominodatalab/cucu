import shlex
import subprocess

from behave import step
from cucu import config


@step('I run the command "{command}" and save stdout to "{stdout_var}", stderr to "{stderr_var}" and exit code to "{exit_code_var}"')
def runs_the_command(context, command, stdout_var, stderr_var, exit_code_var):
    args = shlex.split(command)
    process = subprocess.run(args, capture_output=True)
    context.previous_process = process

    config.CONFIG[exit_code_var] = str(process.returncode)
    config.CONFIG[stdout_var] = process.stdout.decode('utf8')
    config.CONFIG[stderr_var] = process.stderr.decode('utf8')

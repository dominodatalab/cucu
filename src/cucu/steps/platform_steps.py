import sys

from cucu import run_steps, step


@step("I skip this scenario if not on mac")
def skip_scenario_if_on_mac(ctx):
    if "darwin" not in sys.platform:
        ctx.scenario.skip(reason="skipping scenario since we're not on a mac")


@step("I skip this scenario if not on linux")
def skip_scenario_if_on_linuxc(ctx):
    if "linux" not in sys.platform:
        ctx.scenario.skip(
            reason="skipping scenario since we're not on a linux"
        )


@step("I run the following steps if on mac")
def run_steps_if_on_mac(ctx):
    if "darwin" in sys.platform:
        run_steps(ctx, ctx.text)


@step("I run the following steps if on linux")
def run_steps_if_on_linux(ctx):
    if "linux" in sys.platform:
        run_steps(ctx, ctx.text)

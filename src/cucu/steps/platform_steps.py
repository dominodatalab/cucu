import sys

from cucu import step


@step("I skip this test if not on mac")
def skip_test_if_on_mac(ctx):
    if "darwin" not in sys.platform:
        ctx.scenario.skip(reason="skipping scenario since we're not on a mac")


@step("I skip this test if not on linux")
def skip_test_if_on_linuxc(ctx):
    if "linux" not in sys.platform:
        ctx.scenario.skip(reason="skipping scenario since we're not on a linux")

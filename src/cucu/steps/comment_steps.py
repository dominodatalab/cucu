from behave import use_step_matcher

from cucu import step

use_step_matcher("re")  # use regex to match comments


@step("#.*")
def comment_step(ctx):
    """
    A no-op step so that we can see "comments" in results and report.
    Usage: add `* #` to the line you want to show up.
    """
    pass


use_step_matcher("parse")  # set this back to cucu's default matcher parser

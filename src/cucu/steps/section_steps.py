from behave import use_step_matcher

from cucu import step

use_step_matcher("re")  # use regex to match section heading patterns


@step("(#{1,4})\\s*(.*)")
def section_step(ctx, heading_level, section_text):
    """
    A section heading step that organizes scenarios into logical sections.

    Usage:
        * # Main section
        * ## Subsection
        * ### Sub-subsection
        * #### Deep subsection

    The number of # characters determines the heading level (1-4).
    This step is a no-op but provides structure in the HTML report.
    """

    pass


use_step_matcher("parse")  # set this back to cucu's default matcher parser

from behave import use_step_matcher

from cucu import step
from cucu.config import CONFIG

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
    # Count the number of # characters to determine heading level (1-4)
    level = len(heading_level)

    from cucu.database.hooks import create_section_in_section_step

    create_section_in_section_step(
        ctx, level, section_text, ctx.step_index
    )


use_step_matcher("parse")  # set this back to cucu's default matcher parser

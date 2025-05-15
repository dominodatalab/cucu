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
    This step is a no-op but provides structure in the HTML report
    and database (when database functionality is enabled).
    """
    # Store the heading level (1-4) based on number of # characters
    ctx.section_level = len(heading_level)
    ctx.section_text = section_text

    # Additional metadata can be stored here when database functionality is implemented
    # This would include parent-child relationships between sections
    pass


use_step_matcher("parse")  # set this back to cucu's default matcher parser

import logging

from behave.api.step_matchers import use_step_matcher

from cucu import step

use_step_matcher("re")  # use regex to match section heading patterns


@step("(#{1,4})\\s*(.*)")
def section_step(ctx, section_level, section_text):
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
    step = ctx.current_step
    step.section_level = len(section_level)
    step.parent_seq = 0

    while len(ctx.section_step_stack):
        latest_section = ctx.section_step_stack[-1]
        if latest_section.section_level < step.section_level:
            step.parent_seq = latest_section.seq
            break
        ctx.section_step_stack.pop()
        logging.debug(
            f"Section: exited '{latest_section.name}' (level {latest_section.section_level})"
        )

    ctx.section_step_stack.append(ctx.current_step)
    logging.debug(
        f"Section: entering '{step.name}' (level {step.section_level})"
    )


use_step_matcher("parse")  # set this back to cucu's default matcher parser

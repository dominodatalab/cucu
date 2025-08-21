"""
various cucu utilities can be placed here and then exposed publicly through
the src/cucu/__init__.py
"""

import hashlib
import logging
import os
import pkgutil
import shutil
import time

import humanize
from selenium.webdriver.common.by import By
from tabulate import DataRow, TableFormat, tabulate
from tenacity import (
    after_log,
    before_log,
    before_sleep_log,
    retry_if_not_exception_type,
    stop_after_delay,
    wait_fixed,
)
from tenacity import retry as retrying

from cucu import logger
from cucu.browser.core import Browser
from cucu.config import CONFIG

GHERKIN_TABLEFORMAT = TableFormat(
    lineabove=None,
    linebelowheader=None,
    linebetweenrows=None,
    linebelow=None,
    headerrow=DataRow("|", "|", "|"),
    datarow=DataRow("|", "|", "|"),
    padding=1,
    with_header_hide=["lineabove"],
)


class StopRetryException(Exception):
    pass


def generate_short_id(seed=None, length=7):
    """
    Generate a short character ID based on seed (defaults to current performance counter).
    """
    if seed is None:
        seed = time.perf_counter()

    return hashlib.sha256(str(seed).encode("utf-8")).hexdigest()[:length]


def format_gherkin_table(table, headings=[], prefix=""):
    formatted = tabulate(table, headings, tablefmt=GHERKIN_TABLEFORMAT)
    if prefix == "":
        return formatted

    return prefix + formatted.replace("\n", f"\n{prefix}")


#
# code below adapted from:
# https://github.com/behave/behave/blob/994dbfe30e2a372182ea613333e06f069ab97d4b/behave/runner.py#L385
# so we can have the sub steps printed in the console logs
#
def run_steps(ctx, steps_text):
    """
    run sub steps within an existing step definition but also log their output
    so that its easy to see what is happening.
    """

    # -- PREPARE: Save original ctx data for current step.
    # Needed if step definition that called this method uses .table/.text
    original_table = getattr(ctx, "table", None)
    original_text = getattr(ctx, "text", None)

    # first time a given step calls substeps we want to move the step_index
    # so it starts the followings steps the right point.
    if not ctx.current_step.has_substeps:
        ctx.step_index += 1

    ctx.current_step.has_substeps = True

    ctx.feature.parser.variant = "steps"
    steps = ctx.feature.parser.parse_steps(steps_text)

    current_step = ctx.current_step
    current_step_start_at = current_step.start_at

    # XXX: I want to get back to this and find a slightly better way to handle
    #      these substeps without mucking around with so much state in behave
    #      but for now this works correctly and existing tests work as expected.
    try:
        with ctx._use_with_behave_mode():
            for step in steps:
                for formatter in ctx._runner.formatters:
                    step.is_substep = True
                    formatter.insert_step(step, index=ctx.step_index)

                passed = step.run(ctx._runner, quiet=False, capture=False)

                if not passed:
                    if "StopRetryException" in step.error_message:
                        raise StopRetryException(step.error_message)
                    else:
                        raise RuntimeError(step.error_message)

            # -- FINALLY: Restore original ctx data for current step.
            ctx.table = original_table
            ctx.text = original_text
    finally:
        ctx.current_step = current_step
        ctx.current_step.start_at = current_step_start_at

    return True


def retry(func, wait_up_to_s=None, retry_after_s=None):
    """
    utility retry function that can retry the provided `func` for the maximum
    amount of seconds specified by `wait_up_to_s` and wait the number of seconds
    specified in `retry_after_s`
    """
    if wait_up_to_s is None:
        wait_up_to_s = float(CONFIG["CUCU_STEP_WAIT_TIMEOUT_S"])

    if retry_after_s is None:
        retry_after_s = float(CONFIG["CUCU_STEP_RETRY_AFTER_S"])

    @retrying(
        stop=stop_after_delay(wait_up_to_s),
        wait=wait_fixed(retry_after_s),
        retry=retry_if_not_exception_type(StopRetryException),
        before=before_log(logger, logging.DEBUG),
        after=after_log(logger, logging.DEBUG),
        before_sleep=before_sleep_log(logger, logging.DEBUG),
    )
    def new_decorator(*args, **kwargs):
        ctx = CONFIG["__CUCU_CTX"]

        for hook in CONFIG["__CUCU_BEFORE_RETRY_HOOKS"]:
            hook(ctx)

        return func(*args, **kwargs)

    return new_decorator


def load_jquery_lib():
    """
    load jquery library
    """
    jquery_lib = pkgutil.get_data(
        "cucu", "external/jquery/jquery-3.5.1.min.js"
    )
    return jquery_lib.decode("utf8")


def text_in_current_frame(browser: Browser) -> str:
    """
    Utility to get all the visible text of the current frame.

    Args:
        browser (Browser): the browser session switched to the desired frame
    """
    script = "return window.jqCucu && jqCucu.fn.jquery;"
    jquery_version = browser.execute(script)
    if not jquery_version:
        browser.execute(load_jquery_lib())
        browser.execute("window.jqCucu = jQuery.noConflict(true);")
    text = browser.execute(
        'return jqCucu("body").children(":visible").text();'
    )
    return text


def ellipsize_filename(raw_filename):
    max_filename = 100
    new_raw_filename = normalize_filename(raw_filename)
    if len(new_raw_filename) < max_filename:
        return new_raw_filename

    ellipsis = "..."
    # save the last chars, as the ending is often important
    end_count = 40
    front_count = max_filename - (len(ellipsis) + end_count)
    ellipsized_filename = (
        new_raw_filename[:front_count]
        + ellipsis
        + new_raw_filename[-1 * end_count :]
    )
    return ellipsized_filename


def normalize_filename(raw_filename):
    normalized_filename = (
        raw_filename.replace('"', "")
        .replace("{", "")
        .replace("}", "")
        .replace("#", "")
        .replace("&", "")
    )
    return normalized_filename


def get_step_image_dir(step_index, step_name):
    """
    generate .png image file name that meets these criteria:
     - hides secrets
     - escaped
     - filename does not exceed 255 chars (OS limitation)
     - uniqueness comes from step number
    """
    escaped_step_name = CONFIG.hide_secrets(step_name).replace("/", "_")
    unabridged_dirname = f"{step_index:0>4} - {escaped_step_name}"
    dirname = ellipsize_filename(unabridged_dirname)

    return dirname


def take_saw_element_screenshot(ctx, thing, name, index, element=None):
    observed = "saw" if element else "did not see"
    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    take_screenshot(
        ctx,
        ctx.current_step.name,
        label=f'{observed} {prefix}{thing} "{name}"',
        element=element,
    )


def take_screenshot(ctx, step_name, label="", element=None):
    step = ctx.current_step
    if not hasattr(step, "screenshots"):
        step.screenshots = []

    screenshot_dir = os.path.join(
        ctx.scenario_dir, get_step_image_dir(ctx.step_index, step_name)
    )
    if not os.path.exists(screenshot_dir):
        os.mkdir(screenshot_dir)

    if len(label) > 0:
        label = f" - {CONFIG.hide_secrets(label).replace('/', '_')}"
    filename = f"{CONFIG['__STEP_SCREENSHOT_COUNT']:0>4}{label}.png"
    filename = ellipsize_filename(filename)
    filepath = os.path.join(screenshot_dir, filename)

    if CONFIG["CUCU_SKIP_HIGHLIGHT_BORDER"] or not element:
        ctx.browser.screenshot(filepath)
    else:
        location = element.location
        border_width = 4
        x, y = location["x"] - border_width, location["y"] - border_width
        size = element.size
        width, height = size["width"], size["height"]

        position_css = f"position: absolute; top: {y}px; left: {x}px; width: {width}px; height: {height}px; z-index: 9001;"
        visual_css = "border-radius: 4px; border: 4px solid #ff00ff1c; background: #ff00ff05; filter: drop-shadow(magenta 0 0 10px);"

        script = f"""
            (function() {{ // double curly-brace to escape python f-string
                var body = document.querySelector('body');
                var cucu_border = document.createElement('div');
                cucu_border.setAttribute('id', 'cucu_border');
                cucu_border.setAttribute('style', '{position_css} {visual_css}');
                body.append(cucu_border);
            }})();
        """
        ctx.browser.execute(script)

        ctx.browser.screenshot(filepath)

        clear_highlight = """
            (function() {
                var body = document.querySelector('body');
                var cucu_border = document.getElementById('cucu_border');
                body.removeChild(cucu_border);
            })();
        """
        ctx.browser.execute(clear_highlight, element)

    screenshot = {
        "step_name": step_name,
        "label": label,
        "element": element,
        "location": f"({element.location['x']},{element.location['y']})"
        if element
        else "",
        "size": f"({element.size['width']},{element.size['height']})"
        if element
        else "",
        "filepath": filepath,
    }
    step.screenshots.append(screenshot)

    if CONFIG["CUCU_MONITOR_PNG"]:
        shutil.copyfile(filepath, CONFIG["CUCU_MONITOR_PNG"])

    CONFIG["__STEP_SCREENSHOT_COUNT"] += 1


def find_n_click_input_parent_label(ctx, input_element):
    """
    Clicks the nearest parent <label> of an input elemnt (if input is visually hidden or size is zero).
    """
    try:
        # Find the closest ancestor <label> element
        label = input_element.find_element(By.XPATH, "ancestor::label[1]")

        if label and label.is_displayed():
            ctx.browser.click(label)
            logger.debug("Successfully clicked the parent label.")
        else:
            logger.warning("Parent label is not displayed or not found.")

    except Exception as e:
        logger.error(
            f"Click on parent label failed (possibly missing label ancestor): {e}"
        )


def is_element_size_zero(element):
    size = element.size
    return size["width"] == 0 and size["height"] == 0


class TeeStream:
    """
    A stream that writes to both a file stream and captures content in an internal buffer.
    Provides file-like accessors to read the captured content.
    """

    def __init__(self, file_stream):
        self.file_stream = file_stream
        self.string_buffer = []

    def write(self, data):
        self.file_stream.write(data)
        self.string_buffer.append(data)

    def flush(self):
        self.file_stream.flush()

    def getvalue(self):
        return "".join(self.string_buffer)

    def read(self):
        return self.getvalue()

    def clear(self):
        """Clear the internal buffer."""
        self.string_buffer = []

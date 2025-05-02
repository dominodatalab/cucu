# Define custom before/after hooks here
# Warn: Don't import this file into other python files to avoid duplicating hook registers

import datetime

from cucu import (
    register_custom_scenario_subheader_in_report_handling,
    register_custom_tags_in_report_handling,
)
from cucu.config import CONFIG
from cucu.environment import *  # noqa

# point the `cucu lint` command to our own custom linting rules
CONFIG["CUCU_LINT_RULES_PATH"] = "features/lint_rules"


def make_scenario_id_clickable(tag):
    """Example of processing a tag to open up a link to some url"""
    scenario_id = tag.replace(r"@sid-", "")
    return f'<a href="https://localhost/index.php?/cases/view/{scenario_id}" target="_blank">{tag}</a>'


register_custom_tags_in_report_handling(r"@sid-.+", make_scenario_id_clickable)


def my_example_subheader(scenario):
    """Example of a custom subheader for the report

    This may be useful if you want to link results to your log monitor system
    """

    query_time = ""
    if (
        "steps" in scenario
        and len(scenario["steps"]) > 0
        and "result" in scenario["steps"][0]
    ):
        one_minute = datetime.timedelta(minutes=1)
        # get start time from first step iso timestamp
        start_datetime = (
            datetime.datetime.fromisoformat(
                scenario["steps"][0]["result"]["timestamp"]
            )
            - one_minute
        )
        epoc_start_time_ms = int(start_datetime.timestamp()) * 1000

        end_datetime = start_datetime + (
            one_minute * 30
        )  # default to start + 30 minutes
        for step in reversed(scenario["steps"]):
            if step.get("result", []) and step["result"].get(
                "timestamp", None
            ):
                end_duration = (
                    datetime.timedelta(
                        seconds=step["result"].get("duration", 0)
                    )
                    + one_minute
                )
                end_datetime = (
                    datetime.datetime.fromisoformat(
                        step["result"]["timestamp"]
                    )
                    + end_duration
                )
                break

        epoc_end_time_ms = int(end_datetime.timestamp()) * 1000
        query_time = f"&begin={epoc_start_time_ms}&end={epoc_end_time_ms}"

    account_id = "123456"
    result = ""
    if account_id and query_time:
        html = "<span>Log Monitoring System: "
        html += f'<a href="https://localhost/logger?account={account_id}{query_time}" target="_blank">Link 🔗</a> '
        result = html

    return result


register_custom_scenario_subheader_in_report_handling(my_example_subheader)


# TODO:
# - add a register_page_check_hook  # to ensure the page is loaded)
# - add a register_before_retry_hook  # when using the retry decorator on steps)
# - add a register_custom_tags_in_report_handling
# - add a register_custom_scenario_subheader_in_report_handling
# - add a register_custom_variable_handling

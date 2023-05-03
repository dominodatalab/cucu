# nopycln: file
import urllib
from textwrap import dedent

from cucu import register_custom_junit_failure_handler
from cucu.config import CONFIG
from cucu.environment import *


def circle_ci_direct_links_to_reports(feature, scenario):
    """
    custom failure handler that will add links from the tests Tab in CircleCI to
    link directly to our HTML Test Report
    """
    job_id = CONFIG["CIRCLE_WORKFLOW_JOB_ID"]

    if job_id is not None:
        feature_name = urllib.parse.quote(feature.name)
        scenario_name = urllib.parse.quote(scenario.name)

        return dedent(
            f"""
        See the HTML Test Report for more details(triple click the link, then copy and paste into your browser):
        https://output.circle-artifacts.com/output/job/{job_id}/artifacts/0/report/{feature_name}/{scenario_name}/index.html
        """
        )

    return ""


register_custom_junit_failure_handler(circle_ci_direct_links_to_reports)

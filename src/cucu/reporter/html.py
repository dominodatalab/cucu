import glob
import os
import random
import shutil
import sys
import traceback
import urllib
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape as escape_

import jinja2

import cucu.db as db
from cucu import format_gherkin_table, logger
from cucu.ansi_parser import parse_log_to_html
from cucu.config import CONFIG
from cucu.utils import ellipsize_filename, get_step_image_dir

HEX_DIGITS = "1234567890abcdef"


def escape(data):
    if data is None:
        return None

    return escape_(data, {'"': "&quot;"}).rstrip()


def process_tags(element):
    """
    process tags in the element provided (scenario or feature) and basically
    convert the tags to a simple @xxx representation.
    """
    prepared_tags = []

    if "tags" not in element:
        return

    for tag in element["tags"]:
        tag = f"@{tag}"

        # process custom tag handlers
        tag_handlers = CONFIG["__CUCU_HTML_REPORT_TAG_HANDLERS"].items()
        for regex, handler in tag_handlers:
            if regex.match(tag):
                tag = handler(tag)

        prepared_tags.append(tag)

    element["tags"] = " ".join(prepared_tags)


# function to left pad duration with '0' for better alphabetical sorting in html reports.
def left_pad_zeroes(elapsed_time):
    int_decimal = str(round(elapsed_time, 3)).split(".")
    int_decimal[0] = int_decimal[0].zfill(3)
    padded_duration = ".".join(int_decimal)
    return padded_duration


def generate(results, basepath, only_failures=False):
    """
    generate an HTML report for the results provided.
    """

    features = []

    db_path = os.path.join(results, "run.db")
    try:
        db.init_html_report_db(db_path)
        features = []

        db_features = db.feature.select().order_by(db.feature.start_at)
        logger.info(
            f"Starting to process {len(db_features)} features for report"
        )

        for db_feature in db_features:
            feature_results_dir = results
            if db_path := db_feature.worker.cucu_run.db_path:
                feature_results_dir = os.path.dirname(db_path)

            feature_dict = {
                "name": db_feature.name,
                "filename": db_feature.filename,
                "description": db_feature.description,
                "tags": db_feature.tags if db_feature.tags else [],
                "status": db_feature.status,
                "elements": [],
                "results_dir": feature_results_dir,
            }

            db_scenarios = (
                db.scenario.select()
                .where(db.scenario.feature_run_id == db_feature.feature_run_id)
                .order_by(db.scenario.seq)
            )

            feature_has_failures = False

            if len(db_scenarios) == 0:
                logger.debug(f"Feature {db_feature.name} has no scenarios")
                continue

            for db_scenario in db_scenarios:
                scenario_dict = {
                    "name": db_scenario.name,
                    "line": db_scenario.line_number,
                    "tags": db_scenario.tags if db_scenario.tags else [],
                    "status": db_scenario.status or "passed",
                    "steps": [],
                }

                if db_scenario.status == "failed":
                    feature_has_failures = True

                db_steps = (
                    db.step.select()
                    .where(
                        db.step.scenario_run_id == db_scenario.scenario_run_id
                    )
                    .order_by(db.step.seq)
                )

                for db_step in db_steps:
                    step_dict = {
                        "keyword": db_step.keyword,
                        "name": db_step.name,
                        "result": {
                            "status": db_step.status or "passed",
                            "duration": db_step.duration or 0,
                            "timestamp": db_step.end_at or "",
                        },
                        "substep": db_step.is_substep,
                        "screenshots": db_step.screenshots,
                    }

                    if db_step.text:
                        step_dict["text"] = db_step.text

                    if db_step.table_data:
                        step_dict["table"] = db_step.table_data

                    step_dict["result"]["error_message"] = (
                        db_step.error_message.splitlines()
                        if db_step.error_message
                        else []
                    )
                    step_dict["result"]["exception"] = db_step.exception
                    step_dict["result"]["stdout"] = db_step.stdout
                    step_dict["result"]["stderr"] = db_step.stderr
                    step_dict["result"]["browser_logs"] = (
                        db_step.browser_logs.splitlines()
                    )
                    step_dict["result"]["debug_output"] = (
                        db_step.debug_output.splitlines()
                    )

                    scenario_dict["steps"].append(step_dict)

                feature_dict["elements"].append(scenario_dict)

            if feature_has_failures:
                feature_dict["status"] = "failed"
            elif only_failures and not feature_has_failures:
                continue

            features.append(feature_dict)

    finally:
        db.close_html_report_db()

    cucu_dir = os.path.dirname(sys.modules["cucu"].__file__)
    external_dir = os.path.join(cucu_dir, "reporter", "external")
    shutil.copytree(external_dir, os.path.join(basepath, "external"))
    shutil.copyfile(
        os.path.join(cucu_dir, "reporter", "favicon.png"),
        os.path.join(basepath, "favicon.png"),
    )

    #
    # augment existing test run data with:
    #  * features & scenarios with `duration` attribute computed by adding all
    #    step durations.
    #  * add `image` attribute to a step if it has an underlying .png image.
    #
    CONFIG.snapshot()
    reported_features = []
    for feature in features:
        feature["folder_name"] = ellipsize_filename(feature["name"])
        scenarios = []

        if feature["status"] != "untested" and "elements" in feature:
            scenarios = feature["elements"]

        if only_failures and feature["status"] != "failed":
            continue

        feature_duration = 0
        total_scenarios = 0
        total_scenarios_passed = 0
        total_scenarios_failed = 0
        total_scenarios_skipped = 0
        total_scenarios_errored = 0
        feature_started_at = None

        reported_features.append(feature)
        process_tags(feature)

        if feature["status"] not in ["skipped", "untested"]:
            # copy each feature directories contents over to the report directory
            src_feature_filepath = os.path.join(
                feature["results_dir"], feature["folder_name"]
            )
            dst_feature_filepath = os.path.join(
                basepath, feature["folder_name"]
            )
            if os.path.exists(src_feature_filepath):
                shutil.copytree(
                    src_feature_filepath,
                    dst_feature_filepath,
                    dirs_exist_ok=True,
                )
            else:
                logger.warning(
                    f"Feature directory not found, skipping copy: {src_feature_filepath}"
                )

        for scenario in scenarios:
            CONFIG.restore()

            scenario["folder_name"] = ellipsize_filename(scenario["name"])
            scenario_filepath = os.path.join(
                basepath,
                feature["folder_name"],
                scenario["folder_name"],
            )

            scenario_configpath = os.path.join(
                scenario_filepath, "logs", "cucu.config.yaml.txt"
            )
            if os.path.exists(scenario_configpath):
                try:
                    CONFIG.load(scenario_configpath)
                except Exception as e:
                    logger.warning(
                        f"Could not reload config: {scenario_configpath}: {e}"
                    )
            else:
                logger.info(f"No config to reload: {scenario_configpath}")

            process_tags(scenario)

            sub_headers = []
            for handler in CONFIG[
                "__CUCU_HTML_REPORT_SCENARIO_SUBHEADER_HANDLER"
            ]:
                try:
                    sub_header = handler(scenario, feature)
                    if sub_header:
                        sub_headers.append(sub_header)
                except Exception:
                    logger.warning(
                        f'Exception while trying to run sub_headers hook for scenario: "{scenario["name"]}"\n{traceback.format_exc()}'
                    )
            scenario["sub_headers"] = "<br/>".join(sub_headers)

            scenario_duration = 0
            total_scenarios += 1
            total_steps = 0

            if "status" not in scenario:
                total_scenarios_skipped += 1
            elif scenario["status"] == "passed":
                total_scenarios_passed += 1
            elif scenario["status"] == "failed":
                total_scenarios_failed += 1
            elif scenario["status"] == "skipped":
                total_scenarios_skipped += 1
            elif scenario["status"] == "errored":
                total_scenarios_errored += 1

            step_index = 0
            scenario_started_at = None
            for step in scenario["steps"]:
                total_steps += 1

                # Handle section headings with different levels (# to ####)
                if step["name"].startswith("#"):
                    # Map the count to the appropriate HTML heading (h2-h5)
                    # We use h2-h5 instead of h1-h4 so h1 can be reserved for scenario/feature titles
                    step["heading_level"] = (
                        f"h{step['name'][:4].count('#') + 1}"
                    )

                images = []
                image_dir = get_step_image_dir(step_index, step["name"])
                image_dirpath = os.path.join(scenario_filepath, image_dir)
                for index, screenshot in enumerate(step["screenshots"]):
                    filename = os.path.split(screenshot["filepath"])[-1]
                    filepath = os.path.join(image_dirpath, filename)
                    if not os.path.exists(filepath):
                        continue
                    label = screenshot.get("label", step["name"])
                    highlight = None
                    if (
                        screenshot["location"]
                        and not CONFIG["CUCU_SKIP_HIGHLIGHT_BORDER"]
                    ):
                        window_height = screenshot["size"]["height"]
                        window_width = screenshot["size"]["width"]
                        try:
                            highlight = {
                                "height_ratio": screenshot["location"][
                                    "height"
                                ]
                                / window_height,
                                "width_ratio": screenshot["location"]["width"]
                                / window_width,
                                "top_ratio": screenshot["location"]["y"]
                                / window_height,
                                "left_ratio": screenshot["location"]["x"]
                                / window_width,
                            }
                        except TypeError:
                            # If any of the necessary properties is absent,
                            # then oh well, no highlight this time.
                            pass
                    images.append(
                        {
                            "src": urllib.parse.quote(
                                os.path.join(image_dir, filename)
                            ),
                            "index": index,
                            "label": label,
                            "id": f"step-img-{''.join(random.choices(HEX_DIGITS, k=8))}",
                            "highlight": highlight,
                        }
                    )
                step["images"] = sorted(images, key=lambda x: x["index"])

                if "result" in step:
                    if step["result"]["status"] in ["failed", "passed"]:
                        if step["result"]["timestamp"]:
                            timestamp = datetime.fromisoformat(
                                step["result"]["timestamp"]
                            )
                            step["result"]["timestamp"] = timestamp

                            if scenario_started_at is None:
                                scenario_started_at = timestamp
                                scenario["started_at"] = timestamp
                            time_offset = datetime.utcfromtimestamp(
                                (
                                    timestamp - scenario_started_at
                                ).total_seconds()
                            )
                            step["result"]["time_offset"] = time_offset
                        else:
                            step["result"]["timestamp"] = ""
                            step["result"]["time_offset"] = ""

                    scenario_duration += step["result"]["duration"]

                    if "error_message" in step["result"] and step["result"][
                        "error_message"
                    ] == [None]:
                        step["result"]["error_message"] = [""]

                if "text" in step and not isinstance(step["text"], list):
                    step["text"] = [step["text"]]

                # prepare by joining into one big chunk here since we can't do it in the Jinja template
                if "text" in step:
                    text_indent = "       "
                    step["text"] = "\n".join(
                        [text_indent + '"""']
                        + [f"{text_indent}{x}" for x in step["text"]]
                        + [text_indent + '"""']
                    )

                # prepare by joining into one big chunk here since we can't do it in the Jinja template
                if "table" in step:
                    step["table"] = format_gherkin_table(
                        step["table"]["rows"],
                        step["table"]["headings"],
                        "       ",
                    )

                step_index += 1
            logs_dir = os.path.join(scenario_filepath, "logs")

            log_files = []
            if os.path.exists(logs_dir):
                for log_file in glob.iglob(os.path.join(logs_dir, "*.*")):
                    log_filepath = log_file.removeprefix(
                        f"{scenario_filepath}/"
                    )

                    if ".console." in log_filepath and scenario_started_at:
                        log_filepath += ".html"

                    log_files.append(
                        {
                            "filepath": log_filepath,
                            "name": os.path.basename(log_file),
                        }
                    )

                scenario["logs"] = log_files

            scenario["total_steps"] = total_steps
            if scenario_started_at is None:
                scenario["started_at"] = ""
            else:
                if feature_started_at is None:
                    feature_started_at = scenario_started_at
                    feature["started_at"] = feature_started_at

                scenario["time_offset"] = datetime.utcfromtimestamp(
                    (scenario_started_at - feature_started_at).total_seconds()
                )

                for log_file in [
                    x for x in log_files if ".console." in x["name"]
                ]:
                    log_file_filepath = os.path.join(
                        scenario_filepath, "logs", log_file["name"]
                    )

                    input_file = Path(log_file_filepath)
                    output_file = Path(log_file_filepath + ".html")
                    output_file.write_text(
                        parse_log_to_html(
                            input_file.read_text(encoding="utf-8")
                        ),
                        encoding="utf-8",
                    )

            scenario["duration"] = left_pad_zeroes(scenario_duration)
            feature_duration += scenario_duration

        if feature_started_at is None:
            feature["started_at"] = ""

        feature["total_steps"] = sum([x["total_steps"] for x in scenarios])
        feature["duration"] = left_pad_zeroes(
            sum([float(x["duration"]) for x in scenarios])
        )

        feature["total_scenarios"] = total_scenarios
        feature["total_scenarios_passed"] = total_scenarios_passed
        feature["total_scenarios_failed"] = total_scenarios_failed
        feature["total_scenarios_skipped"] = total_scenarios_skipped
        feature["total_scenarios_errored"] = total_scenarios_errored

    keys = [
        "total_scenarios",
        "total_scenarios_passed",
        "total_scenarios_failed",
        "total_scenarios_skipped",
        "total_scenarios_errored",
        "total_steps",
        "duration",
    ]
    grand_totals = {"total_features": len(reported_features)}
    for k in keys:
        grand_totals[k] = sum([float(x[k]) for x in reported_features])

    package_loader = jinja2.PackageLoader("cucu.reporter", "templates")
    templates = jinja2.Environment(loader=package_loader)  # nosec

    def urlencode(string):
        """
        handles encoding specific characters in the names of features/scenarios
        so they can be used in a URL. NOTICE: we're not handling spaces since
        the browser handles those already.

        """
        return (
            string.replace('"', "%22").replace("'", "%27").replace("#", "%23")
        )

    templates.globals.update(escape=escape, urlencode=urlencode)

    index_template = templates.get_template("index.html")
    rendered_index_html = index_template.render(
        features=reported_features,
        grand_totals=grand_totals,
        title="Cucu HTML Test Report",
        basepath=basepath,
        dir_depth="",
    )

    index_output_filepath = os.path.join(basepath, "index.html")
    with open(index_output_filepath, "wb") as output:
        output.write(rendered_index_html.encode("utf8"))

    flat_template = templates.get_template("flat.html")
    rendered_flat_html = flat_template.render(
        features=reported_features,
        grand_totals=grand_totals,
        title="Flat HTML Test Report",
        basepath=basepath,
        dir_depth="",
    )

    flat_output_filepath = os.path.join(basepath, "flat.html")
    with open(flat_output_filepath, "wb") as output:
        output.write(rendered_flat_html.encode("utf8"))

    feature_template = templates.get_template("feature.html")

    for feature in reported_features:
        feature_basepath = os.path.join(basepath, feature["folder_name"])
        os.makedirs(feature_basepath, exist_ok=True)

        scenarios = []
        if feature["status"] != "untested" and "elements" in feature:
            scenarios = feature["elements"]

        rendered_feature_html = feature_template.render(
            feature=feature,
            scenarios=scenarios,
            dir_depth="",
            title=feature.get("name", "Cucu results"),
        )

        feature_output_filepath = os.path.join(
            basepath, f"{feature['name']}.html"
        )

        with open(feature_output_filepath, "wb") as output:
            output.write(rendered_feature_html.encode("utf8"))

        scenario_template = templates.get_template("scenario.html")

        for scenario in scenarios:
            steps = scenario["steps"]
            scenario_basepath = os.path.join(
                feature_basepath, scenario["folder_name"]
            )
            os.makedirs(scenario_basepath, exist_ok=True)

            scenario_output_filepath = os.path.join(
                scenario_basepath, "index.html"
            )

            rendered_scenario_html = scenario_template.render(
                basepath=results,
                feature=feature,
                path_exists=os.path.exists,
                scenario=scenario,
                steps=steps,
                title=scenario.get("name", "Cucu results"),
                dir_depth="../../",
            )

            with open(scenario_output_filepath, "wb") as output:
                output.write(rendered_scenario_html.encode("utf8"))

    return os.path.join(basepath, "flat.html")

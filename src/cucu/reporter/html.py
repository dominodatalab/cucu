import glob
import json
import os
import shutil
import sys
import traceback
import urllib
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape as escape_

import jinja2

from cucu import format_gherkin_table, logger
from cucu.ansi_parser import parse_log_to_html
from cucu.config import CONFIG
from cucu.utils import ellipsize_filename, get_step_image_dir


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

    show_status = CONFIG["CUCU_SHOW_STATUS"] == "true"

    features = []

    run_json_filepaths = list(glob.iglob(os.path.join(results, "*run.json")))
    logger.info(
        f"Starting to process {len(run_json_filepaths)} files for report"
    )

    for run_json_filepath in run_json_filepaths:
        with open(run_json_filepath, "rb") as index_input:
            try:
                features += json.loads(index_input.read())
                if show_status:
                    print("r", end="", flush=True)
            except Exception as exception:
                if show_status:
                    print("")  # add a newline before logger
                logger.warn(
                    f"unable to read file {run_json_filepath}, got error: {exception}"
                )

    # copy the external dependencies to the reports destination directory
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
        if show_status:
            print("F", end="", flush=True)
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
                results, feature["folder_name"]
            )
            dst_feature_filepath = os.path.join(
                basepath, feature["folder_name"]
            )
            shutil.copytree(
                src_feature_filepath, dst_feature_filepath, dirs_exist_ok=True
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
                    logger.warn(
                        f"Could not reload config: {scenario_configpath}: {e}"
                    )
            else:
                logger.info(f"No config to reload: {scenario_configpath}")

            if show_status:
                print("S", end="", flush=True)

            process_tags(scenario)

            sub_headers = []
            for handler in CONFIG[
                "__CUCU_HTML_REPORT_SCENARIO_SUBHEADER_HANDLER"
            ]:
                try:
                    sub_headers.append(handler(scenario))
                except Exception:
                    logger.warn(
                        f"Exception while trying to run sub_headers hook for scenario: \"{scenario['name']}\"\n{traceback.format_exc()}"
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
                if show_status:
                    print("s", end="", flush=True)
                total_steps += 1
                image_dir = get_step_image_dir(step_index, step["name"])
                image_dirpath = os.path.join(scenario_filepath, image_dir)

                if step["name"].startswith("#"):
                    step["heading_level"] = "h4"

                if os.path.exists(image_dirpath):
                    _, _, image_names = next(os.walk(image_dirpath))
                    images = []
                    for image_name in image_names:
                        words = image_name.split("-", 1)
                        index = words[0].strip()
                        try:
                            # Images with label should have a name in the form:
                            # 0000 - This is the image label.png
                            label, _ = os.path.splitext(words[1].strip())
                        except IndexError:
                            # Images with no label should instead look like:
                            # 0000.png
                            # so we default to the step name in this case.
                            label = step["name"]

                        images.append(
                            {
                                "src": urllib.parse.quote(
                                    os.path.join(image_dir, image_name)
                                ),
                                "index": index,
                                "label": label,
                            }
                        )
                    step["images"] = sorted(images, key=lambda x: x["index"])

                if "result" in step:
                    if step["result"]["status"] in ["failed", "passed"]:
                        timestamp = datetime.fromisoformat(
                            step["result"]["timestamp"]
                        )
                        step["result"]["timestamp"] = timestamp

                        if scenario_started_at is None:
                            scenario_started_at = timestamp
                            scenario["started_at"] = timestamp
                        time_offset = datetime.utcfromtimestamp(
                            (timestamp - scenario_started_at).total_seconds()
                        )
                        step["result"]["time_offset"] = time_offset

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

            if os.path.exists(logs_dir):
                log_files = []
                for log_file in glob.iglob(os.path.join(logs_dir, "*.*")):
                    if show_status:
                        print("l", end="", flush=True)
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
                    if show_status:
                        print("c", end="", flush=True)

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
        "duration",
    ]
    grand_totals = {}
    for k in keys:
        grand_totals[k] = sum([float(x[k]) for x in reported_features])

    package_loader = jinja2.PackageLoader("cucu.reporter", "templates")
    templates = jinja2.Environment(loader=package_loader)  # nosec
    if show_status:
        print("")  # add a newline to end status

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
            basepath, f'{feature["name"]}.html'
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

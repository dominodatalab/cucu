import os
import shutil
import sys
import traceback
import urllib
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape as escape_

import jinja2
from playhouse import shortcuts

import cucu.db as db
from cucu import format_gherkin_table, logger
from cucu.ansi_parser import parse_log_to_html
from cucu.config import CONFIG
from cucu.utils import (
    ellipsize_filename,
    get_step_image_dir,
)


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


def generate(results: Path, basepath: Path):
    ## Jinja2 templates setup
    def urlencode(string):
        """
        handles encoding specific characters in the names of features/scenarios
        so they can be used in a URL. NOTICE: we're not handling spaces since
        the browser handles those already.

        """
        return (
            string.replace('"', "%22").replace("'", "%27").replace("#", "%23")
        )

    def browser_timestamp_to_datetime(value):
        """Convert a browser timestamp (in milliseconds since epoch) to a datetime object."""
        try:
            timestamp_sec = int(value) / 1000.0
            return datetime.fromtimestamp(timestamp_sec).strftime(
                "%Y-%m-%d %H:%M:%S,%f"
            )[:-3]
        except (ValueError, TypeError):
            return None

    package_loader = jinja2.PackageLoader("cucu.reporter", "templates")
    templates = jinja2.Environment(loader=package_loader)  # nosec
    templates.globals.update(
        escape=escape,
        urlencode=urlencode,
        browser_timestamp_to_datetime=browser_timestamp_to_datetime,
    )
    feature_template = templates.get_template("feature.html")
    scenario_template = templates.get_template("scenario.html")

    ## prepare report directory
    cucu_dir = Path(sys.modules["cucu"].__file__).parent
    external_dir = cucu_dir / "reporter/external"
    shutil.copytree(external_dir, basepath / "external")
    shutil.copyfile(
        cucu_dir / "reporter/favicon.png",
        basepath / "favicon.png",
    )

    CONFIG.snapshot()

    db_path = results / "run.db"
    try:
        db.init_html_report_db(db_path)

        feature_count = db.feature.select().count()
        scenario_count = db.scenario.select().count()
        step_count = db.step.select().count()
        logger.info(
            f"Starting to process {feature_count} features, {scenario_count} scenarios, and {step_count} steps for report"
        )

        features = []

        db_features = db.feature.select().order_by(db.feature.start_at)

        for db_feature in db_features:
            if db_feature.status == "untested":
                logger.debug(f"Skipping untested feature: {db_feature.name}")
                continue

            feature_results_dir = results
            if db_path := db_feature.worker.cucu_run.db_path:
                logger.debug(
                    f"Combining cucu_runs, using db_path from worker: {db_path}"
                )
                feature_results_dir = os.path.dirname(db_path)

            feature_dict = {
                "name": db_feature.name,
                "filename": db_feature.filename,
                "description": db_feature.description,
                "tags": db_feature.tags if db_feature.tags else [],
                "status": db_feature.status,
                "scenarios": [],  # scenarios
                "results_dir": feature_results_dir,  # directory where feature results are stored
                "folder_name": ellipsize_filename(db_feature.name),
                "started_at": None,
                "duration": 0,
            }

            process_tags(feature_dict)

            if feature_dict["status"] not in ["skipped", "untested"]:
                # copy each feature directories contents over to the report directory
                src_feature_filepath = os.path.join(
                    feature_dict["results_dir"], feature_dict["folder_name"]
                )
                dst_feature_filepath = basepath / feature_dict["folder_name"]

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

            db_scenarios = db_feature.scenarios.select().order_by(
                db.scenario.seq
            )

            feature_has_failures = False

            if len(db_scenarios) == 0:
                logger.debug(f"Feature {db_feature.name} has no scenarios")
                continue

            feature_path = basepath / feature_dict["folder_name"]
            os.makedirs(feature_path, exist_ok=True)
            for db_scenario in db_scenarios:
                scenario_dict = {
                    "name": db_scenario.name,
                    "line": db_scenario.line_number,
                    "tags": db_scenario.tags,
                    "status": db_scenario.status,
                    "steps": [],
                    "folder_name": ellipsize_filename(db_scenario.name),
                }
                if db_scenario.status == "failed":
                    feature_has_failures = True

                db_steps = db_scenario.steps.select().order_by(db.step.seq)

                for db_step in db_steps:
                    scenario_dict["steps"].append(
                        shortcuts.model_to_dict(db_step)
                    )

                scenario_started_at, scenario_duration = process_scenario(
                    scenario_dict,
                    feature_dict["started_at"],
                    feature_path,
                    feature_dict,
                )
                feature_dict["duration"] += scenario_duration

                if feature_dict["started_at"] is None:
                    feature_dict["started_at"] = scenario_started_at

                # render scenario html
                scenario_basepath = feature_path / scenario_dict["folder_name"]
                os.makedirs(scenario_basepath, exist_ok=True)
                rendered_scenario_html = scenario_template.render(
                    basepath=results,
                    feature=feature_dict,
                    path_exists=os.path.exists,
                    scenario=scenario_dict,
                    steps=scenario_dict["steps"],
                    title=scenario_dict.get("name", "Cucu results"),
                    dir_depth="../../",
                )
                scenario_output_filepath = scenario_basepath / "index.html"
                scenario_output_filepath.write_text(rendered_scenario_html)

                # append scenario to feature
                feature_dict["scenarios"].append(scenario_dict)

            if feature_has_failures:
                feature_dict["status"] = "failed"

            # render feature html
            rendered_feature_html = feature_template.render(
                feature=feature_dict,
                scenarios=feature_dict["scenarios"],
                dir_depth="",
                title=feature_dict.get("name", "Cucu results"),
            )
            feature_output_filepath = basepath / f"{feature_dict['name']}.html"
            feature_output_filepath.write_text(rendered_feature_html)

            features.append(feature_dict)

        feature_dict["total_steps"] = sum(
            [x["total_steps"] for x in feature_dict["scenarios"]]
        )
        feature_dict["duration"] = left_pad_zeroes(
            sum([float(x["duration"]) for x in feature_dict["scenarios"]])
        )

        # query the database for stats
        feature_stats_db = db.db.execute_sql("SELECT * FROM flat_feature")
        keys = tuple([x[0] for x in feature_stats_db.description])
        feature_stats = [
            dict(zip(keys, x)) for x in feature_stats_db.fetchall()
        ]

        grand_totals_db = db.db.execute_sql("SELECT * FROM flat_all")
        keys = tuple([x[0] for x in grand_totals_db.description])
        grand_totals = dict(zip(keys, grand_totals_db.fetchone()))

    finally:
        db.close_html_report_db()

    ## Generate index.html and flat.html

    index_template = templates.get_template("index.html")
    rendered_index_html = index_template.render(
        feature_stats=feature_stats,
        grand_totals=grand_totals,
        title="Cucu HTML Test Report",
        basepath=basepath,
        dir_depth="",
    )
    html_index_path = basepath / "index.html"
    html_index_path.write_text(rendered_index_html)

    flat_template = templates.get_template("flat.html")
    rendered_flat_html = flat_template.render(
        features=features,
        grand_totals=grand_totals,
        title="Flat HTML Test Report",
        basepath=basepath,
        dir_depth="",
    )
    html_flat_path = basepath / "flat.html"
    html_flat_path.write_text(rendered_flat_html)

    return html_flat_path


def process_scenario(
    scenario_dict, feature_started_at, feature_path: Path, feature
):
    CONFIG.restore()

    scenario_dict["folder_name"] = ellipsize_filename(scenario_dict["name"])
    scenario_filepath = feature_path / scenario_dict["folder_name"]
    scenario_configpath = scenario_filepath / "logs/cucu.config.yaml.txt"

    if scenario_configpath.exists():
        try:
            CONFIG.load(scenario_configpath)
        except Exception as e:
            logger.warning(
                f"Could not reload config: {scenario_configpath}: {e}"
            )
    else:
        logger.info(f"No config to reload: {scenario_configpath}")

    process_tags(scenario_dict)

    sub_headers = []
    for handler in CONFIG["__CUCU_HTML_REPORT_SCENARIO_SUBHEADER_HANDLER"]:
        try:
            sub_header = handler(scenario_dict, feature)
            if sub_header:
                sub_headers.append(sub_header)
        except Exception:
            logger.warning(
                f'Exception while trying to run sub_headers hook for scenario: "{scenario_dict["name"]}"\n{traceback.format_exc()}'
            )
    scenario_dict["sub_headers"] = "<br/>".join(sub_headers)

    scenario_started_at = None
    scenario_duration = 0
    total_steps = len(scenario_dict["steps"])
    for step_index, step_dict in enumerate(scenario_dict["steps"]):
        # Handle section headings with different levels (# to ####)
        if step_dict["name"].startswith("#"):
            # Map the count to the appropriate HTML heading (h2-h5)
            # We use h2-h5 instead of h1-h4 so h1 can be reserved for scenario/feature titles
            step_dict["heading_level"] = (
                f"h{step_dict['name'][:4].count('#') + 1}"
            )

        image_path = Path(get_step_image_dir(step_index, step_dict["name"]))
        scenario_image_path = scenario_filepath / image_path
        for screenshot_index, screenshot in enumerate(
            step_dict["screenshots"]
        ):
            filename = os.path.split(screenshot["filepath"])[-1]
            if not os.path.exists(scenario_image_path / filename):
                continue

            screenshot["src"] = urllib.parse.quote(str(image_path / filename))
            screenshot["id"] = (
                f"step-img-{step_dict['step_run_id']}-{screenshot_index:0>4}"
            )

        if step_dict["end_at"]:
            if step_dict["status"] in ["failed", "passed"]:
                if step_dict["start_at"]:
                    timestamp = datetime.fromisoformat(step_dict["start_at"])
                    step_dict["timestamp"] = timestamp

                    if not scenario_started_at:
                        scenario_started_at = step_dict["start_at"]

                    if isinstance(scenario_started_at, str):
                        scenario_started_at = datetime.fromisoformat(
                            scenario_started_at
                        )

                    time_offset = datetime.utcfromtimestamp(
                        (timestamp - scenario_started_at).total_seconds()
                    )
                    step_dict["time_offset"] = time_offset
                else:
                    step_dict["timestamp"] = ""
                    step_dict["time_offset"] = ""

            if "error_message" in step_dict and step_dict["error_message"] == [
                None
            ]:
                step_dict["error_message"] = [""]

        if step_dict["text"] and not isinstance(step_dict["text"], list):
            step_dict["text"] = [step_dict["text"]]

        # prepare by joining into one big chunk here since we can't do it in the Jinja template
        if step_dict["text"]:
            text_indent = "       "
            step_dict["text"] = "\n".join(
                [text_indent + '"""']
                + [f"{text_indent}{x}" for x in step_dict["text"]]
                + [text_indent + '"""']
            )

        # prepare by joining into one big chunk here since we can't do it in the Jinja template
        if step_dict["table_data"]:
            step_dict["table_data"] = format_gherkin_table(
                step_dict["table_data"]["rows"],
                step_dict["table_data"]["headings"],
                "       ",
            )

        scenario_duration += step_dict["duration"]
        if scenario_started_at is None:
            scenario_started_at = step_dict["start_at"]
            scenario_dict["started_at"] = scenario_started_at

    logs_path = scenario_filepath / "logs"

    log_files = []
    for log_file in logs_path.glob("*.*"):
        log_filepath = log_file.relative_to(scenario_filepath)

        if scenario_started_at and ".console." in log_filepath.name:
            log_filepath = Path(f"logs/{log_filepath.name}.html")

        log_files.append(
            {
                "filepath": log_filepath,
                "name": os.path.basename(log_file),
            }
        )

    scenario_dict["logs"] = log_files

    scenario_dict["total_steps"] = total_steps
    if not scenario_started_at:
        scenario_dict["started_at"] = ""
    else:
        if isinstance(scenario_started_at, str):
            scenario_started_at = datetime.fromisoformat(scenario_started_at)

        if not feature_started_at:
            feature_started_at = scenario_started_at

        scenario_dict["time_offset"] = datetime.utcfromtimestamp(
            (scenario_started_at - feature_started_at).total_seconds()
        )

        for log_file in [x for x in log_files if ".console." in x["name"]]:
            input_file = scenario_filepath / "logs" / log_file["name"]
            output_file = scenario_filepath / log_file["filepath"]
            output_file.write_text(
                parse_log_to_html(input_file.read_text(encoding="utf-8")),
                encoding="utf-8",
            )

    scenario_dict["duration"] = left_pad_zeroes(scenario_duration)

    return scenario_started_at, scenario_duration

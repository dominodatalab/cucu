import re
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as escape_

import jinja2
from playhouse import shortcuts

import cucu.db as db
from cucu import format_gherkin_table, logger
from cucu.ansi_parser import parse_log_to_html
from cucu.config import CONFIG
from cucu.utils import behave_filepath_to_cucu_logpath, ellipsize_filename


def escape(data):
    if data is None:
        return None

    return escape_(data, {'"': "&quot;"}).rstrip()


def _ignore_screenshots(src, names):
    ignored = set()
    for name in names:
        path = Path(src) / name
        if name.endswith(".png"):
            ignored.add(name)
        elif path.is_dir():
            contents = list(path.iterdir())
            if contents and all(f.suffix == ".png" for f in contents):
                ignored.add(name)
    return ignored


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


def urlencode(string):
    """
    handles encoding specific characters in the names of features/scenarios
    so they can be used in a URL. NOTICE: we're not handling spaces since
    the browser handles those already.

    """
    return string.replace('"', "%22").replace("'", "%27").replace("#", "%23")


def left_pad_zeroes(elapsed_time):
    """left pad duration with '0' for better alphabetical sorting in html reports"""
    int_decimal = str(round(elapsed_time, 3)).split(".")
    int_decimal[0] = int_decimal[0].zfill(3)
    padded_duration = ".".join(int_decimal)
    return padded_duration


def browser_timestamp_to_datetime(value):
    """Convert a browser timestamp (in milliseconds since epoch) to a datetime object"""
    try:
        timestamp_sec = int(value) / 1000.0
        return datetime.fromtimestamp(timestamp_sec).strftime(
            "%Y-%m-%d %H:%M:%S,%f"
        )[:-3]
    except (ValueError, TypeError):
        return None


def step_text_list_to_html(text):
    """Convert a list of step text lines to an indented HTML heredoc format"""
    text_indent = " " * 8
    heredoc_quote = '"""'
    return "\n".join(
        [text_indent + heredoc_quote]
        + [f"{text_indent}{x}" for x in text]
        + [text_indent + heredoc_quote]
    )


def browser_log_level(raw_level):
    if raw_level in ("SEVERE", "ERROR", "CRITICAL"):
        return "error"
    return "warning" if raw_level == "WARNING" else "info"


_LOG_TS_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def log_line_offset(line, scenario_start_at):
    """Return seconds offset from scenario start for a log line that starts with a Python
    logging timestamp (``YYYY-MM-DD HH:MM:SS,mmm``), or None if no timestamp is found."""
    if not scenario_start_at or not line:
        return None
    text = _HTML_TAG_RE.sub("", line).strip()
    m = _LOG_TS_RE.match(text)
    if not m:
        return None
    try:
        ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S,%f")
        return (ts - scenario_start_at).total_seconds()
    except Exception:
        return None


def step_table_to_html(table_data):
    """Convert a step table data structure to an indented HTML table format"""
    text_indent = " " * 8
    return format_gherkin_table(
        table_data["rows"],
        table_data["headings"],
        text_indent,
    )


def generate(results: Path, basepath: Path):
    ## Jinja2 templates setup
    package_loader = jinja2.PackageLoader("cucu.reporter", "templates")
    templates = jinja2.Environment(loader=package_loader)  # nosec
    templates.globals.update(
        escape=escape,
        urlencode=urlencode,
        browser_timestamp_to_datetime=browser_timestamp_to_datetime,
        browser_log_level=browser_log_level,
        log_line_offset=log_line_offset,
        step_text_list_to_html=step_text_list_to_html,
        step_table_to_html=step_table_to_html,
    )
    feature_template = templates.get_template("feature.html")
    scenario_template = templates.get_template("scenario.html")
    scenario_replay_template = templates.get_template("scenario_replay.html")

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

        db_features = db.feature.select().order_by(db.feature.start_at)

        features = []
        for db_feature in db_features:
            if db_feature.status == "untested":
                logger.debug(f"Skipping untested feature: {db_feature.name}")
                continue

            feature_dict = shortcuts.model_to_dict(db_feature, backrefs=True)
            features.append(feature_dict)

            feature_results_dir = results
            if db_path := db_feature.worker.cucu_run.db_path:
                logger.debug(
                    f"Combining cucu_runs, using db_path from worker: {db_path}"
                )
                feature_results_dir = Path(db_path).parent

            feature_dict["results_dir"] = feature_results_dir
            feature_dict["folder_name"] = ellipsize_filename(db_feature.name)
            feature_dict["duration"] = (
                feature_dict["start_at"] - feature_dict["start_at"]
            ).total_seconds()

            process_tags(feature_dict)

            feature_path = basepath / feature_dict["folder_name"]

            if feature_dict["status"] not in ["skipped", "untested"]:
                # copy each feature directories contents over to the report directory
                src_feature_filepath = (
                    Path(feature_dict["results_dir"])
                    / feature_dict["folder_name"]
                )

                if src_feature_filepath.exists():
                    ignore = (
                        _ignore_screenshots
                        if CONFIG.true("CUCU_SCREENSHOT_VIDEO")
                        else None
                    )
                    shutil.copytree(
                        src_feature_filepath,
                        feature_path,
                        dirs_exist_ok=True,
                        ignore=ignore,
                    )
                else:
                    logger.warning(
                        f"Feature directory not found, skipping copy: {src_feature_filepath}"
                    )

            db_scenarios = db_feature.scenarios.select().order_by(
                db.scenario.seq
            )

            if len(db_scenarios) == 0:
                logger.debug(f"Feature {db_feature.name} has no scenarios")
                continue

            for scenario_dict in sorted(
                feature_dict["scenarios"], key=lambda x: x["seq"]
            ):
                CONFIG.restore()

                scenario_dict["folder_name"] = ellipsize_filename(
                    scenario_dict["name"]
                )
                scenario_filepath = feature_path / scenario_dict["folder_name"]
                scenario_configpath = (
                    scenario_filepath / "logs/cucu.config.yaml.txt"
                )
                scenario_dict["total_steps"] = len(scenario_dict["steps"])
                if scenario_dict["start_at"]:
                    offset_seconds = (
                        scenario_dict["start_at"] - feature_dict["start_at"]
                    ).total_seconds()
                    scenario_dict["time_offset"] = datetime.fromtimestamp(
                        offset_seconds, timezone.utc
                    )

                if not scenario_configpath.exists():
                    logger.info(f"No config to reload: {scenario_configpath}")
                else:
                    try:
                        CONFIG.load(scenario_configpath)
                    except Exception as e:
                        logger.warning(
                            f"Could not reload config: {scenario_configpath}: {e}"
                        )

                process_tags(scenario_dict)

                sub_headers = []
                for handler in CONFIG[
                    "__CUCU_HTML_REPORT_SCENARIO_SUBHEADER_HANDLER"
                ]:
                    try:
                        sub_header = handler(scenario_dict, feature_dict)
                        if sub_header:
                            sub_headers.append(sub_header)
                    except Exception:
                        logger.warning(
                            f'Exception while trying to run sub_headers hook for scenario: "{scenario_dict["name"]}"\n{traceback.format_exc()}'
                        )
                scenario_dict["sub_headers"] = "<br/>".join(sub_headers)
                scenario_dict["steps"] = sorted(
                    scenario_dict["steps"], key=lambda x: x["seq"]
                )

                for step_dict in scenario_dict["steps"]:
                    # section_level (root/scenario = 1, everything else is
                    # enclosing + 1) is computed at runtime in section_steps.py
                    # and utils.py's run_steps(); has_substeps distinguishes a
                    # parent step's honorary heading from a real "#" heading
                    if step_dict["section_level"] is not None:
                        level = min(step_dict["section_level"], 6)
                        heading_tag = f"h{level}"
                        if step_dict["has_substeps"]:
                            step_dict["honorary_heading_level"] = heading_tag
                        else:
                            step_dict["heading_level"] = heading_tag
                            if step_dict["is_substep"]:
                                # nested under a parent step: show the number
                                # of #'s that matches the demoted level
                                # directly, so what's on screen always
                                # matches the rendered tag
                                step_dict["heading_display_text"] = (
                                    "#" * level + step_dict["name"].lstrip("#")
                                )

                    # process timestamps and time offsets
                    if not step_dict["end_at"]:
                        continue

                    if (
                        not step_dict["start_at"]
                        or not scenario_dict["start_at"]
                    ):
                        step_dict["timestamp"] = ""
                        step_dict["time_offset"] = ""
                        continue

                    timestamp = step_dict["start_at"]
                    step_dict["timestamp"] = timestamp

                    # Clamp to >= 0: the first step can start a hair before scenario.start_at
                    # due to timing, but a negative epoch in datetime.fromtimestamp wraps to
                    # 23:59:59.999 which would push the step bar off the timeline.
                    offset_seconds = max(
                        0.0,
                        (
                            timestamp - scenario_dict["start_at"]
                        ).total_seconds(),
                    )
                    time_offset = datetime.fromtimestamp(
                        offset_seconds, timezone.utc
                    )
                    step_dict["time_offset"] = time_offset

                logs_path = scenario_filepath / "logs"

                # copy run level console log
                cucu_log_path = behave_filepath_to_cucu_logpath(
                    Path(db_feature.behave_filepath), results
                )
                if cucu_log_path.exists():
                    dest_log_path = logs_path / cucu_log_path.name.lower()
                    dest_log_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(cucu_log_path, dest_log_path)

                log_files = []
                for log_file in logs_path.glob("*.*"):
                    log_filepath = log_file.relative_to(scenario_filepath)

                    if (
                        scenario_dict["start_at"]
                        and ".console." in log_filepath.name
                    ):
                        log_filepath = Path(f"logs/{log_filepath.name}.html")

                    log_files.append(
                        {
                            "filepath": log_filepath,
                            "name": log_file.name,
                        }
                    )

                # generate html version of console log
                for log_file in [
                    x for x in log_files if ".console." in x["name"]
                ]:
                    input_file = scenario_filepath / "logs" / log_file["name"]
                    output_file = scenario_filepath / log_file["filepath"]
                    output_file.write_text(
                        parse_log_to_html(
                            input_file.read_text(encoding="utf-8")
                        ),
                        encoding="utf-8",
                    )

                scenario_dict["logs"] = log_files

                # Assign frame indices and set video path when video mode is enabled.
                screenshots_video = None
                screenshots_video_steps = None
                if CONFIG.true("CUCU_SCREENSHOT_VIDEO"):
                    screenshots_video = "screenshots.mp4"
                    # Assign cumulative frame indices to each screenshot.
                    # The encoder writes one frame per screenshot per step
                    # (or one text-card frame for steps with no screenshots),
                    # so the absolute frame index is the running count of
                    # screenshots seen across all preceding steps.
                    frame_idx = 0
                    for step_d in scenario_dict["steps"]:
                        shots = step_d.get("screenshots") or []
                        if shots:
                            for shot in shots:
                                shot["frame_index"] = frame_idx
                                frame_idx += 1
                        else:
                            frame_idx += 1  # text-card frame
                    screenshots_video_steps = frame_idx

                # render scenario html
                scenario_basepath = feature_path / scenario_dict["folder_name"]
                scenario_basepath.mkdir(parents=True, exist_ok=True)
                rendered_scenario_html = scenario_template.render(
                    basepath=results,
                    feature=feature_dict,
                    path_exists=lambda path: Path(path).exists(),
                    scenario=scenario_dict,
                    steps=scenario_dict["steps"],
                    title=scenario_dict["name"],
                    dir_depth="../../",
                    screenshots_video=screenshots_video,
                    screenshots_video_steps=screenshots_video_steps,
                )
                scenario_output_filepath = scenario_basepath / "index.html"
                scenario_output_filepath.write_text(rendered_scenario_html)

                # render replay-style scenario view

                rendered_replay_html = scenario_replay_template.render(
                    basepath=results,
                    feature=feature_dict,
                    path_exists=lambda path: Path(path).exists(),
                    scenario=scenario_dict,
                    steps=scenario_dict["steps"],
                    title=scenario_dict["name"],
                    dir_depth="../../",
                    screenshots_video=screenshots_video,
                    screenshots_video_steps=screenshots_video_steps,
                )
                scenario_replay_filepath = scenario_basepath / "replay.html"
                scenario_replay_filepath.write_text(rendered_replay_html)

            # render feature html
            rendered_feature_html = feature_template.render(
                feature=feature_dict,
                scenarios=feature_dict["scenarios"],
                dir_depth="",
                title=feature_dict["name"],
            )
            feature_output_filepath = basepath / f"{feature_dict['name']}.html"
            feature_output_filepath.write_text(rendered_feature_html)

            feature_dict["total_steps"] = sum(
                [x["total_steps"] for x in feature_dict["scenarios"]]
            )
            feature_dict["duration"] = left_pad_zeroes(
                sum(
                    [
                        float(x["duration"])
                        for x in feature_dict["scenarios"]
                        if x["duration"]
                    ]
                )
            )

        # query the database for stats
        grand_totals_db = db.db.execute_sql("SELECT * FROM flat_all")
        keys = tuple([x[0] for x in grand_totals_db.description])
        grand_totals = dict(zip(keys, grand_totals_db.fetchone()))

        ## Generate index.html

        index_template = templates.get_template("index.html")
        rendered_index_html = index_template.render(
            features=features,
            grand_totals=grand_totals,
            title="Cucu HTML Test Report",
            basepath=basepath,
            dir_depth="",
        )
        html_index_path = basepath / "index.html"
        html_index_path.write_text(rendered_index_html)

    finally:
        db.close_html_report_db()

    return html_index_path

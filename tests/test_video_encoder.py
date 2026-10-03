"""Unit tests for video encoder module."""

from unittest.mock import MagicMock, patch

import imageio.v2 as iio

from cucu.config import CONFIG
from cucu.reporter.encoder import (
    _render_text_card,
    _resolve_dimensions,
    encode_frame_specs,
    encode_videos_parallel,
    encode_workers,
    gather_scenario_frames,
)


def test_render_text_card_creates_image():
    img = _render_text_card(
        text="Test step",
        keyword="Given",
        status="passed",
        width=1366,
        height=768,
    )
    assert img is not None
    assert img.size == (1366, 768)
    assert img.mode == "RGB"


def test_render_text_card_with_multiline_text():
    img = _render_text_card(
        text="Line 1\nLine 2\nLine 3",
        keyword="When",
        status="failed",
        width=1366,
        height=768,
    )
    assert img.size == (1366, 768)


def test_render_text_card_different_statuses():
    for status in ["passed", "failed", "skipped", "untested"]:
        img = _render_text_card(
            text=f"Test {status}",
            keyword="Then",
            status=status,
            width=1280,
            height=720,
        )
        assert img.size == (1280, 720)


def test_resolve_dimensions_returns_config_defaults_when_no_screenshots():
    step = MagicMock()
    step.screenshots = []
    width, height = _resolve_dimensions([step], "/some/dir")
    assert width == 1366
    assert height == 768


def test_resolve_dimensions_returns_image_size_from_first_screenshot():
    step = MagicMock()
    step.screenshots = [{"html_src": "step_0.png"}]
    fake_img = MagicMock()
    fake_img.size = (1920, 1080)
    with (
        patch(
            "cucu.reporter.encoder._resolve_image_path",
            return_value="/some/dir/step_0.png",
        ),
        patch("cucu.reporter.encoder.Image.open", return_value=fake_img),
    ):
        width, height = _resolve_dimensions([step], "/some/dir")
    assert width == 1920
    assert height == 1080


def _fake_scenario(steps):
    scenario = MagicMock()
    scenario.steps.order_by.return_value = steps
    return scenario


def _fake_step(keyword="Given", name="a step", status="passed", shots=None):
    s = MagicMock()
    s.keyword = keyword
    s.name = name
    s.status = status
    s.text = None
    s.screenshots = shots or []
    return s


def test_gather_scenario_frames_returns_card_specs(tmp_path):
    scenario_dir = tmp_path / "feature" / "scenario"
    scenario_dir.mkdir(parents=True)
    scenario = _fake_scenario(
        [
            _fake_step(name="step one"),
            _fake_step(name="step two", status="failed"),
        ]
    )

    gathered = gather_scenario_frames(scenario, scenario_dir)

    assert gathered is not None
    frame_specs, width, height = gathered
    assert len(frame_specs) == 2
    assert frame_specs[0] == ("card", "Given step one", "Given", "passed")
    assert frame_specs[1][3] == "failed"
    assert (width, height) == (1366, 768)


def test_gather_scenario_frames_returns_image_specs(tmp_path):
    scenario_dir = tmp_path / "feature" / "scenario"
    scenario_dir.mkdir(parents=True)
    img_path = scenario_dir / "0001 - step.png"
    _render_text_card("x", "Given", "passed", 64, 64).save(img_path)
    scenario = _fake_scenario(
        [_fake_step(shots=[{"html_src": "0001 - step.png"}])]
    )

    gathered = gather_scenario_frames(scenario, scenario_dir)

    frame_specs, width, height = gathered
    assert frame_specs == [("image", str(img_path))]
    assert (width, height) == (64, 64)


def test_gather_scenario_frames_no_steps_returns_none(tmp_path):
    scenario_dir = tmp_path / "feature" / "scenario"
    scenario_dir.mkdir(parents=True)

    assert gather_scenario_frames(_fake_scenario([]), scenario_dir) is None


def test_encode_frame_specs_writes_mp4(tmp_path):
    output = tmp_path / "screenshots.mp4"
    specs = [
        ("card", "Given a step", "Given", "passed"),
        ("card", "Then another", "Then", "failed"),
    ]

    result = encode_frame_specs(specs, output, 64, 64)

    assert result == output
    assert output.exists() and output.stat().st_size > 0


def test_encode_frame_specs_exact_frame_count_and_size(tmp_path):
    # The concat list repeats the last entry so its duration counts;
    # -frames:v must trim the output back to exactly len(frame_specs).
    output = tmp_path / "screenshots.mp4"
    specs = [("card", f"Given step {i}", "Given", "passed") for i in range(3)]

    assert encode_frame_specs(specs, output, 64, 64) == output

    reader = iio.get_reader(str(output))
    try:
        assert reader.count_frames() == 3
        assert tuple(reader.get_meta_data()["size"]) == (64, 64)
    finally:
        reader.close()


def test_encode_frame_specs_scales_mismatched_image(tmp_path):
    img_path = tmp_path / "shot.png"
    _render_text_card("x", "Given", "passed", 128, 96).save(img_path)
    output = tmp_path / "screenshots.mp4"

    assert encode_frame_specs([("image", str(img_path))], output, 64, 64)

    reader = iio.get_reader(str(output))
    try:
        assert tuple(reader.get_meta_data()["size"]) == (64, 64)
    finally:
        reader.close()


def test_encode_frame_specs_path_with_single_quote(tmp_path):
    img_dir = tmp_path / "scenario with 'quotes'"
    img_dir.mkdir()
    img_path = img_dir / "0001 - shot.png"
    _render_text_card("x", "Given", "passed", 64, 64).save(img_path)
    output = tmp_path / "screenshots.mp4"

    result = encode_frame_specs([("image", str(img_path))], output, 64, 64)

    assert result == output
    assert output.stat().st_size > 0


def test_encode_videos_parallel_encodes_and_copies(tmp_path):
    jobs = []
    for i in range(3):
        src = tmp_path / f"scenario{i}" / "screenshots.mp4"
        dest = tmp_path / f"report{i}" / "screenshots.mp4"
        src.parent.mkdir()
        dest.parent.mkdir()
        specs = [("card", f"Given step {i}", "Given", "passed")]
        jobs.append((specs, 64, 64, src, dest))

    encoded = encode_videos_parallel(jobs, workers=2)

    assert encoded == 3
    for i in range(3):
        assert (tmp_path / f"scenario{i}" / "screenshots.mp4").exists()
        assert (tmp_path / f"report{i}" / "screenshots.mp4").exists()


def test_encode_videos_parallel_counts_failures(tmp_path):
    bad_spec = [("image", str(tmp_path / "missing.png"))]
    good_spec = [("card", "Given ok", "Given", "passed")]
    jobs = [
        (bad_spec, 64, 64, tmp_path / "bad.mp4", None),
        (good_spec, 64, 64, tmp_path / "good.mp4", None),
    ]

    assert encode_videos_parallel(jobs, workers=2) == 1
    assert (tmp_path / "good.mp4").exists()


def test_encode_workers_default_capped_at_six():
    CONFIG["CUCU_VIDEO_ENCODE_WORKERS"] = ""
    assert 1 <= encode_workers() <= 6


def test_encode_workers_respects_config_override():
    CONFIG["CUCU_VIDEO_ENCODE_WORKERS"] = "7"
    try:
        assert encode_workers() == 7
    finally:
        CONFIG["CUCU_VIDEO_ENCODE_WORKERS"] = ""

from pathlib import Path

from cucu.ansi_parser import parse_log_to_html


def test_parse_log():
    data_dir = Path(__file__).parent / Path("../data/unit")
    input = (data_dir / "ansi.log").read_text()
    expected = (data_dir / "ansi.log.html").read_text()

    actual = parse_log_to_html(input)
    assert actual == expected

from pathlib import Path

from cucu.ansi_parser import parse_log_to_html


def test_parse_log():
    """
    To regenerate the expected log and html:
    ```bash
    cucu run -g data/features/feature_with_failing_scenario_with_web.feature
    cp 'report/Feature with failing scenario with web/Just a scenario that opens a web page/logs/cucu.debug.console.log' data/unit/ansi.log
    cp 'report/Feature with failing scenario with web/Just a scenario that opens a web page/logs/cucu.debug.console.log.html' data/unit/ansi.log.html
    ```
    """
    data_dir = Path(__file__).parent / Path("../data/unit")
    input = (data_dir / "ansi.log").read_text()
    expected = (data_dir / "ansi.log.html").read_text()

    actual = parse_log_to_html(input)
    assert actual == expected

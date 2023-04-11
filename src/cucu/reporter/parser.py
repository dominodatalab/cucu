import html
import re

ESC_SEQ = "["
TRANSLATION = {
    ESC_SEQ + "1A": "",  # throw away "move cursor up 1"
    ESC_SEQ + "0m": "</span>",
    ESC_SEQ + "31m": '<span style="color: red;">',
    ESC_SEQ + "32m": '<span style="color: green;">',
    ESC_SEQ + "35m": '<span style="color: magenta">',
    ESC_SEQ + "90m": '<span style="color: darkgrey;">',
}
REGEX = re.compile("|".join(map(re.escape, TRANSLATION)))


def parse_log_to_html(input: str) -> str:
    """ "
    Parse an ansi color log to html
    """
    return f"<pre>\n{REGEX.sub(lambda match: TRANSLATION[match.group(0)], html.escape(input, quote=False))}\n</pre>\n"

import html
import re

from behave.formatter.ansi_escapes import colors, escapes

from cucu import logger

ESC_SEQ = "\x1b["
TRANSLATION = {v: f'<span style="color: {k};">' for k, v in colors.items()} | {
    escapes["reset"]: "</span>",
    escapes["up"]: "",  # throw away move cursor up 1
}
REGEX = re.compile("|".join(map(re.escape, TRANSLATION)))


def parse_log_to_html(input: str) -> str:
    """ "
    Parse an ansi color log to html
    """
    result = f"<pre>\n{REGEX.sub(lambda match: TRANSLATION[match.group(0)], html.escape(input, quote=False))}\n</pre>\n"
    if ESC_SEQ in result:
        lines = "\n".join([x for x in result.split("\n") if ESC_SEQ in x])
        logger.warn(f"Detected unmapped ansi escape code!:\n{lines}")

    return result

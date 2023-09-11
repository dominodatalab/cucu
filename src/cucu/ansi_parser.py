import html
import re

from behave.formatter.ansi_escapes import colors, escapes

ESC_SEQ = r"\x1b["
TRANSLATION = (
    {colors["grey"]: '<span style="color: grey;">\n'}
    | {  # grey indicates a new step, and hence add a line break
        v: f'<span style="color: {k};">'
        for k, v in colors.items()
        if k != "grey"
    }
    | {
        "\n" + escapes["reset"] + "\n": "</span>\n",
        escapes["reset"]: "</span>",
        escapes["up"] + "\n": "",  # remove a line break with cursor up
        ESC_SEQ + "46": "",  # ignore DELETE (num keypad)
        ESC_SEQ + "48": "",  # ignore INSERT (num keypad)
        ESC_SEQ + "49": "",  # ignore END (num keypad)
        ESC_SEQ + "50": "",  # ignore DOWN ARROW (num keypad)
        ESC_SEQ + "51": "",  # ignore PAGE DOWN (num keypad)
        ESC_SEQ + "52": "",  # ignore LEFT ARROW (num keypad)
        ESC_SEQ + "54": "",  # ignore RIGHT ARROW (num keypad)
        ESC_SEQ + "55": "",  # ignore HOME (num keypad)
        ESC_SEQ + "56": "",  # ignore UP ARROW (num keypad)
        ESC_SEQ + "57": "",  # ignore PAGE UP (num keypad)
    }
)
RE_TO_HTML = re.compile("|".join(map(re.escape, TRANSLATION)))

RE_TO_REMOVE = re.compile(
    r"\x1b\[(0;)?[0-9A-F]{1,2}m"
)  # detect hex values, not just decimal digits


def remove_ansi(input: str) -> str:
    return RE_TO_REMOVE.sub("", input)


def parse_log_to_html(input: str) -> str:
    """
    Parse an ansi color log to html
    """
    html_start = "<!DOCTYPE html>\n<html>\n"
    html_end = "</html>\n"
    head = '<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n</head>\n'
    body_start = '<body style="color: white; background-color: #100c08;">'  # use dark bg since colors are from behave
    body_end = "</body>\n"
    result = f"{html_start}{head}{body_start}<pre>\n{RE_TO_HTML.sub(lambda match: TRANSLATION[match.group(0)], html.escape(input, quote=False))}\n</pre>{body_end}{html_end}"
    if ESC_SEQ in result:
        lines = "\n".join([x for x in result.split("\n") if ESC_SEQ in x])

        print(
            f"Detected unmapped ansi escape code!:\n{lines}"
        )  # use print instead of logger to avoid circular import

    return result

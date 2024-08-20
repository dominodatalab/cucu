import os

import humanize

from cucu import fuzzy, logger, step
from cucu.utils import take_saw_element_screenshot


def find_file_input(ctx, name, index=0):
    """

        * <input type="file">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired button on screen
      index(str):  the index of the button if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()
    element = fuzzy.find(
        ctx.browser, name, ['input[type="file"]'], index=index
    )

    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    take_saw_element_screenshot(ctx, "file input", name, index, element)

    if element is None:
        raise RuntimeError(f'unable to find the {prefix}file input "{name}"')

    return element


@step('I upload the file "{filepath}" to the file input "{name}"')
def upload_file_to_input(ctx, filepath, name):
    _input = find_file_input(ctx, name)
    _input.send_keys(os.path.abspath(filepath))


JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width >> 1)),
          y = rect.top + (offsetY || (rect.height >> 1)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
"""


@step('I drag and drop the file "{filepath}" to "{name}"')
def drag_and_drop_file(ctx, name, filepath):
    drop_target = fuzzy.find(ctx.browser, name, ["*"])
    drop_target_html = drop_target.get_attribute("outerHTML")
    logger.debug(
        f'looked for drag & drop target "{name}" and found "{drop_target_html}"'
    )
    file_input = ctx.browser.execute(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(os.path.abspath(filepath))

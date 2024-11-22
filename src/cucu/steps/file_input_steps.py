import os

import humanize

from cucu import fuzzy, logger, retry, step
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
    var args = arguments,
    element = args[0],
    offsetX = args[1],
    offsetY = args[2],
    doc = element.ownerDocument || document;

    for (var i = 0; ; ) {
    var box = element.getBoundingClientRect(),
        clientX = box.left + (offsetX || box.width / 2),
        clientY = box.top + (offsetY || box.height / 2),
        target = doc.elementFromPoint(clientX, clientY);

    if (target && element.contains(target)) break;

    if (++i > 1) {
        var ex = new Error("Element not interactable");
        ex.code = 15;
        throw ex;
    }

    element.scrollIntoView({
        behavior: "instant",
        block: "center",
        inline: "center",
    });
    }

    var input = doc.createElement("INPUT");
    input.setAttribute("type", "file");
    input.setAttribute("multiple", "");
    input.setAttribute("style", "position:fixed;z-index:2147483647;left:0;top:0;");
    input.onchange = function (ev) {
    input.parentElement.removeChild(input);
    ev.stopPropagation();

    var dataTransfer = {
        constructor: DataTransfer,
        effectAllowed: "all",
        dropEffect: "none",
        types: ["Files"],
        files: input.files,
        setData: function setData() {},
        getData: function getData() {},
        clearData: function clearData() {},
        setDragImage: function setDragImage() {},
    };

    if (window.DataTransferItemList) {
        dataTransfer.items = Object.setPrototypeOf(
        Array.prototype.map.call(input.files, function (f) {
            return {
            constructor: DataTransferItem,
            kind: "file",
            type: f.type,
            getAsFile: function getAsFile() {
                return f;
            },
            getAsString: function getAsString(callback) {
                var reader = new FileReader();
                reader.onload = function (ev) {
                callback(ev.target.result);
                };
                reader.readAsText(f);
            },
            webkitGetAsEntry: function webkitGetAsEntry() {
                return {
                constructor: window.FileSystemEntry || window.Entry,
                name: f.name,
                fullPath: "/" + f.name,
                isFile: true,
                isDirectory: false,
                file: function file(callback) {
                    callback(f);
                },
                };
            },
            };
        }),
        {
            constructor: DataTransferItemList,
            add: function add() {},
            clear: function clear() {},
            remove: function remove() {},
        }
        );
    }

    ["dragenter", "dragover", "drop"].forEach(function (type) {
        var event = doc.createEvent("DragEvent");
        event.initMouseEvent(
        type,
        true,
        true,
        doc.defaultView,
        0,
        0,
        0,
        clientX,
        clientY,
        false,
        false,
        false,
        false,
        0,
        null
        );

        Object.setPrototypeOf(event, null);
        event.dataTransfer = dataTransfer;
        Object.setPrototypeOf(event, DragEvent.prototype);

        target.dispatchEvent(event);
    });
    };

    doc.documentElement.appendChild(input);
    input.getBoundingClientRect(); /* force reflow for Firefox */
    return input;
"""


def drag_and_drop_file(ctx, name, filepath):
    drop_target = fuzzy.find(ctx.browser, name, ["*"])
    drop_target_html = drop_target.get_attribute("outerHTML")
    logger.debug(
        f'looked for drag & drop target "{name}" and found "{drop_target_html}"'
    )
    file_input = ctx.browser.execute(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(os.path.abspath(filepath))


@step('I drag and drop the file "{filepath}" to "{name}"')
def should_drag_and_drop_file(ctx, filepath, name):
    drag_and_drop_file(ctx, name, filepath)


@step('I wait to drag and drop the file "{filepath}" to "{name}"')
def wait_to_drag_and_drop_file(ctx, filepath, name):
    retry(drag_and_drop_file)(ctx, name, filepath)

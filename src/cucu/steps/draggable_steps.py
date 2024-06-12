from selenium.webdriver.support.ui import WebDriverWait

from cucu import fuzzy, helpers, logger
from cucu.utils import take_saw_element_screenshot


def find_draggable_element(ctx, name, index=0):
    """
    find a draggable element on screen by fuzzy matching on the name provided
    and the target element:

        * <* draggable="true">

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired draggable element on screen
      index(str):  the index of the draggable element if there are duplicates
    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()
    element = fuzzy.find(
        ctx.browser, name, ['*[draggable="true"]'], index=index
    )

    take_saw_element_screenshot(ctx, "draggable", name, index, element)

    return element


def is_draggable(element):
    """
    Checks if an element is draggable.
    Args:
        element (WebElement): The element to check.
    Returns:
        bool: True if the element is draggable, False otherwise.
    """
    return element.get_attribute("draggable") == "true"


def is_not_draggable(element):
    """
    Checks if an element is not draggable.
    Args:
        element (WebElement): The element to check.
    Returns:
        bool: True if the element is not draggable, False otherwise.
    """
    return not is_draggable(element)


def find_target_element(ctx, name, index=0):
    ctx.check_browser_initialized()
    _element = fuzzy.find(ctx.browser, name, ["*"], index=index)

    return _element


JS_DRAG_AND_DROP = """
    const cucuDragAndDrop = async (dragElem, dropElem) => {

    function triggerEvent(elem, eventName, dataTransfer = null) {
        return new Promise((resolve) => {
            const eventObj = new DragEvent(eventName, {
                bubbles: true,
                cancelable: true,
                composed: true,
                dataTransfer: dataTransfer,
            });

            function listener() {
                resolve(eventObj);
                elem.removeEventListener(eventName, listener);
            }

            elem.addEventListener(eventName, listener);
            elem.dispatchEvent(eventObj);
        });
    }

    const dragstartObj = await triggerEvent(dragElem, 'dragstart', new DataTransfer());
    await triggerEvent(dropElem, 'dragenter', dragstartObj.dataTransfer);
    const dropeventObj = await triggerEvent(dropElem, 'drop', dragstartObj.dataTransfer);
    await triggerEvent(dragElem, 'dragend', dropeventObj.dataTransfer);

    window.dragAndDropCompleted = true;
    };

    cucuDragAndDrop(arguments[0], arguments[1]);
"""


def drag_element_to_element(ctx, drag_name, drop_name):
    driver = ctx.browser.driver

    driver.execute_script("window.dragAndDropCompleted = false;")

    start_drag_rect = drag_name.rect
    logger.debug(
        f"Start location of drag element {drag_name.text}: {start_drag_rect}"
    )
    logger.debug("Executing drag-and-drop via JavaScript.")

    driver.execute_script(JS_DRAG_AND_DROP, drag_name, drop_name)

    # Wait for the JavaScript flag to be set to True
    WebDriverWait(driver, 10).until(
        lambda driver: driver.execute_script(
            "return window.dragAndDropCompleted;"
        )
    )

    end_drag_rect = drag_name.rect
    logger.debug(
        f"End location of drag element {drag_name.text}: {end_drag_rect}"
    )

    if start_drag_rect == end_drag_rect:
        raise RuntimeError(
            f"Drag element {drag_name.text} position did not change"
        )
    else:
        logger.debug("Drag element position changed successfully.")

    logger.debug("Drag-and-drop operation executed.")


helpers.define_thing_with_name_in_state_steps(
    "element", "draggable", find_target_element, is_draggable
)

helpers.define_thing_with_name_in_state_steps(
    "element", "not draggable", find_target_element, is_not_draggable
)

helpers.define_thing_with_name_in_state_steps(
    "element", "draggable", find_target_element, is_draggable, with_nth=True
)

helpers.define_thing_with_name_in_state_steps(
    "element",
    "not draggable",
    find_target_element,
    is_not_draggable,
    with_nth=True,
)

helpers.define_two_thing_interaction_steps(
    "drag",
    drag_element_to_element,
    "element",
    find_draggable_element,
    "to",
    "element",
    find_target_element,
)

helpers.define_two_thing_interaction_steps(
    "drag",
    drag_element_to_element,
    "element",
    find_draggable_element,
    "to",
    "element",
    find_target_element,
    with_nth=True,
)

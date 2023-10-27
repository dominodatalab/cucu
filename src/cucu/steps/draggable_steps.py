import humanize
from selenium.webdriver.support.ui import WebDriverWait

from cucu import fuzzy, helpers, logger


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
    _element = fuzzy.find(
        ctx.browser, name, ['*[draggable="true"]'], index=index
    )

    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    if _element is None:
        raise RuntimeError(
            f"Could not find {prefix}element {name} or it is not draggable"
        )

    return _element


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

    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    if _element is None:
        raise RuntimeError(f"Could not find {prefix}element {name}")

    return _element


JS_DRAG_AND_DROP = """
var dragElem = arguments[0];
var dropElem = arguments[1];
var completed = false;

console.log("JavaScript drag-and-drop sequence initiated.");

// Create and dispatch 'dragstart' event on dragElem
var dragStartEvent = new DragEvent('dragstart', {
  bubbles: true,
  cancelable: true,
  composed: true,
  dataTransfer: new DataTransfer(),
});
console.log("Dispatching dragstart event");
dragElem.dispatchEvent(dragStartEvent);

setTimeout(() => {
  // Create and dispatch 'dragenter' event on dropElem
  var dragEnterEvent = new DragEvent('dragenter', {
    bubbles: true,
    cancelable: true,
    composed: true,
    dataTransfer: dragStartEvent.dataTransfer,
  });
  console.log("Dispatching dragenter event");
  dropElem.dispatchEvent(dragEnterEvent);

  setTimeout(() => {
    // Create and dispatch 'drop' event on dropElem
    var dropEvent = new DragEvent('drop', {
      bubbles: true,
      cancelable: true,
      composed: true,
      dataTransfer: dragStartEvent.dataTransfer,
    });
    console.log("Dispatching drop event");
    dropElem.dispatchEvent(dropEvent);

    setTimeout(() => {
      // Create and dispatch 'dragend' event on dragElem
      var dragEndEvent = new DragEvent('dragend', {
        bubbles: true,
        cancelable: true,
        composed: true,
        dataTransfer: dropEvent.dataTransfer,
      });
      console.log("Dispatching dragend event");
      dragElem.dispatchEvent(dragEndEvent);

      console.log("JavaScript drag-and-drop sequence completed.");
      completed = true;
      window.dragAndDropCompleted = completed;

    }, 100);  // End of 'dragend' event

  }, 100);  // End of 'drop' event

}, 100);  // End of 'dragenter' event
"""


def drag_element_to_element(ctx, drag_name, drop_name):
    driver = ctx.browser.driver

    start_drag_rect = drag_name.rect
    logger.info(f"Start location of drag element: {start_drag_rect}")
    logger.debug("Executing drag-and-drop via JavaScript.")

    driver.execute_script(JS_DRAG_AND_DROP, drag_name, drop_name)

    # Wait for the JavaScript flag to be set to True
    WebDriverWait(driver, 10).until(
        lambda driver: driver.execute_script(
            "return window.dragAndDropCompleted;"
        )
    )

    end_drag_rect = drag_name.rect
    logger.info(f"End location of drag element: {end_drag_rect}")

    if start_drag_rect == end_drag_rect:
        raise RuntimeError(
            "Drag element position did not change after drag and drop operation!"
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

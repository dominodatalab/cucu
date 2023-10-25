import humanize

from cucu import fuzzy, helpers, logger, retry, step
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException



def find_draggable_element(ctx, name, index=0):
    """
        * <* draggable="true">
    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired draggable element on screen
      index(str):  the index of the draggable element if there are duplicates
    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()
    _element = fuzzy.find(ctx.browser, name, ['*[draggable="true"]'], index=index)

    prefix = "" if index == 0 else f"{humanize.ordinal(index)} "

    if _element is None:
        raise RuntimeError(f"Could not find {prefix}element {name} or it is not draggable")

    return _element


def is_draggable(element):
    """
    Checks if an element is draggable.
    Args:
        element (WebElement): The element to check.
    Returns:
        bool: True if the element is draggable, False otherwise.
    """
    return element.get_attribute('draggable') == "true"


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



def drag_element_to_element(ctx, drag_name, drop_name):

    start_drag_rect = drag_name.rect
    logger.info(f"Start location of drag element: {start_drag_rect}")

    action = ActionChains(ctx.browser.driver)
    action.click_and_hold(drag_name).move_to_element(drop_name).release(drop_name).perform()

    end_drag_rect = drag_name.rect
    logger.info(f"End location of drag element: {end_drag_rect}")

    if start_drag_rect == end_drag_rect:
        raise RuntimeError(f"Drag element position did not change after drag and drop operation!")
    else:
        logger.info(f"Drag element position changed successfully!")


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
    "element", "not draggable", find_target_element, is_not_draggable, with_nth=True
)

helpers.define_interaction_on_thing_with_name_steps(
    "element", "drag", find_draggable_element, drag_element_to_element, "to", "element", find_target_element
)

helpers.define_interaction_on_thing_with_name_steps(
    "element", "drag", find_draggable_element, drag_element_to_element, "to", "element", find_target_element, with_nth=True
)

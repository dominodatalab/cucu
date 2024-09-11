# only thing your project requires to load cucu steps
from selenium.webdriver.common.by import By

from cucu import step


@step('I should see the element with id "{id}" has a child')
def should_see_the_element_with_id_has_a_child(ctx, id):
    # this code forces the frame switching code to switch out of the wrong
    # frame when looking for elements that happen to be in the default
    # (top level) frame
    frames = ctx.browser.execute('return document.querySelectorAll("iframe");')
    if frames:
        ctx.browser.switch_to_frame(frames[-1])

    element = ctx.browser.css_find_elements(f"*[id={id}]")[0]
    element.find_elements(By.CSS_SELECTOR, "*")[0]

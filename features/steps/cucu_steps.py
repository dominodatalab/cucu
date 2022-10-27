# only thing your project requires to load cucu steps
import cucu.steps

from cucu import step
from selenium.webdriver.common.by import By


@step('I should see the element with id "{id}" has a child')
def should_see_the_element_with_id_has_a_child(ctx, id):
    ctx.check_browser_initialized()
    element = ctx.browser.css_find_elements(f"*[id={id}]")[0]
    child = element.find_elements(By.CSS_SELECTOR, "*")[0]

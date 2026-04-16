from selenium.webdriver.remote.webdriver import WebDriver

_DEEP_QUERY_FIRST_JS = """
var sel = arguments[0];
function cucuWalkFirst(n) {
    if (!n) {
        return null;
    }
    if (n.nodeType === 1 && n.matches && n.matches(sel)) {
        return n;
    }
    var ch = n.children;
    if (ch) {
        for (var i = 0; i < ch.length; i++) {
            var r = cucuWalkFirst(ch[i]);
            if (r) {
                return r;
            }
        }
    }
    if (n.nodeType === 1 && n.shadowRoot) {
        var sh = n.shadowRoot.children;
        for (var j = 0; j < sh.length; j++) {
            var r2 = cucuWalkFirst(sh[j]);
            if (r2) {
                return r2;
            }
        }
    }
    return null;
}
return cucuWalkFirst(document.documentElement);
"""

_DEEP_QUERY_ALL_JS = """
var sel = arguments[0];
var acc = [];
function cucuWalkAll(n) {
    if (!n) {
        return;
    }
    if (n.nodeType === 1 && n.matches && n.matches(sel)) {
        acc.push(n);
    }
    var ch = n.children;
    if (ch) {
        for (var i = 0; i < ch.length; i++) {
            cucuWalkAll(ch[i]);
        }
    }
    if (n.nodeType === 1 && n.shadowRoot) {
        var sh = n.shadowRoot.children;
        for (var j = 0; j < sh.length; j++) {
            cucuWalkAll(sh[j]);
        }
    }
}
cucuWalkAll(document.documentElement);
return acc;
"""


def deep_query_selector_first(driver: WebDriver, selector: str):
    """
    Return the first element matching the CSS selector in the current frame's
    document, including inside open shadow roots (depth-first preorder).

    Closed shadow roots are not visible to the page and are skipped. Match
    behavior for selectors that only exist across shadow boundaries is
    undefined; prefer simple selectors scoped to a single root when possible.

    parameters:
      driver    - Selenium WebDriver (current browsing context)
      selector  - CSS selector string
    returns:
      WebElement or None
    """
    return driver.execute_script(_DEEP_QUERY_FIRST_JS, selector)


def deep_query_selector_all(driver: WebDriver, selector: str):
    """
    Return all elements matching the selector in tree order (same traversal as
    deep_query_selector_first, but every match is collected).

    parameters:
      driver    - Selenium WebDriver (current browsing context)
      selector  - CSS selector string
    returns:
      list of WebElement (possibly empty)
    """
    found = driver.execute_script(_DEEP_QUERY_ALL_JS, selector)
    return list(found or [])

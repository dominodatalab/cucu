# ![Cucu Logo](logo.png) **CUCU** - Easy BDD web testing

End-to-end testing framework that uses [gherkin](https://cucumber.io/docs/gherkin/)
to drive various underlying tools/frameworks to create real world testing scenarios.

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/dominodatalab/cucu/tree/main.svg?style=svg&circle-token=CCIPRJ_FnyZPtQ9odT5vmGW3CmZNU_bf0cfd776a09729ca4225a2860d9b59c4dae88af)](https://dl.circleci.com/status-badge/redirect/gh/dominodatalab/cucu/tree/main)

## Why cucu?
1. Cucu avoids unnecessary abstractions (i.e. no Page Objects!) while keeping scenarios readable.
    ```gherkin
    Feature: My First Cucu Test
      We want to be sure the user get search results using the landing page

      Scenario: User can get search results
        Given I open a browser at the url "https://www.google.com/search"
         When I wait to write "google" into the input "Search"
          And I click the button "Google Search"
         Then I wait to see the text "results"
    ```
2. Designed to be run **locally** and in **CI**
3. Runs a selenium container for you OR you can bring your own browser / container
4. Does fuzzy matching to approximate actions of a real user
5. Provides many steps out of the box
6. Makes it easy to create **customized** steps
7. Enables hierarchical configuration and env var and **CLI arg overrides**
8. Comes with a linter that is **customizable**

## Supporting docs
1. [CHANGELOG.md](CHANGELOG.md) - for latest news
2. [CONTRIBUTING.md](CONTRIBUTING.md) - how we develop and test the library
3. [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
4. [CONTRIBUTORS.md](CONTRIBUTORS.md)
5. [LICENSE](LICENSE)

# Table of Contents

- [ **CUCU** - Easy BDD web testing](#-cucu---easy-bdd-web-testing)
  - [Why cucu?](#why-cucu)
  - [Supporting docs](#supporting-docs)
- [Table of Contents](#table-of-contents)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Install Walkthrough](#install-walkthrough)
- [Usage](#usage)
  - [Cucu Run](#cucu-run)
  - [Run specific browser version with docker](#run-specific-browser-version-with-docker)
- [Extending Cucu](#extending-cucu)
  - [Fuzzy matching](#fuzzy-matching)
  - [Custom steps](#custom-steps)
  - [Before / After hooks](#before--after-hooks)
  - [Custom lint rules](#custom-lint-rules)
- [More Ways To Install Cucu](#more-ways-to-install-cucu)
  - [Install From Build](#install-from-build)

# Installation
## Requirements
Cucu requires
1. python 3.9+
2. docker (to do UI testing)

## Install Walkthrough
_Get your repo setup using cucu as a test framework_

1. install and start Docker if you haven't already
2. install [cucu](https://pypi.org/project/cucu/)
   ```
   pip install cucu
   ```
3. create the folder structure and files with content:
    _Cucu uses the [behave framework](https://github.com/behave/behave) which expects the `features/steps` directories_
   - features/
      - steps/
      - `__init__.py` # enables cucu and custom steps
        ```python
        # import all of the steps from cucu
        from cucu.steps import *  # noqa: F403, F401

        # import individual sub-modules here (i.e. module names of your custom step py files)
        # Example: For file features/steps/ui/login.py
        # import steps.ui.login_steps
        ```
   - environment.py - enables before/after hooks
     ```python
     # flake8: noqa
     from cucu.environment import *

     # Define custom before/after hooks here
     ```
4. list available cucu steps
   ```bash
   cucu steps
   ```
   - if you have `brew install fzf` then you can fuzzy find steps
     ```bash
     cucu steps | fzf
     # start typing for search
     ```
5. **create your first cucu test**
   - features/my_first_test.feature
     ```gherkin
     Feature: My First Cucu Test
       We want to be sure the user get search results using the landing page

       Scenario: User can get search results
         Given I open a browser at the url "https://www.google.com/search"
          When I wait to write "google" into the input "Search"
           And I click the button "Google Search"
          Then I wait to see the text "results"
     ```
6. **run it**
   ```bash
   cucu run features/my_first_test.feature
   ```

# Usage
## Cucu Run
The command `cucu run` is used to run a given test or set of tests and in its
simplest form you can use it like so:
```bash
cucu run features/my_first_test.feature
```

That would simply run the "google search for the word google" and once it's
finished executing you can use the `cucu report` command to generate an easy
to navigate and read HTML test report which includes the steps and screenshots
from that previous test run.

*NOTE:*
By default we'll simply use the `Google Chrome` you have installed and there's
a python package that'll handle downloading chromedriver that matches your
specific local Google Chrome version.

## Run specific browser version with docker

[docker hub](https://hub.docker.com/) has easy to use docker containers for
running specific versions of chrome, edge and firefox browsers for testing that
you can spin up manually in standalone mode like so:

```bash
docker run -d -p 4444:4444 selenium/standalone-chrome:latest
```

If you are using ARM64 CPU architecture (Mac M1 or M2), you must use seleniarm
container.

```bash
docker run -d -p 4444:4444 seleniarm/standalone-chromium:latest
```

And can choose a specific version replacing the `latest` with any tag from
[here](https://hub.docker.com/r/selenium/standalone-chrome/tags). You can find
browser tags for `standalone-edge` and `standalone-firefox` the same way. Once
you run the command you will see with `docker  ps -a` that the container
is running and listening on port `4444`:

Specific tags for seleniarm:
[here](https://hub.docker.com/r/seleniarm/standalone-chromium/tags)

```bash
> docker ps -a
CONTAINER ID ... PORTS                                                NAMES
7c719f4bee29 ... 0.0.0.0:4444->4444/tcp, :::4444->4444/tcp, 5900/tcp  wizardly_haslett
```

*NOTE:* For seleniarm containers, the available browsers are chromium and firefox.
The reason for this is because Google and Microsoft have not released binaries
for their respective browsers (Chrome and Edge).

Now when running `cucu run some.feature` you can provide
`--selenium-remote-url http://localhost:4444` and this way you'll run a very
specific version of chrome on any setup you run this on.

You can also create a docker hub setup with all 3 browser nodes connected using
the utilty script at `./bin/start_selenium_hub.sh` and you can point your tests
at `http://localhost:4444` and then specify the `--browser` to be `chrome`,
`firefox` or `edge` and use that specific browser for testing.

The docker hub setup for seleniarm: `./bin/start_seleniarm_hub.sh`
*NOTE:* `edge` cannot be selected as a specific browser for testing

To ease using various custom settings you can also set most of the command line
options in a local `cucurc.yml` or in a more global place at `~/.cucurc.yml`
the same settings. For the remote url above you'd simply have the following
in your `cucurc.yml`:

```bash
CUCU_SELENIUM_REMOTE_URL: http://localhost:4444
```

Then you can simply run `cucu run path/to/some.feature` and `cucu` would load
the local `cucurc.yml` or `~/.cucurc.yml` settings and use those.

# Extending Cucu

## Fuzzy matching

`cucu` uses selenium to interact with the browser but on top of that we've
developed a fuzzy matching set of rules that allow the framework to find
elements on the page by having a label and a type of element we're searching for.

The principal is simple you want to `click the button "Foo"` so we know you want
to find a button which can be one of a few different kind of HTML elements:

  * `<a>`
  * `<button>`
  * `<input type="button">`
  * `<* role="button">`
  * etc

We also know that it has the name you provided labeling it and that can be
done using any of the following rules:

  * `<thing>name</thing>`
  * `<*>name</*><thing></thing>`
  * `<thing attribute="name"></thing>`
  * `<*>name</*>...<thing>...`

Where `thing` is any of the previously identified element types. With the above
rules we created a simple method method that uses the those rules to find a set
of elements labeled with the name you provide and type of elements you're
looking for. We currently use [swizzle](https://github.com/jquery/sizzle) as
the underlying element query language as its highly portable and has a bit
useful features than basic CSS gives us.

## Custom steps
It's easy to create custom steps, for example:
1. create a new python file in your repo `features/steps/ui/weird_button_steps.py`
    ```python
    from cucu import fuzzy, retry, step

    # make this step available for scenarios and listed in `cucu steps`
    @step('I open the wierd menu item "{menu_item}"')
    def open_jupyter_menu(ctx, menu_item):
        # using fuzzy.find
        dropdown_item = fuzzy.find(ctx.browser, menu_item, ["li a"])
        dropdown_item.click()

    # example using retry
    def click_that_weird_button(ctx):
        # using selenium's css_find_elements
        ctx.browser.css_find_elements("button[custom_thing='painful-id']")[0].click()

    @step("I wait to click this button that isn't aria compliant on my page")
    def wait_to_click_that_weird_button(ctx):
        # makes this retry with the default wait timeout
        retry(click_that_weird_button)(ctx)  # remember to call the returned function `(ctx)` at the end
    ```
2. then update the magic `features/steps/__init__.py` file (this one file only!)

   _Yeah I know that this is kind of odd, but work with me here😅_
    ```python
    # import all of the steps from cucu
    from cucu.steps import *  # noqa: F403, F401

    # import individual sub-modules here (i.e. module names of your custom step py files)
    # Example: For file features/steps/ui/login.py
    # import steps.ui.login_steps
    import steps.ui.weird_button_steps
    ```
3. profit!

## Before / After hooks

There are several hooks you can access, here's a few:
```python
register_before_retry_hook,
register_before_scenario_hook,
register_custom_junit_failure_handler,
register_custom_tags_in_report_handling,
register_custom_scenario_subheader_in_report_handling,
register_custom_variable_handling,
register_page_check_hook,
```

And here's an example:
1. add your function def to `features/environment.py`
   ```python
    import logging

    from cucu import (
        fuzzy,
        logger,
        register_page_check_hook,
        retry,
    )
    from cucu.config import CONFIG
    from cucu.environment import *

    def print_elements(elements):
        """
        given a list of selenium web elements we print their outerHTML
        representation to the logs
        """
        for element in elements:
            logger.debug(f"found element: {element.get_attribute('outerHTML')}")

    def wait_for_my_loading_indicators(browser):
       # aria-label="loading"
       def should_not_see_aria_label_equals_loading():
          # ignore the checks on the my-page page as there are these silly
          # spinners that have aria-label=loading and probably shouldn't
          if "my-page" not in browser.get_current_url():
             elements = browser.css_find_elements("[aria-label='loading'")
             if elements:
                   print_elements(elements)
                   raise RuntimeError("aria-label='loading', see above for details")

       retry(should_not_see_aria_label_equals_loading)()

       # my-attr contains "loading"
       def should_not_see_data_test_contains_loading():
          elements = browser.css_find_elements("[my-attr*='loading'")
          if elements:
             print_elements(elements)
             raise RuntimeError("my-attr*='loading', see above for details")

       retry(should_not_see_data_test_contains_loading)()

       # class contains "my-spinner"
       def should_not_see_class_contains_my_spinner():
          elements = browser.css_find_elements("[class*='my-spinner'")
          if elements:
             print_elements(elements)
             raise RuntimeError("class*='my-spinner', see above for details")

       retry(should_not_see_class_contains_my_spinner)()


    register_page_check_hook("my loading indicators", wait_for_my_loading_indicators)
   ```
2. done!

## Custom lint rules

You can easily extend the `cucu lint` linting rules by setting the variable
`CUCU_LINT_RULES_PATH` and pointing it to a directory in your features source
that has `.yaml` files that are structured like so:

```yaml
[unique_rule_identifier]:
  message: [the message to provide the end user explaining the violation]
  type: [warning|error] # I or W  will be printed when reporting the violation
  current_line:
    match: [regex]
  previous_line:
    match: [regex]
  next_line:
    match: [regex]
  fix:
    match: [regex]
    replace: [regex]
    -- or --
    delete: true
```

The `current_line`, `previous_line` and `next_line` sections are used to match
on a specific set of lines so that you can then "fix" the current line a way
specified by the `fix` block. When there is no `fix` block provided then
`cucu lint` will notify the end user it can not fix the violation.

In the `fix` section one can choose to do `match` and `replace` or to simply
`delete` the violating line.

# More Ways To Install Cucu

## Install From Build

Within the cucu directory you can run `uv build` and that will produce some
output like so:

```bash
Building source distribution...
Building wheel from source distribution...
Successfully built dist/cucu-0.207.0.tar.gz and dist/cucu-0.207.0-py3-none-any.whl
```

At this point you can install the file `dist/cucu-0.1.0.tar.gz` using
`pip install .../cucu/dist/cucu-*.tar.gz` anywhere you'd like and have the `cucu` tool ready to
run.

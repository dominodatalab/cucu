# cucu

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/cerebrotech/cucu/tree/main.svg?style=svg&circle-token=81eb2db26e4d6529e8cbb1319fe0f50a992bb50e)](https://dl.circleci.com/status-badge/redirect/gh/cerebrotech/cucu/tree/main)

End to end testing framework that uses [cucumber](https://cucumber.io/) (i.e. gherkin BDD language) to
validate a product behaves as expected.

Cucu avoids unnecessary abstractions (no Page Objects) while keeping scenarios readable.
```gherkin
Feature: My First Cucu Test
  We want to be sure the user get search results using the landing page

  Scenario: User can get search results
    Given I open a browser at the url "https://www.google.com/search"
     When I wait to write "google" into the input "Search"
      And I click the button "Google Search"
     Then I wait to see the text "results"
```

- [cucu](#cucu)
- [Requirements](#requirements)
- [Setup and Usage](#setup-and-usage)
- [Running Tests](#running-tests)
  - [Cucu Run](#cucu-run)
    - [Run specific browser version with docker](#run-specific-browser-version-with-docker)
- [Extending Cucu](#extending-cucu)
  - [Custom lint rules](#custom-lint-rules)
- [More Ways To Install Cucu](#more-ways-to-install-cucu)
  - [Install From Source](#install-from-source)
  - [Install From Build](#install-from-build)
- [Cucu Development](#cucu-development)
  - [Dev Setup](#dev-setup)
    - [Fancier Dev Setup](#fancier-dev-setup)
  - [Dev Run](#dev-run)
  - [Dev Debugging](#dev-debugging)
  - [Running Built In Tests](#running-built-in-tests)
  - [Tagging A New Release](#tagging-a-new-release)

# Requirements
Cucu requires
1. python 3.7+
2. docker (to do UI testing)

# Setup and Usage
_Get your repo setup using cucu as a test framework_

1. install and start Docker if you haven't already
2. add cucu your `requirements.txt` to get from GH by label (use current label number)
   ```
   git+ssh://git@github.com/cerebrotech/cucu@0.116.0#egg=cucu
   ```
3. install it
   ```
   pip install -r requirements.txt
   ```
4. create the folder structure and files with content: [^1] [^2]
   - features/
      - steps/
      - `__init__.py` # enables cucu and custom steps
        ```
        # import all of the steps from cucu
        from cucu.steps import *  # noqa: F403, F401

        # import individual sub-modules here (i.e. module names of py files)
        # Example: For file features/steps/ui/login.py
        # import steps.ui.login_steps
        ```
   - environment.py - enables before/after hooks
     ```
     # flake8: noqa
     from cucu.environment import *

     # Define custom before/after hooks here
     ```
5. list available cucu steps
   ```
   cucu steps
   ```
   - if you have `brew install fzf` then you can fuzzy find steps
     ```
     cucu steps | fzf
     # start typing for search
     ```
6. **create your first cucu test**
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
7. **run it**
   ```
   cucu run features/my_first_test.feature
   ```

[^1]: Cucu uses the [behave framework](https://github.com/behave/behave) which expects the `features/steps` directories

[^2]: You can write your own steps! Just remember to include them in: `features/steps/__init__.py`

# Running Tests
_Technically it should be running Scenarios (tests) or running Feature (.feature files)_
## Cucu Run
The command `cucu run` is used to run a given test or set of tests and in its
simplest form you can use it like so:
```
cucu run data/features/google_kitten_search.feature
```

That would simply run the "google search for kittens test" and once it's
finished executing you can use the `cucu report` command to generate an easy
to navigate and read HTML test report which includes the steps and screenshots
from that previous test run.

*NOTE:*
By default we'll simply use the `Google Chrome` you have installed and there's
a python package that'll handle downloading chromedriver that matches your
specific local Google Chrome version.

### Run specific browser version with docker

[docker hub](https://hub.docker.com/) has easy to use docker containers for
running specific versions of chrome, edge and firefox browsers for testing that
you can spin up manually in standalone mode like so:

```
docker run -d -p 4444:4444 selenium/standalone-chrome:latest
```

And can choose a specific version replacing the `latest` with any tag from
[here](https://hub.docker.com/r/selenium/standalone-chrome/tags). You can find
browser tags for `standalone-edge` and `standalone-firefox` the same way. Once
you run the command you will see with `docker  ps -a` that the container
is running and listening on port `4444`:

```
> docker ps -a
CONTAINER ID ... PORTS                                                NAMES
7c719f4bee29 ... 0.0.0.0:4444->4444/tcp, :::4444->4444/tcp, 5900/tcp  wizardly_haslett
```

Now when running `cucu run some.feature` you can provide
`--selenium-remote-url http://localhost:4444` and this way you'll run a very
specific version of chrome on any setup you run this on.

You can also create a docker hub setup with all 3 browser nodes connected using
the utilty script at `./bin/start_selenium_hub.sh` and you can point your tests
at `http://localhost:4444` and then specify the `--browser` to be `chrome`,
`firefox` or `edge` and use that specific browser for testing.

To ease using various custom settings you can also set most of the command line
options in a local `cucurc.yml` or in a more global place at `~/.cucurc.yml`
the same settings. For the remote url above you'd simply have the following
in your `cucurc.yml`:

```
CUCU_SELENIUM_REMOTE_URL: http://localhost:4444
```

Then you can simply run `cucu run path/to/some.feature` and `cucu` would load
the local `cucurc.yml` or `~/.cucurc.yml` settings and use those.

# Extending Cucu

## Custom lint rules

You can easily extend the `cucu lint` linting rules by setting the variable
`CUCU_LINT_RULES_PATH` and pointing it to a directory in your features source
that has `.yaml` files that are structured like so:

```
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

## Install From Source

Clone this repo locally and then proceed to install python 3.7+ as indicated
earlier. At this point you should be able to simply run `make install` at the
top level of the source tree and it should install all required dependencies.

## Install From Build

Within the cucu directory you can run `poetry build` and that will produce some
output like so:

```
Building cucu (0.1.0)
  - Building sdist
  - Built cucu-0.1.0.tar.gz
  - Building wheel
  - Built cucu-0.1.0-py3-none-any.whl
```

At this point you can install the file `dist/cucu-0.1.0.tar.gz` using
`pip install ....tar.gz` anywhere you'd like and have the `cucu` tool ready to
run.

# Cucu Development

## Dev Setup
The short list
1. install `brew` - see [brew](https://brew.sh/)
2. bash
   ```bash
   brew install fzf
   brew install pyenv
   brew install pre-commit
   pyenv install 3.7

   pip install poetry
   poetry self add poetry-dotenv-plugin

   # from top-level of cucu directory
   pre-commit install
   poetry install
   ```

### Fancier Dev Setup
1. use `pipx` to install `poetry` in a separate python virtual environment
   ```bash
   brew install pipx
   pipx install poetry
   # inject the extension into poetry's virtualenv
   pipx inject poetry poetry-dotenv-plugin
   ```
   _now the poetry app and dependencies won't be in your main python install_
2. setup poetry's directory to use the project's directory (THIS IS A GLOBAL CHANGE)
   1. exit poetry shell if you're in it
   2. delete all existing poetry virtualenv directories
      ```bash
      rm -rf ~/.cache/pypoetry
      ```
   3. change poetry's global config
      ```bash
      poetry config virtualenvs.in-project true
      ```
   4. re-install cucu's poetry
      ```bash
      poetry install
      # you should see the newly created virtualenv directory under the cucu top-level directory
      ls .venv/
      ```
   _required for VSCode debugging below_

## Dev Run
1. drop into a poetry shell environment
   ```bash
   poetry shell
   ```
2. once in the poetry shell use the `cucu` command like normal
   ```bash
   cucu
   ```
3. you can run a test and see the generated **results/** directory
   ```bash
   cucu run features/browser/links.feature
   ls results
   ```
4. and even generate an html report
   ```bash
   cucu report
   ls report/index.html
   ```

## Dev Debugging
Here's some options
1. drop into an ipdb debugger on failure using the cucu run `-i` argument
2. add a `breakpoint()` call to python code to drop into an ipdb debugger
3. configure VSCode secret sauce
   1. setup poetry's directory to use the project's directory - see [Fancier Dev Setup](#fancier-dev-setup)
   2. in VSCode **`Python: Select Interpreter`** as `./.venv/bin/python`
   3. add a launch`.vscode/launch.json` and **change the `args`**
      ```json
      {
          "version": "0.2.0",
          "configurations": [
              {
                  "name": "cucu run",
                  "type": "python",
                  "request": "launch",
                  "cwd": "${workspaceFolder}",
                  "program": "src/cucu/cli/core.py",
                  "args": ["run", "features/cli/lint.feature"]
              }
          ]
      }
      ```
   4. add a VSCode breakpoint to python code
   5. run the VSCode debugger as normal
4. pip install it in `--editable` mode to test in your own project
   ```bash
   # change to your project
   cd ~/code/boo
   # install your local cucu in editable mode
   pip install -e ~/code/cucu
   ```

## Running Built In Tests
You can run the existing `cucu` tests by simply executing `make test` and can
also check the code coverage by running `make coverage`.

## Tagging A New Release
To tag a new release of cucu, first create a branch. On your new branch you can
simply run `make release` and it'll create a commit with the updated package version.
Then, you can create a PR for the new release. When the PR is merged, *GitHub Actions* will
tag a new release and *CircleCI* will publish the release to the internal pypi (JFrog).

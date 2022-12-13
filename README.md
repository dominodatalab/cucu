# cucu

[![CircleCI](https://circleci.com/gh/cerebrotech/cucu/tree/main.svg?style=svg&circle-token=8ad8867cae9cd93ece480ab64236c08307a4df35)](https://circleci.com/gh/cerebrotech/cucu/tree/main)

End to end testing framework that uses [cucumber](https://cucumber.io/) to
validate a product behaves as expected.

# requirements

Python 3.7+ is required and recommend setting up
[pyenv](https://github.com/pyenv/pyenv).

# use cucu as a library
*or how to use cucu in your repo*

1. add cucu your `requirements.txt` to get from GH by label (use current label number)
   ```
   git+ssh://git@github.com/cerebrotech/cucu@0.65.0#egg=cucu
   ```
2. install it
   ```
   pip install -r requirements.txt
   ```

3. create the folder structure and files with content:
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
4. see cucu steps
   ```
   cucu steps
   ```
   - if you have `brew install fzf` then you can fuzzy find steps
     ```
     cucu steps | fzf
     # start typing for search
     ```
5. create your first cucu test
   - features/my_first_test.feature
     ```
     Feature: My First Cucu Test
       We want to be sure the user get search results using the landing page

       Scenario: User can get search results
         Given I open a browser at the url "https://www.google.com/search"
          When I wait to write "google" into the input "Search"
           And I click the button "Google Search"
          Then I wait to see the text "results"
     ```
6. run it
   ```
   cucu run features/my_first_test.feature
   ```

# run a test

The command `cucu run` is used to run a given test or set of tests and in its
simplest invocation you can use it like so:

```
cucu run data/features/google_kitten_search.feature
```

That would simply run the "google search for kittens test" and once it's
finished executing you can use the `cucu report` command to generate an easy
to navigate and read HTML test report which includes the steps and screenshots
from that previous test run.

To run with tags specified, run ```cucu run <test folder name> --tags=<name of tag 1> --tags=<name of tag 2> ...```
If you want to run with a testrail tag, you will need to add quotes around the tag name, e.g. ```--tags="testrail(1234)"```.

For more options, run ```cucu run --help```.

*NOTE:*
By default we'll simply use the `Google Chrome` you have installed and there's
a python package that'll handle downloading chromedriver that matches your
specific local Google Chrome version.

# run specific browser version with docker

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

# extending cucu

## custom lint rules

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

# more ways to install cucu

## from source

Clone this repo locally and then proceed to install python 3.7+ as indicated
earlier. At this point you should be able to simply run `make install` at the
top level of the source tree and it should install all required dependencies.

## from build

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

# development

* Install the `pre-commit` utility. This can be done using the command
`brew install pre-commit`. (If you don't have `brew`,
[install that, first](https://brew.sh/).
* From the top-level director of the `cucu` repository,
run `pre-commit install`.

## running built in tests

You can run the existing `cucu` tests by simply executing `make test` and can
also check the code coverage by running `make coverage`.


## tagging a new release

To tag a new release of cucu, first create a branch. On your new branch you can
simply run `make release` and it'll update the package version and create a new
git tag. Add those changes to a git commit and run
`git push origin --tags [your branch name here]` to push the new tag up to
git. Then, you can create a PR for the new release.

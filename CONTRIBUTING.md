# Contributing to Cucu
Thank you for your interest in contributing to Cucu!

## Getting started checklist
1. Read our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
2. Agree to [Developer Certificate of Origin](#developer-certificate-of-origin)
3. Glance at the [Design](#design)
4. Walk through [Cucu Development](#cucu-development)


# Developer Certificate of Origin
We want this experience to be great for both you and the project, so we use the DCO (https://developercertificate.org/) as a simple way to do this.

As a contributor you:
1. ensure that whatever you contribute respects intellectual property rights of others
2. agree to release rights for your contribution under the cucu's current LICENSE
3. sign off by adding `Signed-off-by` statement to your commit message

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

# Design
Currently `cucu` uses selenium to interact with a browser but we
aim to support running the tests through other selenium testing frameworks.

## Why Gherkin (i.e. BDD-style tests)
There are a few reasons for writing the actual tests in `gherkin` including:

 * tests are readable by anyone in the organization, since they're just plain
   English that describe interactions and validations.
 * steps within a `gherkin` test can do actions on the browser, hit an API or
   anything else you can do programatically to simulate various other testing
   needs (ie use *iptables* to limit bandwidth, use *docker/kubectl* to
   pause/stop/restart containers, etc.)
 * there's only one implementation per "step" and this makes for better reusing
   of existing test code which can be maintained in the long term.
 * clear separate of the intent from the code implementation, enforced by the framework,
   avoids spegatti code of other frameworks

## Notable libraries used
1. [behave](https://behave.readthedocs.io/en/stable/) - drives the tests
2. [tenacity](https://github.com/jd/tenacity) - used for retries
3. [selenium]() - interact with browsers
4. [chromedriver-autoinstaller]() / [geckodriver-autoinstaller]() - auto-install for running locally
5. [Jinja2]() - templates
6. [pygls]() - language server
7. [ipdb]() - debugging convience
8. [jellyfish]() / [humanize]() / [tabulate]() - easier human readablilty

TODO remove:
strip-ansi = "^0.1.1"
pebble = "^5.0.3"

# Dev Setup
The short list
1. install `poetry`
2. install a compatible python - see pyproject.toml
3. start docker - used for `cucu run`*
4. shell
   ```bash
   # install poetry plugin
   poetry self add poetry-dotenv-plugin

   # creates your poetry env
   make install

   # just making sure all the code checks work
   make check

   # from top-level of cucu directory
   pre-commit install
   ```

### Fancier Dev Setup
1. use `pipx` to install `poetry` in a separate python virtual environment
   ```bash
   brew install pipx
   pipx install poetry
   # inject the extension into the poetry pipx virtualenv
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

## Cucu Run
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

## Cucu Debugging
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

Easy as this (but runs a while)
```bash
make test
```

TODO - Coverage
```bash
make coverage
```


# Backstory
Cucu was developed as a framework primarly by Rodney Gomes through his experience over years of test automation utilizing multiple programming languages. Recognizing careers in the tech industry invlove stints at various companies we wanted to build take our toolbox with us, so Cedric Young ported this to the Open Source community. The hope of this project is to be of mutual benefit, that both you and the project get enriched by each other.

Thank you for reading this :)

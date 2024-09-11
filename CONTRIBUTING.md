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
`cucu` is a "batteries-included" approach to testing
1. Connect to local browser or docker container
2. Does fuzzy matching on DOM elements
3. Implements a large set of standard steps
4. Enables customization of steps & linter rules
5. Has enchanced HTML reports
6. Designed for both local and CI use
7. Supports Chrome, Firefox, and Edge browsers

## Why Gherkin (i.e. BDD-style tests)
There are a few reasons for writing the actual tests in `gherkin` including:

 * tests are readable by anyone in the organization, since the
   interactions and validations are described in plain English.
 * steps within a `gherkin` test can do actions on the browser, hit an API or
   anything else you can do programatically to simulate various other testing
   needs (ie use *iptables* to limit bandwidth, use *docker/kubectl* to
   pause/stop/restart containers, etc.)
 * there's only one implementation per "step," which makes for better reuse
   of existing test code and smoother long-term maintenance.
 * there's a clear separation of intent and implementation that's enforced by the framework,
   which helps avoids the spaghetti code other frameworks tend towards

## Notable libraries used
1. [behave](https://behave.readthedocs.io/en/stable/) - drives the tests
2. [tenacity](https://github.com/jd/tenacity) - used for retries
3. [selenium]() - interact with browsers
4. [chromedriver-autoinstaller]() / [geckodriver-autoinstaller]() - auto-install for running locally
5. [Jinja2]() - templates
6. [pygls]() - language server
7. [ipdb]() - debugging convience
8. [jellyfish]() / [humanize]() / [tabulate]() - easier human readablilty

# Dev Setup
The short list
1. install [uv](https://github.com/astral-sh/uv)
2. start docker - used for `cucu run`*
3. shell
   ```bash
   # creates virtual env, downloading python if needed
   make setup

   # lint the code
   make lint

   # from top-level of cucu directory
   uv run pre-commit install
   ```

## Running cucu
1. `uv run` cucu commands
   ```bash
   uv run cucu
   ```
3. you can run a test and see the generated **results/** directory
   ```bash
   uv run cucu run features/browser/links.feature
   ls results
   ```
4. and even generate an html report
   ```bash
   uv run cucu report
   ls report
   ```

## Debugging cucu
Here's some options:
1. drop into an ipdb debugger on failure using the cucu run `-i` argument
2. add a `breakpoint()` call to python code to drop into an ipdb debugger
3. configure VSCode to launch and connect in debug mode
   1. in VSCode **`Python: Select Interpreter`** as `./.venv/bin/python`
   2. add a launch`.vscode/launch.json` and **change the `args`**
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
   3. add a VSCode breakpoint to python code
   4. run the VSCode debugger as normal
4. if are developing cucu and want to test it as a framework in another project then install it in `--editable` mode
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

# Backstory
Cucu was originally developed primarly by Rodney Gomes, leveraging his
years of experience in test automation across multiple programming languages.
Getting tired of rebuilding the same framework every time he switched jobs,
it was his wish to be able to take his toolbox with him. Honoring this desire,
Cedric Young put in the work to make the framework's code open source.
The hope of this project is to be of mutual benefit, that both you and the
project be enriched by each other.

Thank you for reading this :)

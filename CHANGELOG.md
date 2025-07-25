# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project closely adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.2.7
- Add - steps - add step to save the current browser URL to a variable

## 1.2.6
- Fix - core run - allow config to be changed by environment.py import

## 1.2.5
- Add - CONFIG now can save multiple snapshots in a stack
- Add - features, scenarios and steps - add various metadata
- Add - pytest-check for mulitple asserts
- Add - steps - add browser info and screenshot info
- Add - steps - add debug log and browser log
- Add - steps - add section level, seq and parent_seq info
- Change - extract generate_short_id to utils
- Change - rename .start_timestamp => to .start_at
- Change - use pathlib for paths
- Chore - CI - fix results to not be deleted by pytest
- Chore - makefile - make fix more like make lint

## 1.2.4
- Fix - restore state after tab info
- Change - replace offset with start time in step html report
- Change - make CONFIG yaml dump more robust
- Chore - change to use uv-build packaging

## 1.2.3
- Add - additional tab information steps
- Change - retry open a browser

## 1.2.2
- Chore - make lint also run ruff format --check
- Add - tags command to list tags and affected scenario counts
- Add - click parent label of an input element when the size of the input element is zero

## 1.2.1
- Add - tab information to html report and cucu debug console log

## 1.2.0
- Add - levels 2-4 to section step
- Change - rename comment step to section step
- Add - linting for section step
- Change - min python to 3.10

## 1.1.2
- Add - `cucu init` command to setup new projects

## 1.1.1
- Chore - bump coverage lib from 7.6.12 to 7.8.0
- Chore - change CI to not use experimental COVERAGE_CORE=sysmon

## 1.1.0
- Add - now python 3.13 compatible
- Change - use stdlib pdb instead of unsupported ipdb
- Change - rename CUCU_IPDB_ON_FAILURE => to CUCU_DEBUG_ON_FAILURE
- Chore - bump selenium lib to 4.31.0

## 1.0.13
- Change - rename logger.warn to logger.warning

## 1.0.12
- Chore - add coverage badge
- Chore - add docs on dev automation
- CI - fix renovate config
- CI - change renovate to ignore python minor versions
- CI - fix for bots
- Chore - bump dep versions

## 1.0.11
- Chore - bump psutil

## 1.0.10
- Chore - change package homepage to wiki page

## 1.0.9
- Chore - update for selenium 4.28
- Chore - update CI with selenium docker images to 126

## 1.0.8
- Chore - bump pypi publishing GH action version

## 1.0.7
- Fix - stablize CI runs (increase workers, add envvar tweaks)
- Fix - parse --workers correctly
- Fix - Ctrl-C to terminate for multi-workers
- Fix - ensure testing webserver is online
- Change - use fork when not MacOS for multi-worker
- Chore - bump jellyfish to 1.1.3

## 1.0.6
- Chore - relax required versions for requests library

## 1.0.5
- Fix - Resolved issues with the drag-and-drop feature to ensure compatibility with all input options.

## 1.0.4
- Change - for retry steps, also log before and after call messages

## 1.0.3
- Add - functional test for drag and drop file functionality

## 1.0.2
- Chore - fix logo for pypi

## 1.0.1
- Chore - fix pyproject.toml authors and urls
- Change - add pre-commit to makefile

## 1.0.0
- Change to 1.0.0!
- Chore - fix GH workflow for test publish

## 0.207.0
- Chore - prep for publish - p2
- Replace poetry with uv
- Set default local python to 3.12
- Run pre-commit with uv
- Fix isort with ruff

## 0.206.0
- Chore - prep for publish
- Replace black with ruff
- Remove detect-secrets to be replaced by GH repo security
- Remove bandit to be replaced by GH CodeQL
- Cleanup makefile

## 0.205.0
- Change - increase information logged for failing before_scenario_hooks

## 0.204.0
- Chore - add gh workflows for publishing
- Chore - fix project metadata

## 0.203.0
- Chore - move repo GH org locations
- Chore - remove sonarqube

## 0.202.0
- Add - wait step to saving values from any table cells to a variable

## 0.201.0
- Change - add report path to the JUnit files when available

## 0.200.0
- Change - increase the log level of scheduling a feature file

## 0.199.0
- Chore - remove deprecated CI
- Chore - add PR template

## 0.198.0
- Chore - add sonarqube
- Chore - refactor circle config (config-drive executor, embed commands, move workflows up)
- Chore - configure renovate
- Chore - remove dependabot config (duplicates renovate)
- Chore - remove safety (duplicates sonarqube)
- Change - swap pebble for mpire, kill procs on run timeout

## 0.197.0
- Fix - before all hooks are now executed

## 0.196.0
- Fix - after scenario hook error message unintentionally replaces scenario error message

## 0.195.0
- Fix - HTML report is generated into a wrong folder
- Change - `&` is replaced in file name
- Change - shortened feature name and scenario name are recorded in JUnit

## 0.194.0
- Fix - Ignore exceptions while key in desired dynamic dropdown value

## 0.193.0
- Change - Set default value of `CUCU_SKIP_HIGHLIGHT_BORDER` to `True`

## 0.192.0
- Fix - test status should be independent of ‘mht data' and 'browser logs' download status.

## 0.191.0
- Change - shorten fienames and paths, remove quotes, '{,},#' from file names.

## 0.190.0
- Add - screenshot highlight on find functions
- Change - highlight to be separate overlay element
- Change - enable element border highlight be default
- Change - enable CUCU_MONITOR_PNG by default
- Chore - CI downgrade to python 3.11 for stability
- Chore - CI unpin remote docker executor
- Chore - bump packages
  |  | Package                                                            | From      | To       |
  |--|--------------------------------------------------------------------|-----------|----------|
  |  | [coverage](https://github.com/nedbat/coveragepy)                   | `7.4.2`   | `7.4.3`  |
  |  | [importlib-metadata](https://github.com/python/importlib_metadata) | `6.11.0`  | `7.0.1`  |
  |  | [black](https://github.com/psf/black)                              | `23.12.1` | `24.2.0` |
  |  | [pytest](https://github.com/pytest-dev/pytest)                     | `7.4.4`   | `8.0.2`  |
  |  | [ruff](https://github.com/astral-sh/ruff)                          | `0.1.15`  | `0.2.2`  |
  |  | [safety](https://github.com/pyupio/safety)                         | `2.4.0b2` | `3.0.1`  |
  |  | bandit                                                             | `1.7.5`   | `1.7.7`  |
  |  | jinja2                                                             | `3.1.2`   | `3.1.3`  |
- Chore - black format files

## 0.189.0
- Change - after-hook failures will report as 'passed' instead of 'failed/errored' to testrail and html reports

## 0.188.0
- Fix - how element size is gotten in fuzzy find

## 0.187.0
- Fix - clearing input sometimes causes the input to be not interactable

## 0.186.0
- Fix - handle mht data response that is not of type dictionary

## 0.185.0
- Change - hook failures will report as 'errored' instead of 'failed' to testrail and html reports

## 0.184.0
- Change - Added step duration to failure step

## 0.183.0
- Change - Added ability to take multiple screenshots per step

## 0.182.0
- Chore - Update docker README for ARM64 based CPU
- Chore - Add seleniarm_hub bash file

## 0.181.0
- Change - only obfuscate values in config yaml file

## 0.180.0
- Change - only obfuscate certain parts in json output

## 0.179.0
- Fix - step that expects to not see a table

## 0.178.0
- Add - error message to json and junit
- Change - print expected and found tables on fail
- Chore - bump pebble

## 0.177.0
- Fix - text regex steps mess up the fuzzy find js code
- Chore - bump dependencies
- Chore - update pip in CI pre-commit
- Chore - group dependabot updates

## 0.176.0
- Add - preliminary border injection behind feature flag

## 0.175.0
- Change - left pad duration with zeroes for better alphabetical sorting in flat.html report

## 0.174.0
- Chore - prevent secrets from being merged to main
- Chore - stabilize CI by reducing workers

## 0.173.0
- Add - functions and steps for dragging and dropping elements
- Add - add helper function for two interacting elements

## 0.172.0
- Add repository and homepage fields to solve an issue with pip/poetry failing to install this package.

## 0.171.0
- Change - shorten image filenames for OS compatibiltiy
- Add - enable install on python 3.12
- Change - CI - use python 3.12
- Change - CI - use selenium 117 images
- Change - CI - chain jobs
- Change - CI - pre-commit use smaller resource
- Change - increase runtime-timeout values

## 0.170.0
- Change - retry ElementNotInteractableException exception when clicking a dynamically generated dropdown option

## 0.169.0
- Add - step and test for waiting until a table has a certain number of rows

## 0.168.0
- Add - step and test for clicking a table column within a table row that has specified text

## 0.167.0
- Fix - fuzzy JS code injection in web page redirection

## 0.166.0
- Add - functions and steps for clicking a row in a table

## 0.165.0
- Change - update dependencies

## 0.164.0
- Change - improve colorized log html file

## 0.163.0
- Change - enable color output in cucu logs when running in parallel

## 0.162.0
- Fix - use absolute path when uploading files using drag and drop

## 0.161.0
- Change - add .txt as browser console log file suffix

## 0.160.0
- Add - drag and drop file upload step

## 0.159.0
- Change - ignore exceptions from sub_headers hook
- Security - update Certifi to remove e-Tugra root certificate
- Change - use isinstance instead of direct type compare

## 0.158.0
- Add - steps to handle dynamic dropdown
- Change - improve the robustness of selecting options in a dropdown
- Change - fuzzy find won't consider elements with either 0 width or 0 height

## 0.157.0
- Add - differentiate between cucu built-in and custom steps
## 0.156.0
- Add - option to only find web elements with the name inside in fuzzy find
- Change - when finding dropdown options when the dropdown is not a select element, only considers name inside option

## 0.155.0
- Add - timestamp tooltip to steps in html report

## 0.154.0
- Add - steps to check if the nth button is disabled

## 0.153.0
- Fix - js function fails because element text is undefined

## 0.152.0
- Change - exact text match has higher priority in fuzzy find
- Change - immediate sibling has higher priority in fuzzy find

## 0.151.0
- Fix - standardize junit.xml names to match with feature names

## 0.150.0
- Fix - standardize json and log file names to match with feature names

## 0.149.0
- Fix - run_steps re-raise StopRetryException

## 0.148.0
- Fix - step image filenames that have redacted secrets

## 0.147.0
- Change - move config reload earlier

## 0.146.0
- Add - reload saved scenario config in reporting
- Change - report shows "flat.html" link in stdout

## 0.145.0
- Fix - reporting when file names have secrets

## 0.144.0
- Fix - preserve parent security CUCU_SECRETS setting
- Change - ignore objects in hide_secrets
- Change - skip secrets in config dump

## 0.143.0
- Fix - fuzzy find detect text with padding for radio buttons

## 0.142.0
- Change - hooks to LIFO order

## 0.141.0
- Fix - runtime dependency

## 0.140.0
- Add - favicon to HTML report
- Add - save config per scenario
- Change - enable MHT web page snapshot for all chrome scenarios
- Dev - move hide_secrets into Config
- Dev - update CI to use python 3.11
- Dev - update CI to use selenium-standalone 114.0

## 0.139.0
- Change - migrate to pygls 1.x
- Change - move configs into pyproject.toml
- Change - pyproject.toml author to ddl
- Change - update packages
- Dev - build remove unneeded upload artifacts
- Dev - removed pyenv since using poetry
- Fix - makefile test command

## 0.138.0
- Change - cucu to load unique named jQuery

## 0.137.0
- Add - MHT web page snapshot
- Change - Output table indecies to stdout

## 0.136.0
- Add - more debug logs in cucu steps

## 0.135.0

Prep for packaging

### Add
- add various project files
  - CHANGELOG.md
  - CODE_OF_CONDUCT.md
  - CONTRIBUTING.md - content moved from README.md
  - CONTRIBUTORS.md
  - LICENSE
  - logo.png
- add dev tools
  - detect private keys in pre-commit
  - bandit secure patterns
  - isort linter
  - ruff linter
  - safety deps checker

### Change
- change makefile
- change tooling and pyproject.toml
  - add project classifiers

### Remove
- remove unused libs (nox, retrying, strip-ansi, flake8)
  - remove noxfile.py
- remove unused DESIGN.md

### Fix
- fix many import sorts

### Secure
- add bandit and safety
  - ignore with noseq for subprocess and html

----
# Template
## [{version}]

### Add
### Change
### Deprecate
### Remove
### Fix
### Secure

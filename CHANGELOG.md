# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project closely adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# 1.4.8
- Fix - convert html tables with rowspan and colspan to uniform rectangular logical tables
        for realiable comparison in table steps

# 1.4.7
- Change - fuzzy find matching with relevance score
- Add - config to disable feature CUCU_SKIP_FUZZY_RELEVANCE: true

##  Relevance scoring (ordering)

Case-sensitive matching. Higher scores rank first. After scoring, we
deduplicate and sort by score desc, then by original discovery order
(`pass`) asc as a tiebreaker. The `index` returned by fuzzy_find is
the Nth best-ranked element after this sort.

Area priority (highest → lowest):
  1) Immediate text content (direct TEXT_NODE children only)
  2) Attribute content with sub-weights (aria-label > id > class; others default)
  3) Full text content (includes children)

Within each area, exact match outranks substring match.

Empty text fallback: if nothing matches and the element has empty
full text, a small default score is applied so empty-but-possibly
relevant nodes are not entirely discarded.

# 1.4.6
- Add - keep selenium session alive to prevent browser timeout during long after-scenario hooks

# 1.4.5
- Change - lazy load report images (except Firefox)
- Chore - skip image check for default tests
- Chore - improve some logging
- Chore - improve some tests

# 1.4.4
- Fix - colorize debug output in html report

# 1.4.3
- Change table row count equality from 'equals' to 'exactly'

# 1.4.2
- Fix - browser logs report

# 1.4.1
- Change - always all report step logs sections
- Change - add more logging to fuzzy find
- Change - preserve newlines in browser log report

# 1.4.0
- Add - proxy options exposed to end user
CUCU_PROXY_HOST and CUCU_PROXY_PORT are added as environment varibales that will
direct the underlying browser to attach to a proxy service. This allows for
monitoring of traffic between the client and the server during tests.

For example:
Create HAR files based on captured network traffic.
Profile network activity from the website under test.
Compare requested endpoints across .feature files to forecast network traffic.
Use the exposed variables like so:
CUCU_PROXY_HOST=localhost CUCU_PROXY_PORT=9009 cucu run features/proxy_test.feature

# 1.3.33
- Add - enhance fuzzy debug logging
- Chore - refactor fuzzy.js in prep for enhanced filtering

# 1.3.32
- Fix - ensure table row matches have same number of cols
- Add - logging to successful find table

# 1.3.31
- Add - override cucu_secrets redaction using a config option

# 1.3.30
- Add - steps to validate tables' row count against an operator

## 1.3.29
- Fix - option from nth dynamic dropdown
- Fix - report correct nth number in screenshots
- Fix - dedup fuzzy find
- Fix - step for blank nth input
- Add - screenshot when saw option for dropdown
- Test - Add - test for nth dynamic dropdown

## 1.3.28
- Add - lint rule to enforce single space after Feature and Scenario keywords

## 1.3.27
- Add - step to open a new tab

## 1.3.26
- Change - Turn on "nth" steps for checking dropdown disablement

## 1.3.25
- Add - feature log to html report when available
- Add - behave_filepath to feature db

## 1.3.24
- Change - Remove logging useful only for development

## 1.3.23
- Change - scroll before click for chrome and edge
- Change - browser dimensions test to use actual window size not viewport size
- Chore - upgrade selenium py to 4.38.0
- CI - Chore - upgrade selenium standalone images to 142.0

## 1.3.22
- Chore - lib upgrades, includes pytest to 9.0.0
- Chore - fix build to include LICENSE and CHANGELOG.md
- CI - update renovate to ignore behave

## 1.3.21
- Chore - upgrade pygls to 2.0.0

## 1.3.20
- Add - emit selinium session id to cucu debug logs
- Add - step for pattern matching in file contents

## 1.3.19
- Fix - html step ordering with substeps

## 1.3.18
- Change - add browser steps to assert url matches regex
- Fix - html highlighting with html_id

## 1.3.17
- Change - refactor html generation code to rely on db only
- Fix - some db col types and add changes to support refactor
- Change - remove feature --report-only-failures and --only-failures args
- Change - rename col from scenario["line"] => to scenario["line_number"]
- Fix - doc CONTRIBUTING.md with -d option
- Add - more db views
- Chore - move highlight data to recording phase

## 1.3.16
- Fix - fix a typo inverting a condition in assert_url_is

## 1.3.15
- Change - refactor HTML report highlighting to use CSS and db

## 1.3.14
- Add --combine option to report command
- CI - change - to auto-trigger publish production

## 1.3.13
- Change - UX for combined reports - add column totals
- Change - UX scenario report - make step-logs collapsible
- Change - demote fuzzy logging level to debug
- Change - db cucu_run cols
- Fix - db worker parent id for
- Chore - db cleanup access names for orm
- Chore - use db namespace
- Chore - refactor to use pathlib.Path more

## 1.3.12
- Chore - bump versions (renovate)
- Fix - url information display in the report

## 1.3.11
- Fix - custom report subheaders
- Fix - de-dup custom sub-headers in report cmd

## 1.3.10
- Add - logging to provide more insight into what Fuzzy is doing

## 1.3.9
- Fix - re-add CONFIG["SCNEARIO_RUN_ID"]
- Fix - render skipped steps as untested
- Fix - db for untested steps
- Change - ansi_parser scrub move cursor up

## 1.3.8
- Add - step level logs to html report

## 1.3.7
- Change - use db to generate html report
- Change - rewrite db recording from hooks to formatter api
- Change - --dry-run now creates feature folder
- Change - move some data out of context since formatters don't get context
- Fix - some tests
- Fix - formatters to not overwrite is_substep
- Add - missing db fields
- Chore - update pyproject.toml format change

## 1.3.6
- Fix - get tab info before executing hooks

## 1.3.5
- Change - remove cli option show-status to simplify code
- Change - rename default arg on report command

## 1.3.4
- Fix - access step.is_substep only in after_step

## 1.3.3
- Fix - make step run id more unique

## 1.3.2
- Fix - db map workers to one to one per process

## 1.3.1
- Fix - various minor db issues

## 1.3.0
- Add - record test run to local db
  This adds db recording of test runs with the following tables:
  - cucu_run - one per `cucu run`
  - worker - including a "parent" worker"
  - feature - includes tags
  - scenario - includes tags
  - step - granular details including debug and browser logs, browser and screenshot info
- Add - peewee orm lib
- Chore - add copilot instructions

## 1.2.8
- Fix - avoid unfocus event in after_step

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

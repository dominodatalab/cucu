# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project closely adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.171.0
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

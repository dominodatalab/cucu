# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project closely adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.140.0
- Add - favicon to HTML report
- Add - save config per scenario
- Change - enable MHT web page snapshot for all chrome scenarios
- Change - move hide_secrets into Config
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

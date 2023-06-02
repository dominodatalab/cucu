# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project closely adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## 0.131.0

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

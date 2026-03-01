---
applyTo: '**'
---

# cucu Project Instructions

## What This Project Is

**cucu** is a Python BDD/Gherkin-based web testing framework built on top of [Behave](https://behave.readthedocs.io/) and Selenium. It provides a large library of pre-built step definitions for browser interaction and enables teams to write readable, plain-English UI tests. Published to PyPI.

## Definitions

- **Feature**: A group of related Scenarios. AKA a test suite.
- **Scenario**: A single test case. AKA a test.

## Commands

```bash
make setup      # Install dev dependencies (uv sync --dev)
make fix        # Auto-fix formatting and linting issues (use this instead of make lint)
make lint       # Run linters (ruff, pre-commit, cucu lint)
make ci-lint    # CI linting (skips pre-commit)
make test       # Run all tests (pytest + cucu feature tests)
make build      # Build wheel + sdist

# Run specific tests
uv run pytest tests/test_config.py                    # Single pytest unit test file
uv run cucu run features/browser/links.feature        # Single feature file
uv run cucu run features/browser/links.feature:10     # Specific scenario by line number
uv run cucu run features/ --workers 4                 # Parallel feature test run

# Other cucu commands
uv run cucu                  # Show CLI help
uv run cucu run features/ -g # Run tests and generate HTML report
uv run cucu report           # Generate HTML report from existing results
uv run cucu steps            # List all available step definitions
uv run cucu lint features/   # Lint feature files
```

Docker must be running for `cucu run` (Selenium uses it).

## Build & Validation

```bash
# Format and fix all issues in one shot (ruff format + ruff check --fix + pre-commit + cucu lint --fix)
make fix

# Run feature tests and generate HTML report
# outputs: results/run.db report/index.html
uv run cucu run -g features

# OR use a specific feature file and optional line number of the individual scenario
uv run cucu run -g features/cli/report_with_custom_failure_handler.feature:6
```

Lint steps in order: `ruff format` → `ruff check` → `pre-commit` → `cucu lint features/`.

## Architecture

### Source layout (`src/cucu/`)

- **`cli/core.py`** — All CLI commands (run, lint, steps, init, report, vars, etc.). Keep new commands here.
- **`steps/`** — 27 modules of pre-built Gherkin step definitions (buttons, inputs, tables, dropdowns, links, etc.)
- **`browser/`** — Selenium wrapper. `core.py` is the main browser class; `fuzzy/core.py` handles intelligent DOM element matching
- **`environment.py`** — Behave lifecycle hooks (before/after all, feature, scenario, step)
- **`hooks.py`** — Custom hook registration API (`register_before_scenario_hook()`, etc.)
- **`config.py`** — `CONFIG` dict — hierarchical config loaded from `cucurc.yml` → env vars → CLI args. Use for multi-location values; use `ctx` for scenario-scoped values.
- **`db.py`** — SQLite results DB using Peewee ORM. Only manage connections (`db.init()`, `db.connect()`, `db.close()`) here; other modules use ORM queries but not connections. No migrations needed (DB generated at runtime).
- **`reporter/`** — HTML report generation via Jinja2 templates
- **`lint/`** — Feature file linter with YAML rule files in `lint/rules/`
- **`language_server/core.py`** — LSP server for IDE integration (built on `pygls`)

### Test layout

- **`tests/`** — Unit tests (pytest) for CLI and utility functionality
- **`features/`** — Integration tests (cucu/Behave) for cucu's own features. `features/environment.py` sets up test hooks; `features/cucurc.yml` sets test config.
- **`data/`** — Fixtures for feature tests
- **`src/cucu/init_data/`** — Templates for `cucu init`, validated by feature tests

## Coding Standards

- Use `make fix` (not `make lint`) to fix code style
- Update `CHANGELOG.md` for each PR; bump version in `pyproject.toml` + run `uv lock` when releasing; keep the spec file updated
- Keep `__init__.py` files minimal
- Use `CONFIG` for values shared across multiple locations; use `ctx` for scenario-scoped values
- Use `pathlib` over `os.path`
- Use guard clauses to reduce nesting
- Let exceptions propagate — don't bulletproof code
- No docstrings for obvious functions; avoid obvious single-line comments
- No relative imports — always import from top of file
- Don't extract unnecessary helper functions
- Don't use `getattr(obj, "attr", default)` when you control the object
- Always check exit codes and stdout/stderr when running shell commands
- Use the default `results/` folder; don't pass `--results` in examples/tests

## Step Definition Pattern

Split steps into `find_*(ctx, name)` + `action_*(ctx, element)` helpers plus a thin `@step` wrapper. Helpers are importable by other step modules.

```python
from cucu import step
from cucu.browser import fuzzy

def find_button(ctx, name, index=0):
    return fuzzy.find(ctx.browser, name, ["button", 'input[type="button"]', '*[role="button"]'], index=index)

def click_button(ctx, button):
    ctx.browser.click(button)

@step('I click the "{name}" button')
def step_impl(ctx, name):
    click_button(ctx, find_button(ctx, name))
```

All new step files go in `src/cucu/steps/`. Each new file must be explicitly imported in `src/cucu/steps/__init__.py` — steps are not auto-discovered.

## Hook Registration Pattern

Hooks are stored as lists inside `CONFIG` — not Behave decorators, not an event emitter. Register via functions in `src/cucu/hooks.py`. Do not modify `environment.py` directly.

```python
from cucu import register_before_scenario_hook

def setup(ctx):
    ctx.my_value = "something"

register_before_scenario_hook(setup)
```

Available: `register_before_all_hook`, `register_after_all_hook`, `register_before_scenario_hook`, `register_after_scenario_hook`, `register_page_check_hook`, `register_before_retry_hook`.

## Fuzzy DOM Matching

Use `fuzzy.find` instead of direct XPath or CSS selectors. Pass multiple CSS selector alternatives; the JS library matches by visible text across all of them.

```python
from cucu.browser import fuzzy

element = fuzzy.find(
    ctx.browser,
    name,                                                         # visible text to match
    ["button", 'input[type="submit"]', '*[role="button"]'],
    index=index,                                                  # 0-based when multiple matches
)
```

Source: `src/cucu/browser/fuzzy/core.py`

## Configuration: cucurc.yml Hierarchy

Configuration is NOT a single `.env` file. Files load in order (each overrides the previous):
`~/.cucurc.yml` → cwd → feature file directory. Environment variables always win.

Add per-directory `cucurc.yml` files rather than a single root config. See `src/cucu/config.py` for all available `CONFIG.define()` variables.

## Retry Pattern for Waiting Steps

Use the `retry()` decorator instead of writing polling loops.

```python
from cucu.utils import retry
from cucu import step

@step('I wait to see the "{name}" button')
def step_impl(ctx, name):
    retry(find_button)(ctx, name)

@step('I wait up to "{seconds}" seconds to see the "{name}" button')
def step_impl_with_timeout(ctx, seconds, name):
    retry(find_button, wait_up_to_s=float(seconds))(ctx, name)
```

Source: `src/cucu/steps/flow_control_steps.py`

## Release Process

1. Bump version in `pyproject.toml` + add `CHANGELOG.md` entry + run `uv lock`
2. PR → merge to main
3. GitHub Actions auto-detects new version → creates GitHub Release → publishes to test.pypi.org
4. Manually trigger `publish-production.yml` to publish to pypi.org

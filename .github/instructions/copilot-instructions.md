---
applyTo: '**'
---

# cucu Project Instructions

**cucu** is a Python BDD/Gherkin web testing framework built on Behave + Selenium. Published to PyPI.

## Commands

```bash
make setup      # uv sync --dev
make fix        # ruff format + ruff check --fix + pre-commit + cucu lint --fix  ← use this, not make lint
make test       # pytest + cucu feature tests

uv run pytest tests/test_config.py                 # unit test
uv run cucu run features/browser/links.feature     # feature test
uv run cucu run features/browser/links.feature:10  # specific scenario by line
uv run cucu run -g features/                       # all feature tests + HTML report
uv run cucu steps                                  # list all step definitions
```

Docker must be running for `cucu run` (Selenium).

## Source Layout

`src/cucu/`:
- `cli/core.py` — all CLI commands; add new ones here only
- `steps/` — Gherkin step definitions; explicitly imported in `steps/__init__.py`
- `browser/core.py` — Selenium wrapper; `browser/fuzzy/core.py` — JS-based DOM matching
- `environment.py` — Behave lifecycle hooks; do not modify directly
- `hooks.py` — hook registration API
- `config.py` — `CONFIG` global state; hierarchical config via `cucurc.yml` + env vars
- `db.py` — SQLite/Peewee ORM; only this file calls `db.init()`/`db.connect()`/`db.close()`
- `reporter/` — Jinja2 HTML reports
- `lint/` — `.feature` linter; rules in `lint/rules/*.yaml`

Tests:
- `tests/` — pytest unit tests (CLI, utils, config)
- `features/` — cucu/Behave integration tests (browser, steps); `features/cucurc.yml` sets test config
- `data/` — fixtures for feature tests

## Coding Standards

- `make fix` to fix style — never run ruff or cucu lint directly
- Update `CHANGELOG.md` per PR; bump `pyproject.toml` version + run `uv lock` on release
- Minimal `__init__.py`; no relative imports; imports at top of file only
- `CONFIG` for shared/multi-location values; `ctx` for scenario-scoped values
- `pathlib` over `os.path`; guard clauses over nesting
- Let exceptions propagate — no bulletproofing, no defensive `getattr`
- No docstrings or comments for obvious code; don't extract unnecessary helpers
- Always check exit codes + stdout/stderr when running shell commands
- Use default `results/` folder; never pass `--results` in examples or tests

## Step Definitions

New steps go in `src/cucu/steps/` and must be explicitly imported in `src/cucu/steps/__init__.py`.

Split into `find_*` + `action_*` helpers (importable by other step modules) and a `@step` wrapper:

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

Use `fuzzy.find(ctx.browser, name, [css_selectors], index=index)` for all DOM matching — not XPath or direct CSS. Pass multiple selector alternatives; the JS library matches by visible text. Source: `src/cucu/browser/fuzzy/core.py`.

For waiting variants, wrap with `retry()` instead of writing polling loops:

```python
from cucu.utils import retry

@step('I wait up to "{seconds}" seconds to see the "{name}" button')
def step_impl(ctx, seconds, name):
    retry(find_button, wait_up_to_s=float(seconds))(ctx, name)
```

## Hooks

Hooks are stored as lists in `CONFIG` — not Behave decorators. Register via `src/cucu/hooks.py`. Never modify `environment.py` directly.

```python
from cucu import register_before_scenario_hook

def setup(ctx):
    ctx.my_value = "something"

register_before_scenario_hook(setup)
```

Available: `register_before_all_hook`, `register_after_all_hook`, `register_before_scenario_hook`, `register_after_scenario_hook`, `register_page_check_hook`, `register_before_retry_hook`.

## Configuration

Config loads in order, each overriding the previous: `~/.cucurc.yml` → cwd → feature file directory → env vars (always wins). Add per-directory `cucurc.yml` files; don't use a single root `.env`. See `src/cucu/config.py` for all `CONFIG.define()` variables.

## Release

1. Bump version in `pyproject.toml` + add `CHANGELOG.md` entry + run `uv lock`
2. PR → merge to main → GitHub Actions publishes to test.pypi.org automatically
3. Manually trigger `publish-production.yml` to publish to pypi.org

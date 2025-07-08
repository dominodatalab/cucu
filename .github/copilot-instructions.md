# Project coding standards

## Definitions
- Feature: A group of releated Scnenarios. AKA a test suite.
- Scenario: A single test case. AKA a test.

## Testing
- Tests in the `/tests` directory validate CLI functionality and are run via `pytest`.
- Tests in the `/features` directory validate the features of cucu and are run via `cucu run`.
- Tests and supporting files in the `/data` directory are used by the tests in the `/features` directory.
- Files, tests and supporting files in the `/src/init_data` directory are used by `cucu init` and validated by test in the `/features` directory.

## Coding standards
- Use `make fix` to check and fix code style issues (skip `make lint`).
- Add a summary to the change log for each PR, incrementing the version number if needed.
- Keep the spec file updated
- Avoid having much in the `__init__.py` file
- Keep commands implemented in the `cli/core.py` file
- Avoid comments where the code is self-explanatory, including obvious single-line comments
- In general use the CONFIG to store values that are used in multiple places and ctx to store values that are shared in a scenario run
- Avoid docstrings for functions that are obvious
- Only import at the top of the file
- Do not use relative imports
- Use guard clauses to avoid indentation
- Don't bulletproof code and instead let exceptions happen
- Don't extract helper functions
- Prefer using more modern python stdlib features like `pathlib`

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
- Use `make lint` to check for code style issues.
- Use `make fix` to fix code style issues.
- Part of `make lint` and `make fix` is to run the `cucu lint` command that checks for code style issues of `.feature` files.
- Add a summary to the change log for each PR, incrementing the version number if needed.
- Keep the spec file updated
- Avoid having much in the `__init__.py` file
- Keep commands implemented in the `cli/core.py` file
- Avoid 1-line code comments where the code is self-explanatory

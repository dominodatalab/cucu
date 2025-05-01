<!-- your project readme here -->

# Development
## E2E tests
Use [cucu](https://pypi.org/project/cucu/) to run e2e-tests with the following:
1. make sure you're in the **repo root**
2. install the --dev dependecies
    ```sh
    uv sync --dev
    ```
3. activate it
    ```sh
    source .venv/bin/activate
    ```
4. run scenario
    ```sh
    cucu run features
    ```

### Other helpful commands

- Show all steps
    ```sh
    cucu steps
    ```
- Run scenario by tag
    ```sh
    cucu run features --tag my_tag
    ```
- Run scenario by line number
    ```sh
    cucu run features/example.feature:8
    ```
- Generate an html report
    ```sh
    cucu report
    ```
- Run scenarios and generate report
    ```sh
    cucu run features -g
    ```
- Lint your feature files!
    _see `/features/lint_rules` for custom rules_
    ```sh
    cucu lint
    ```

# Tagging Tests

> [!Note] This is just an example of how use tags

1. Tags are very important as they provide:

   - Critical metadata for reporting and tracking
   - Control where it runs in CI
   - Filtering on what tests should run

2. They can be at the **Feature** file level or at the **Scenario** level.

3. Here's a list of some notable tags
   | Tag       | Gist                                                                                            | Example   |
   | --------- | ----------------------------------------------------------------------------------------------- | --------- |
   | @sid-#### | **[Required]** The scenario (i.e. test case) id (numbers only) that is used to track and record | @sid-1234 |


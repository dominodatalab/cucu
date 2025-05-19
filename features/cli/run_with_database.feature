Feature: Run with database
  As a developer I want the run to be recorded in the database

  Scenario: User can run a basic non-browser test with database enabled
    Given I run the command "cucu run data/features/echo.feature --database --results {CUCU_RESULTS_DIR}/database-results --no-color-output" and expect exit code "0"

        * # Check run
     When I run the command "cucu dbq "from cucu_run" --db={CUCU_RESULTS_DIR}/database-results/results.db" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" contains the following:
          """
          ┌────────┬─.*
          │ run_id │ .*
          │ int64  │ .*
          ├────────┼─.*
          │      1 │ .*
          └────────┴─.*
          """

        * # Check feature
     When I run the command "cucu dbq "from feature" --db={CUCU_RESULTS_DIR}/database-results/results.db" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" contains the following:
          """
          ┌────────┬─.*
          │ run_id │ .*
          │ int64  │ .*
          ├────────┼─.*
          │      1 │ .*
          └────────┴─.*
          """

        * # Check scenario
     When I run the command "cucu dbq "from scenario" --db={CUCU_RESULTS_DIR}/database-results/results.db" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" contains the following:
          """
          ┌────────┬─.*
          │ run_id │ .*
          │ int64  │ .*
          ├────────┼─.*
          │      1 │ .*
          └────────┴─.*
          """

        * # Check step
     When I run the command "cucu dbq "from step" --db={CUCU_RESULTS_DIR}/database-results/results.db" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" contains the following:
          """
          ┌────────┬─.*
          │ run_id │ .*
          │ int64  │ .*
          ├────────┼─.*
          │      1 │ .*
          └────────┴─.*
          """

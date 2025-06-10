Feature: Run with database
  As a developer I want the run to be recorded in the database

  Scenario: User can run a basic non-browser test with database enabled
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/database-results --no-color-output" and expect exit code "0"

        * # Check run
     When I run the command "cucu dbq "from CucuRun" --db={CUCU_RESULTS_DIR}/database-results/results.db" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
          """
          [\s\S]*
          │ cucu_run_id │ .*
          [\s\S]*
          │ * 1 │ .*
          [\s\S]*
          """

        * # Check feature
     When I run the command "cucu dbq "from Feature" --db={CUCU_RESULTS_DIR}/database-results/results.db" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
          """
          [\s\S]*
          │ cucu_run_id │ .*
          [\s\S]*
          │ * 1 │ .*
          [\s\S]*
          """

        * # Check scenario
     When I run the command "cucu dbq "from Scenario" --db={CUCU_RESULTS_DIR}/database-results/results.db" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
          """
          [\s\S]*
          │ cucu_run_id │ .*
          [\s\S]*
          │ * 1 │ .*
          [\s\S]*
          """

        * # Check step
     When I run the command "cucu dbq "from StepDef" --db={CUCU_RESULTS_DIR}/database-results/results.db" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
          """
          [\s\S]*
          │ cucu_run_id │ .*
          [\s\S]*
          │ * 1 │ .*
          [\s\S]*
          """

Feature: Run with JUnit
  As a developer I want the user to be able to run tests and generate JUnit
  XML reports in the desired locations

  Scenario: User gets the JUnit XML files in the default location
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/run_with_default_junit_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_default_junit_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see a file at "{CUCU_RESULTS_DIR}/run_with_default_junit_results/Echo.xml"

  Scenario: User gets the JUnit XML files in the custom location
    Given I run the command "cucu run data/features/echo.feature --junit {CUCU_RESULTS_DIR}/junit_files --results {CUCU_RESULTS_DIR}/run_with_custom_junit_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_custom_junit_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should not see a file at "{CUCU_RESULTS_DIR}/run_with_custom_junit_results/Echo.xml"
      And I should see a file at "{CUCU_RESULTS_DIR}/junit_files/Echo.xml"

  Scenario: User can see the error message for tables in the JUnit XML results
    Given I run the command "cucu run data/features/feature_with_failing_scenario_with_table.feature --results {CUCU_RESULTS_DIR}/tables_in_output_results" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see the file at "{CUCU_RESULTS_DIR}/tables_in_output_results/Feature with failing to find a table.xml" contains the following:
      """
      RuntimeError: unable to find desired table
      expected:
        | nope | this | is | not | it |

      found:
      "1st" table:
        | Name   | City          | Country       |
        | Alfred | Berlin        | Germany       |
        | Joe    | San Francisco | United States |
        | Maria  | Cancun        | Mexico        |
      """

  Scenario: User can choose to include or exclude stacktraces from the JUnit XML results
    Given I run the command "cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/junit_without_stacktraces_results" and expect exit code "1"
     Then I should see the file at "{CUCU_RESULTS_DIR}/junit_without_stacktraces_results/Feature with failing scenario.xml" does not contain the following:
      """
      raise RuntimeError("step fails on purpose")
      """
     When I run the command "cucu run data/features/feature_with_failing_scenario.feature --junit-with-stacktrace --results {CUCU_RESULTS_DIR}/junit_with_stacktraces_results" and expect exit code "1"
     Then I should see the file at "{CUCU_RESULTS_DIR}/junit_with_stacktraces_results/Feature with failing scenario.xml" contains the following:
      """
      raise RuntimeError("step fails on purpose")
      """

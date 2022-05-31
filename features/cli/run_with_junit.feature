Feature: Run with JUnit
  As a developer I want the user to be able to run tests and generate JUnit
  XML reports in the desired locations

  Scenario: User gets the JUnit XML files in the default location
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/run_with_default_junit_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_default_junit_report" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see the file at "{CUCU_RESULTS_DIR}/run_with_default_junit_results/TESTS-Echo.xml"

  Scenario: User gets the JUnit XML files in the custom location
    Given I run the command "cucu run data/features/echo.feature --junit {CUCU_RESULTS_DIR}/junit_files --results {CUCU_RESULTS_DIR}/run_with_custom_junit_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_custom_junit_report" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should not see the file at "{CUCU_RESULTS_DIR}/run_with_custom_junit_results/TESTS-Echo.xml"
      And I should see the file at "{CUCU_RESULTS_DIR}/junit_files/TESTS-Echo.xml"

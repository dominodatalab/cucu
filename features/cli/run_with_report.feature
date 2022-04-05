Feature: Run with report
  As a developer I want the user to be able to run tests and automatically
  generate the HTML test report.

  Scenario: User can run a passing scenario and generate a report
    Given I run the command "cucu run data/features/feature_with_passing_scenario.feature --results {CUCU_RESULTS_DIR}/run_with_report_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_report_report" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/run_with_report_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see the link "Feature: Feature with passing scenario"
     When I click the link "Feature: Feature with passing scenario"
     Then I should see the link "Scenario: Just a scenario that passes"

  Scenario: User can run a failing scenario and generate a report
    Given I run the command "cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/run_with_report_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_report_report" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/run_with_report_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see the link "Feature: Feature with failing scenario"
     When I click the link "Feature: Feature with failing scenario"
     Then I should see the link "Scenario: Just a scenario that fails"

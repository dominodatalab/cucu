@report
Feature: Run with report
  As a developer I want the user to be able to run tests and automatically
  generate the HTML test report.

  Scenario: User can run a passing scenario and generate a report
    Given I run the command "cucu run data/features/feature_with_passing_scenario.feature --results {CUCU_RESULTS_DIR}/run_with_report_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_report_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/run_with_report_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see the link "Feature with passing scenario"
     When I click the link "Feature with passing scenario"
     Then I should see the link "Just a scenario that passes"

  Scenario: User can run a failing scenario and generate a report
    Given I run the command "cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/run_with_report_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_report_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/run_with_report_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see the link "Feature with failing scenario"
     When I click the link "Feature with failing scenario"
     Then I should see the link "Just a scenario that fails"

  Scenario: User can generate a correct report with long feature name and scenario name
    Given I run the command "cucu run data/features/feature_with_long_names.feature --results {CUCU_RESULTS_DIR}/run_with_report_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_report_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/run_with_report_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see the link "Feature with an absolutely unnecessarily, ridiculously, comically, I don't know what they're thinking, long name"
     When I click the link "Feature with an absolutely unnecessarily, ridiculously, comically, I don't know what they're thinking, long name"
     Then I should see the link "Scenario with an absolutely unnecessarily, ridiculously, comically, I don't know what they're thinking, long name"
      And I click the link "Scenario with an absolutely unnecessarily, ridiculously, comically, I don't know what they're thinking, long name"

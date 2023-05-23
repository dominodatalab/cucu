@report
Feature: Report with custom subheader
  As a developer I want the user to be able to generate reports that contain
  custom subheader handling

  Scenario: User can register a custom subheader handler for reporting
    Given I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_subheader_handling/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_subheader_handling/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu import register_custom_scenario_subheader_in_report_handling

      def subheader_generator(scenario):
          return f'<div>this is a subheader of \{scenario["name"]\}'

      register_custom_scenario_subheader_in_report_handling(subheader_generator)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_subheader_handling/feature_with_custom_subheader_handling.feature" with the following:
      """
      Feature: Feature with custom subheader handling

        Scenario: Scenario with a custom subheader handler
          Given I echo "nothing to see here"
      """
      And I run the command "cucu run {CUCU_RESULTS_DIR}/report_with_custom_subheader_handling --results {CUCU_RESULTS_DIR}/custom_subheader_handling_results --generate-report --report {CUCU_RESULTS_DIR}/custom_subheader_handling_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"

     When I start a webserver at directory "{CUCU_RESULTS_DIR}/custom_subheader_handling_report" and save the port to the variable "PORT"
      And I set the variable "CUCU_BROKEN_IMAGES_PAGE_CHECK" to "disabled"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I wait to click the link "Feature with custom subheader handling"
      And I click the link "Scenario with a custom subheader handler"

     Then I should see the text "this is a subheader of Scenario with a custom subheader handler"

  Scenario: User can register a custom subheader handler for reporting and use "cucu report" after the run
    Given I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_subheader_handling/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_subheader_handling/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu import register_custom_scenario_subheader_in_report_handling

      def subheader_generator(scenario):
          return f'<div>this is a subheader of \{scenario["name"]\}'

      register_custom_scenario_subheader_in_report_handling(subheader_generator)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_subheader_handling/feature_with_custom_subheader_handling.feature" with the following:
      """
      Feature: Feature with custom subheader handling

        Scenario: Scenario with a custom subheader handler
          Given I echo "nothing to see here"
      """
      And I run the command "cucu run {CUCU_RESULTS_DIR}/report_with_custom_subheader_handling --results {CUCU_RESULTS_DIR}/custom_subheader_handling_results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/custom_subheader_handling_results --output {CUCU_RESULTS_DIR}/custom_subheader_handling_report" and expect exit code "0"

     When I start a webserver at directory "{CUCU_RESULTS_DIR}/custom_subheader_handling_report" and save the port to the variable "PORT"
      And I set the variable "CUCU_BROKEN_IMAGES_PAGE_CHECK" to "disabled"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I wait to click the link "Feature with custom subheader handling"
      And I click the link "Scenario with a custom subheader handler"

     Then I should see the text "this is a subheader of Scenario with a custom subheader handler"

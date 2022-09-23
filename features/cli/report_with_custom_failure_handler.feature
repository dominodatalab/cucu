@report
Feature: Report with custom failure handler
  As a developer I want the user to be able to generate reports that contain
  failures with some custom handling of the failure output

  Scenario: User can register a custom failure handler for reporting
    Given I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_failure_handling/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_failure_handling/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu import register_custom_failure_handler

      def my_failure_handler(feature, scenario):
        return f"look ma: \{feature.name\}\n"

      register_custom_failure_handler(my_failure_handler)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_failure_handling/feature_with_custom_tag_handling.feature" with the following:
      """
      Feature: Feature with a failure

        Scenario: Scenario that definitely fails
          Given I click the button "not there"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/report_with_custom_failure_handling --results {CUCU_RESULTS_DIR}/custom_failure_handler_results --generate-report --report {CUCU_RESULTS_DIR}/custom_failure_handler_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/custom_failure_handler_report" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I wait to click the link "Feature with a failure"
      And I click the link "Scenario that definitely fails"
     Then I wait to see the text "look ma: Feature with a failure"

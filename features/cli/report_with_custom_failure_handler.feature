@report
Feature: Report with custom JUnit failure handler
  As a developer I want the user to be able to generate reports that contain
  failures with some custom handling of the failure in the JUnit output

  Scenario: User can register a custom failure handler for reporting
    Given I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_failure_handling/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_failure_handling/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu import register_custom_junit_failure_handler

      def my_failure_handler(feature, scenario):
        return f"\nlook ma: \{feature.name\}\n"

      register_custom_junit_failure_handler(my_failure_handler)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_failure_handling/feature_with_custom_tag_handling.feature" with the following:
      """
      Feature: Feature with a failure

        Scenario: Scenario that definitely fails
          Given I click the button "not there"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/report_with_custom_failure_handling --results {CUCU_RESULTS_DIR}/custom_failure_handler_results --generate-report --report {CUCU_RESULTS_DIR}/custom_failure_handler_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see the file at "{CUCU_RESULTS_DIR}/custom_failure_handler_results/Feature with a failure.xml" matches the following:
      """
      [\s\S]*
      look ma: Feature with a failure
      [\s\S]*
      """

  @workers
  Scenario: User sees custom handler is not duplicated when running in parallel
    Given I create a file at "{CUCU_RESULTS_DIR}/custom_failure_handling_and_workers/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_failure_handling_and_workers/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu import register_custom_junit_failure_handler

      def my_failure_handler(feature, scenario):
        return f"\nlook ma: \{feature.name\}\n"

      register_custom_junit_failure_handler(my_failure_handler)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_failure_handling_and_workers/feature_01_with_custom_tag_handling.feature" with the following:
      """
      Feature: Feature 01 with a failure

        Scenario: Scenario that definitely fails
          Given I click the button "not there"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_failure_handling_and_workers/feature_02_with_custom_tag_handling.feature" with the following:
      """
      Feature: Feature 02 with a failure

        Scenario: Scenario that definitely fails
          Given I click the button "not there"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_failure_handling_and_workers/feature_03_with_custom_tag_handling.feature" with the following:
      """
      Feature: Feature 03 with a failure

        Scenario: Scenario that definitely fails
          Given I click the button "not there"
      """

     Then I run the command "cucu run {CUCU_RESULTS_DIR}/custom_failure_handling_and_workers --workers 2 --results {CUCU_RESULTS_DIR}/custom_failure_handler_results --generate-report --report {CUCU_RESULTS_DIR}/custom_failure_handler_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see the file at "{CUCU_RESULTS_DIR}/custom_failure_handler_results/Feature 01 with a failure.xml" does not match the following:
      """
      [\s\S]*
      look ma: Feature 01 with a failure
      [\s\S]*
      look ma: Feature 01 with a failure
      [\s\S]*
      """
      And I should see the file at "{CUCU_RESULTS_DIR}/custom_failure_handler_results/Feature 02 with a failure.xml" does not match the following:
      """
      [\s\S]*
      look ma: Feature 02 with a failure
      [\s\S]*
      look ma: Feature 02 with a failure
      [\s\S]*
      """
      And I should see the file at "{CUCU_RESULTS_DIR}/custom_failure_handler_results/Feature 03 with a failure.xml" does not match the following:
      """
      [\s\S]*
      look ma: Feature 03 with a failure
      [\s\S]*
      look ma: Feature 03 with a failure
      [\s\S]*
      """

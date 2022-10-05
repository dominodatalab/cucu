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
      And I should see the file at "{CUCU_RESULTS_DIR}/custom_failure_handler_results/TESTS-Feature_with_a_failure.xml" matches the following:
      """
      [\s\S]*
      look ma: Feature with a failure
      [\s\S]*
      """

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
      And I create a file at "{CUCU_RESULTS_DIR}/custom_failure_handling_and_workers/feature_with_custom_tag_handling.feature" with the following:
      """
      Feature: Feature with a failure

        Scenario: Scenario that definitely fails
          Given I click the button "not there"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_failure_handling_and_workers/another_feature_with_custom_tag_handling.feature" with the following:
      """
      Feature: Another feature with a failure

        Scenario: Another scenario that definitely fails
          Given I click the button "not there"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/custom_failure_handling_and_workers --workers 2 --results {CUCU_RESULTS_DIR}/custom_failure_handler_results --generate-report --report {CUCU_RESULTS_DIR}/custom_failure_handler_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see the file at "{CUCU_RESULTS_DIR}/custom_failure_handler_results/TESTS-Feature_with_a_failure.xml" matches the following:
      """
      <testsuite name="Feature with a failure" tests="1" errors="0" failures="1" skipped="0" timestamp=".*">
       <testcase classname="Feature with a failure" name="Scenario that definitely fails" status="failed" time=".*">
        <failure>
         <![CDATA[
      look ma: Feature with a failure

      Given I click the button "not there"
      [\s\S]*
      ]]>
        </failure>
       </testcase>
      </testsuite>
      """

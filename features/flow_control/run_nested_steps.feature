Feature: Run nested steps
  As a developer I want the test writers to be able to measure the execution
  time for a given set of steps.

  Scenario: User gets an appropriate error when attempting to use nested run steps calls
    Given I create a file at "{CUCU_RESULTS_DIR}/nested_run_steps/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/nested_run_steps/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/nested_run_steps/nested_steps_feature.feature" with the following:
      """
      Feature: Feature that attempts to run nested run steps

        Scenario: Scenario that runs nested run steps
          Given I repeat "3" times the following steps with iteration variable "ITER":
            \"\"\"
            Given I repeat "3" times the following steps with iteration variable "ITER":
              '''
              Then I echo "blah"
              '''
            \"\"\"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/nested_run_steps/nested_steps_feature.feature --results {CUCU_RESULTS_DIR}/nested_run_steps_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
      And I should see "{STDOUT}" contains the following:
      """
      it is currently unsupported to run nested flow controls steps
      """

Feature: Vars
  As a developer I want the `cucu vars` command to work as expected

  Scenario: User gets error message when violation can not be fixed
    Given I create a file at "{CUCU_RESULTS_DIR}/cucu_vars_features/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu.config import CONFIG

      CONFIG.define("JUST_A_TEST", "test variable", default=None)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/cucu_vars_features/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/cucu_vars_features/echo.feature" with the following:
      """
      Feature: Feature with sceneario that echos

        Scenario: This is a scenario that simply echos
          Given I echo "Hello There"
      """
     When I run the command "cucu vars {CUCU_RESULTS_DIR}/cucu_vars_features/" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      # can see a built in variable
      And I should see "{STDOUT}" contains the following:
      """
      FEATURE_RESULTS_DIR
      """
      # can see a custom variable defined in the underlying project
      And I should see "{STDOUT}" contains the following:
      """
      JUST_A_TEST
      """

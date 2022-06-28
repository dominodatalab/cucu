Feature: Vars
  As a developer I want the `cucu vars` command to work as expected

  Scenario: User can use cucu vars as expected
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
     When I run the command "cucu vars {CUCU_RESULTS_DIR}/cucu_vars_features/" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      # can see a built in variable
     Then I should see "{STDOUT}" contains the following:
      """
      FEATURE_RESULTS_DIR
      """
      # can see a custom variable defined in the underlying project
      And I should see "{STDOUT}" contains the following:
      """
      JUST_A_TEST
      """

  Scenario: User can set variable values at runtime
    Given I set the variable "FOO" to "blah"
     Then I should see "{FOO}" is equal to "blah"

  Scenario: User can set variable values with multiline strings at runtime
    Given I set the variable "FOO" to "bar"
     When I set the variable "FIZZ" to the following:
      """
      the value of FOO is {FOO}
      """
     Then I should see "{FIZZ}" is equal to "the value of FOO is bar"

@variables
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
      Feature: Feature with scenario that echos

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

  @regex
  Scenario: User can extract values from a string by matching on a regex
    Given I set the variable "LOG" to "the commit sha is 38a465ae3ef5ad41fbecf03b752c3b25cc6302dc"
     When I match the regex "the commit sha is (?P<sha>[a-f0-9]+)" in "{LOG}" and save the group "sha" to the variable "SHA"
     Then I should see "{SHA}" is equal to "38a465ae3ef5ad41fbecf03b752c3b25cc6302dc"

  @regex
  Scenario: User can extract values from a string by searching for a regex
    Given I set the variable "LOG" to "the commit sha is 38a465ae3ef5ad41fbecf03b752c3b25cc6302dc"
     When I search for the regex "sha is (?P<sha>[a-f0-9]+)" in "{LOG}" and save the group "sha" to the variable "SHA"
     Then I should see "{SHA}" is equal to "38a465ae3ef5ad41fbecf03b752c3b25cc6302dc"

  @regex @negative
  Scenario: User gets an error when they can not match on a regex
    Given I set the variable "LOG" to "the commit sha is 38a465ae3ef5ad41fbecf03b752c3b25cc6302dc"
     Then I expect the following step to fail with "\"sha is (?P<sha>[a-f0-9]+)\" did not match \"the commit sha is 38a465ae3ef5ad41fbecf03b752c3b25cc6302dc\""
      """
      Then I match the regex "sha is (?P<sha>[a-f0-9]+)" in "{LOG}" and save the group "sha" to the variable "SHA"
      """

  @regex @negative
  Scenario: User gets an error when they can not search for a regex
    Given I set the variable "LOG" to "the commit sha is 38a465ae3ef5ad41fbecf03b752c3b25cc6302dc"
     Then I expect the following step to fail with "\"boopity\" did not match anything in \"the commit sha is 38a465ae3ef5ad41fbecf03b752c3b25cc6302dc\""
      """
      Then I search for the regex "boopity" in "{LOG}" and save the group "sha" to the variable "SHA"
      """

  Scenario: User can use custom variable resolution and see expected logs
    Given I create a file at "{CUCU_RESULTS_DIR}/custom_variables/environment.py" with the following:
      """
      import cucu
      from cucu.environment import *

      cucu.register_custom_variable_handling("CUSTOM_.*", lambda x: "booyah")
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_variables/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_variables/echo.feature" with the following:
      """
      Feature: Feature with custom variables

        Scenario: That simply prints a custom variable
          Given I echo "\{CUSTOM_VARIABLE\}"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/custom_variables/ --results {CUCU_RESULTS_DIR}/custom_variables_results/ --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      # can see a built in variable
     Then I should see "{STDOUT}" matches the following
      """
      Feature: Feature with custom variables

        Scenario: That simply prints a custom variable
      booyah

          Given I echo "\{CUSTOM_VARIABLE\}"     # .*
          # CUSTOM_VARIABLE="booyah"

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]+
      """

  Scenario: User can use custom variable resolution with secrets and see expected logs
    Given I create a file at "{CUCU_RESULTS_DIR}/custom_variables_with_secrets/environment.py" with the following:
      """
      import cucu
      from cucu.environment import *

      CONFIG["CUCU_SECRETS"] = "CUSTOM_VARIABLE"
      cucu.register_custom_variable_handling("CUSTOM_.*", lambda x: "booyah")
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_variables_with_secrets/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_variables_with_secrets/echo.feature" with the following:
      """
      Feature: Feature with custom variables

        Scenario: That simply prints a custom variable
          Given I echo "\{CUSTOM_VARIABLE\}"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/custom_variables_with_secrets/ --results {CUCU_RESULTS_DIR}/custom_variables_with_secrets_results/" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      # can see a built in variable
     Then I should see "{STDOUT}" does not contain "booyah"

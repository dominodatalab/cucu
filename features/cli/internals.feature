Feature: Internals
  As a developer I wan the user to see the right stacktrace when using steps
  that happen to use our src/cucu/helpers.py functions to define steps.

  Scenario: User gets the right stacktrace for steps using step helpers
    Given I run the command "cucu run data/features/feature_with_failing_scenario_with_web.feature --results={CUCU_RESULTS_DIR}/helpers_stacktrace_results" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" matches the following:
      """
      [\s\S]*
      .*File ".*\/src\/cucu\/steps\/text_steps.py", line 34, in \<module\>
      [\s\S]*
      """

  Scenario: User can run a feature file that uses cucu behave types
    Given I run the command "cucu run data/features/feature_with_scenario_using_nth_type.feature --results={CUCU_RESULTS_DIR}/with_nth_results" and expect exit code "0"

  Scenario: Running cucu in cucu without --results results in exception
    Given I run the command "cucu run data/features/echo.features" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     Then I should see "{STDERR}" contains the following:
      """
      running within cucu but --results was not used
      """

  Scenario: User gets a warning when using an undefined variable reference
    Given I create a file at "{CUCU_RESULTS_DIR}/undefined_variable_usage/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/undefined_variable_usage/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/undefined_variable_usage/undefined_variable_feature.feature" with the following:
      """
      Feature: Feature with undefined variable

        Scenario: This is a scenario that is using an undefined variable
          Given I echo "\{UNDEFINED\}"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/undefined_variable_usage/undefined_variable_feature.feature --results {CUCU_RESULTS_DIR}/undefined_variable_results" and save stdout to "STDOUT" and expect exit code "0"
      And I should see "{STDOUT}" contains the following:
      """
      WARNING variable "UNDEFINED" is undefined
      """

  Scenario: User can use variables with various value types
    Given I create a file at "{CUCU_RESULTS_DIR}/variable_value_types/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/variable_value_types/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu.config import CONFIG

      CONFIG["BOOLEAN_VARIABLE"] = True
      CONFIG["INT_VARIABLE"] = 42
      CONFIG["STRING_VARIABLE"] = "foobar"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/variable_value_types/variable_types_feature.feature" with the following:
      """
      Feature: Variable types feature

        Scenario: This is a senario that echos variables of various types
          Given I echo "\{BOOLEAN_VARIABLE\} \{INT_VARIABLE\} \{STRING_VARIABLE\}"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/variable_value_types/variable_types_feature.feature --results {CUCU_RESULTS_DIR}/variable_value_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" contains the following:
      """
      True 42 foobar
      """
      And I should see "{STDERR}" is empty

  Scenario: User can run consecutive scenarios and be sure that variable values do not "bleed"
    Given I create a file at "{CUCU_RESULTS_DIR}/variable_bleed/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/variable_bleed/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/variable_bleed/bleed.feature" with the following:
      """
      Feature: Feature with two scenarios that make sure variables do not bleed

        Scenario: This scenario sets variables
          Given I set the variable "FOO" to "bar"

        Scenario: This sceneario should not see variables set by the previous one
          Given I should see "\{FOO\}" is empty
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/variable_bleed/bleed.feature --results {CUCU_RESULTS_DIR}/variable_bleed_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"

  @custom
  Scenario: User can define a custom step which uses direct WebElement find methods
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see the element with id "button-with-child" has a child

  @custom
  Scenario: User can define a custom step which uses direct WebElement find methods across iframes
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/frames.html"
     Then I should see the button "button"
      And I should see the element with id "button-with-child" has a child

  @custom
  Scenario: User can define a custom step which uses direct WebElement and finds the elemnet on the default frame
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/frames.html"
     Then I should see the button "button"
      And I should see the element with id "button-on-default-frame" has a child

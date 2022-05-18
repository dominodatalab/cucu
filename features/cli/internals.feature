Feature: Internals
  As a developer I wan the user to see the right stacktrace when using steps
  that happen to use our src/cucu/helpers.py functions to define steps.

  Scenario: User can load cucurc values from a cucucrc file in
    Given I run the command "cucu run data/features/feature_with_failing_scenario_with_web.feature --results={CUCU_RESULTS_DIR}/helpers_stacktrace_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
      Then I should see "{EXIT_CODE}" is equal to "1"
       And I should see "{STDOUT}" matches the following:
       """
       [\s\S]*
       .*File ".*\/src\/cucu\/steps\/text_steps.py", line 25, in \<module\>
       [\s\S]*
       """

  Scenario: User can run a feature file that uses cucu behave types
    Given I run the command "cucu run data/features/feature_with_scenario_using_nth_type.feature --results={CUCU_RESULTS_DIR}/with_nth_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"

  Scenario: Running cucu in cucu without --results results in exception
    Given I run the command "cucu run data/features/echo.features" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is not equal to "0"
      And I should see "{STDERR}" contains the following:
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
     When I run the command "cucu run {CUCU_RESULTS_DIR}/undefined_variable_usage/undefined_variable_feature.feature --results {CUCU_RESULTS_DIR}/undefined_variable_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
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
     When I run the command "cucu run {CUCU_RESULTS_DIR}/variable_value_types/variable_types_feature.feature --results {CUCU_RESULTS_DIR}/variable_value_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" contains the following:
      """
      True 42 foobar
      """
      And I should see "{STDERR}" is empty

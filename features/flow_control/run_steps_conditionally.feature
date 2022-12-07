Feature: Run steps conditionally
  As a developer I want the test writers to be able to run steps based on
  conditions expressed in variables

  Scenario: User can run a set of steps based on values being equal
    Given I set the variable "VARIABLE" to "true"
     When I run the following steps if "{VARIABLE}" is equal to "false"
      """
      When I create a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-not-exist" with the following:
       '''
       this file should not have been created
       '''
      """
     Then I should not see a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-not-exist"
     When I run the following steps if "{VARIABLE}" is equal to "true"
      """
      When I create a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-exist" with the following:
       '''
       this file should not have been created
       '''
      """
     Then I should see a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-exist"

  Scenario: User can run a set of steps based on value containing or not another value
    Given I set the variable "VARIABLE" to "FOOBAR"
     When I run the following steps if "{VARIABLE}" contains "something"
      """
      When I create a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-not-exist" with the following:
       '''
       this file should not have been created
       '''
      """
     Then I should not see a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-not-exist"
     When I run the following steps if "{VARIABLE}" contains "FOO"
      """
      When I create a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-exist" with the following:
       '''
       this file should not have been created
       '''
      """
     Then I should see a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-exist"

  Scenario: User can run a set of steps based on value matching or not
    Given I set the variable "VARIABLE" to "FOOBAR"
     When I run the following steps if "{VARIABLE}" matches "foobar?"
      """
      When I create a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-not-exist" with the following:
       '''
       this file should not have been created
       '''
      """
     Then I should not see a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-not-exist"
     When I run the following steps if "{VARIABLE}" matches "FOO.*"
      """
      When I create a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-exist" with the following:
       '''
       this file should not have been created
       '''
      """
     Then I should see a file at "{SCENARIO_RESULTS_DIR}/conditional_steps/this-should-exist"

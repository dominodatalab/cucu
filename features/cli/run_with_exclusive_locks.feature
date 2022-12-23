Feature: Run with exclusive locks
  As a developer I want the user to be able have a way to make sure features
  and scenarios can get exclusive locks to a resource using the tag @cucu:lock(...)
  to obtain and release locks per scenario runs

  Scenario: User can use exclusive locks per scenarios to guarantee exclusive access to some resource
    Given I create a file at "{CUCU_RESULTS_DIR}/scenario_using_locks/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/scenario_using_locks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{SCENARIO_RESULTS_DIR}/somefile.txt" with the following:
      """
      """
      And I create a file at "{CUCU_RESULTS_DIR}/scenario_using_locks/first_feature_using_locks.feature" with the following:
      """
      Feature: First feature with scenarios using exclusive locks

        Scenario: Scenario that requires exclusive lock to start a webserer on a specific port
          Given I acquire the exclusive lock on the resource "that-somefile-txt" for the duration of this scenario
           When I read the contents of the file at "{SCENARIO_RESULTS_DIR}/somefile.txt" and save to the variable "INPUT"
           Then I create a file at "{SCENARIO_RESULTS_DIR}/somefile.txt" with the following:
            '''
            \{INPUT\}0
            '''
      """
      And I create a file at "{CUCU_RESULTS_DIR}/scenario_using_locks/second_feature_using_locks.feature" with the following:
      """
      Feature: Second feature with scenarios using exclusive locks

        Scenario: Another scenario that requires exclusive lock to start a webserer on a specific port
          Given I acquire the exclusive lock on the resource "that-somefile-txt" for the duration of this scenario
           When I read the contents of the file at "{SCENARIO_RESULTS_DIR}/somefile.txt" and save to the variable "INPUT"
           Then I create a file at "{SCENARIO_RESULTS_DIR}/somefile.txt" with the following:
            '''
            \{INPUT\}0
            '''
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/scenario_using_locks --workers 2 --results {CUCU_RESULTS_DIR}/scenario_using_locks_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see the file at "{SCENARIO_RESULTS_DIR}/somefile.txt" is equal to the following:
      """
      00
      """

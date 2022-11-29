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
      And I create a file at "{CUCU_RESULTS_DIR}/scenario_using_locks/first_feature_using_locks.feature" with the following:
      """
      Feature: First feature with scenarios using exclusive locks

        @cucu:lock(port-20000)
        Scenario: Scenario that requires exclusive lock to start a webserer on a specific port
          Given I start a webserver at directory "\{CUCU_RESULTS_DIR\}/" on port "20000"
           Then I sleep for "3" seconds
      """
      And I create a file at "{CUCU_RESULTS_DIR}/scenario_using_locks/second_feature_using_locks.feature" with the following:
      """
      Feature: Second feature with scenarios using exclusive locks

        @cucu:lock(port-20000)
        Scenario: Another scenario that requires exclusive lock to start a webserer on a specific port
          Given I start a webserver at directory "\{CUCU_RESULTS_DIR\}/" on port "20000"
           Then I sleep for "3" seconds
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/scenario_using_locks --workers 2 --results {CUCU_RESULTS_DIR}/scenario_using_locks_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see the previous step took more than "6" seconds

  Scenario: User can use exclusive locks per feature to guarantee exclusive access to some resource
    Given I create a file at "{CUCU_RESULTS_DIR}/feature_using_locks/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/feature_using_locks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/feature_using_locks/first_feature_using_locks.feature" with the following:
      """
      @cucu:lock(port-20000)
      Feature: First feature with scenarios using exclusive locks

        Scenario: Scenario that requires exclusive lock to start a webserer on a specific port
          Given I start a webserver at directory "\{CUCU_RESULTS_DIR\}/" on port "20000"
           Then I sleep for "3" seconds
      """
      And I create a file at "{CUCU_RESULTS_DIR}/feature_using_locks/second_feature_using_locks.feature" with the following:
      """
      @cucu:lock(port-20000)
      Feature: Second feature with scenarios using exclusive locks

        Scenario: Another scenario that requires exclusive lock to start a webserer on a specific port
          Given I start a webserver at directory "\{CUCU_RESULTS_DIR\}/" on port "20000"
           Then I sleep for "3" seconds
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/feature_using_locks --workers 2 --results {CUCU_RESULTS_DIR}/feature_using_locks_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see the previous step took more than "6" seconds

Feature: Run and measure
  As a developer I want the test writers to be able to measure the execution
  time for a given set of steps.

  Scenario: User gets measurement step output in the logs when measuring following steps
    Given I create a file at "{CUCU_RESULTS_DIR}/measuring_following_steps/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/measuring_following_steps/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/measuring_following_steps/measuring_feature.feature" with the following:
      """
      Feature: Feature that measures a set of steps

        Scenario: Scenario that measures a block of following steps
          Given I run the following timed steps as "Create and Verify Directory"
            \"\"\"
            Then I create the directory at "\{SCENARIO_RESULTS_DIR\}/files/iter-1"
             And I should see the directory at "\{SCENARIO_RESULTS_DIR\}/files/iter-1"
            \"\"\"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/measuring_following_steps/measuring_feature.feature --results {CUCU_RESULTS_DIR}/measuring_following_steps_results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
      """
      Feature: Feature that measures a set of steps

        Scenario: Scenario that measures a block of following steps
            ⤷ Then I create the directory at .*
            ⤷  And I should see the directory at .*
      .* INFO "Create and Verify Directory" timer took .*
          Given I run the following timed steps as "Create and Verify Directory" .*
              \"\"\"
              Then I create the directory at .*
               And I should see the directory at .*
              \"\"\"
      [\s\S]*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

  Scenario: User gets measurement step output in the logs
    Given I create a file at "{CUCU_RESULTS_DIR}/measuring_between_steps/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/measuring_between_steps/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/measuring_between_steps/measuring_feature.feature" with the following:
      """
      Feature: Feature that measures a set of steps

        Scenario: Scenario that measures a block of steps between two steps
          Given I start the timer "Create and Verify Directory"
           When I create the directory at "\{SCENARIO_RESULTS_DIR\}/files/iter-1"
           Then I should see the directory at "\{SCENARIO_RESULTS_DIR\}/files/iter-1"
            And I stop the timer "Create and Verify Directory"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/measuring_between_steps/measuring_feature.feature --results {CUCU_RESULTS_DIR}/measuring_between_steps_results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
      """
      Feature: Feature that measures a set of steps

        Scenario: Scenario that measures a block of steps between two steps
          Given I start the timer "Create and Verify Directory" .*
           When I create the directory at .*
           [\s\S]*
           Then I should see the directory at .*
           [\s\S]*
      .* INFO "Create and Verify Directory" timer took .*
            And I stop the timer "Create and Verify Directory" .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

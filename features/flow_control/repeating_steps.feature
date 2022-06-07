Feature: Repeating steps
  As a developer I want the test writers to be able to repeat steps in a loop.

  Scenario: User can repeat a set of steps N times
    Given I repeat "3" times the following steps with iteration variable "ITER":
      """
      Then I create the directory at "{SCENARIO_RESULTS_DIR}/files/iter-\{ITER\}"
      """
     Then I should see the directory at "{SCENARIO_RESULTS_DIR}/files/iter-1"
      And I should see the directory at "{SCENARIO_RESULTS_DIR}/files/iter-2"
      And I should see the directory at "{SCENARIO_RESULTS_DIR}/files/iter-3"

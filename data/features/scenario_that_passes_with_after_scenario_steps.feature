Feature: Feature with passing scenarios using after scenario steps
  As a developer I want the test writers to be able to run after scenario steps
  when the scenario passes.

  Scenario: Passing scenario with after scenario steps
    Given I run the following steps at the end of the current scenario:
      """
      Then I delete the file at "{CUCU_RESULTS_DIR}/delete-me.txt"
      """
     When I create a file at "{CUCU_RESULTS_DIR}/delete-me.txt" with the following:
      """
      this file should always be cleaned up
      """

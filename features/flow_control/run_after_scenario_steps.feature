Feature: Run after scenario hooks
  As a developer I want the test writers to be able to reliably run after
  scenario steps so they can do test clean up reliably.

  Scenario: User can use after scenario step to clean up files when the scenario passes
    Given I run the command "cucu run data/features/scenario_that_passes_with_after_scenario_steps.feature --results={CUCU_RESULTS_DIR}/passing_sceneario_with_after_steps_results" and expect exit code "0"
     Then I should not see a file at "{CUCU_RESULTS_DIR}/delete-me.txt"

  Scenario: User can use after scenario step to clean up files when the scenario fails
    Given I run the command "cucu run data/features/scenario_that_fails_with_after_scenario_steps.feature --results={CUCU_RESULTS_DIR}/failing_sceneario_with_after_steps_results" and expect exit code "1"
     Then I should not see a file at "{CUCU_RESULTS_DIR}/delete-me.txt"

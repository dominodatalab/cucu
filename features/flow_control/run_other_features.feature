Feature: Run other features
  As a developer I want the test writers to be able to run other feature files
  from a scenario.

  Scenario: User can run a specific feature file
    Given I run the feature at "data/features/echo.feature" with results at "{CUCU_RESULTS_DIR}/run_feature_echo_results"

  Scenario: User gets an error when running a failing feature file
    Given I expect the following step to fail with ""cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/run_failing_feature_from_scenario_results" exited with 1, see above for details"
      """
      Then I run the feature at "data/features/feature_with_failing_scenario.feature" with results at "{CUCU_RESULTS_DIR}/run_failing_feature_from_scenario_results"
      """

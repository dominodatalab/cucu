Feature: Run other features
  As a developer I want the test writers to be able to run other feature files
  from a scenario.

  Scenario: User can run a specific feature file
    Given I run the feature at "data/features/echo.feature" with results at "{CUCU_RESULTS_DIR}/run_feature_echo_results"

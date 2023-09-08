Feature: Platform steps
  As a developer I want the user to be able to interact with files on the
  filesystem

  Scenario: User can use platform skipping steps to skip tests correctly
    Given I run the command "cucu run data/features/feature_with_platform_specific_scenarios.feature --results {CUCU_RESULTS_DIR}/platform_specific_results --no-color-output" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      Feature: Feature with passing scenario
      [\s\S]+
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 1 skipped
      2 steps passed, 0 failed, 2 skipped, 0 undefined
      [\s\S]+
      """

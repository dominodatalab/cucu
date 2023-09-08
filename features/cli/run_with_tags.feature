Feature: Run with tags
  As a developer I want the user to be able to use tags to pick which tests to
  run.

  Scenario: User can run a specific feature using a tag
    Given I run the command "cucu run data/features/feature_with_tagging.feature --tags '@second' --show-skips --results {CUCU_RESULTS_DIR}/scenario_with_tag_results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      @all
      Feature: Feature with tagging

        @first
        Scenario: Scenario that is tagged with @first

        @second
        Scenario: Scenario that is tagged with @second
      second

          Given I echo "second"     # .*

        @disabled @testrail\(123,456\)
        Scenario: Scenario that is skipped

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 2 skipped
      1 step passed, 0 failed, 2 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

  Scenario: User can exclude a specific feature using a tag
    Given I run the command "cucu run data/features/feature_with_tagging.feature --tags '~@second' --show-skips --results {CUCU_RESULTS_DIR}/scenario_without_tag_results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      @all
      Feature: Feature with tagging

        @first
        Scenario: Scenario that is tagged with @first
      first

          Given I echo "first"     # .*

        @second
        Scenario: Scenario that is tagged with @second

        @disabled @testrail\(123,456\)
        Scenario: Scenario that is skipped

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 2 skipped
      1 step passed, 0 failed, 2 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

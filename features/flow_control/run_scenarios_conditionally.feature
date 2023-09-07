Feature: Run scenarios conditionally
  As a developer I want the user to be able to run scenarios conditionally.

  Background: Clean up files
    Given I delete the file at "./skip_first_scenario.txt" if it exists
      And I delete the file at "./skip_second_scenario.txt" if it exists

  Scenario: User can run scenarios conditionally based on presence of a file
    Given I run the command "cucu run data/features/feature_skipping_scenarios_by_file_presence.feature --results {CUCU_RESULTS_DIR}/skip_scenarios_conditionally_results --no-color-output" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      Feature: Feature with skipping scenarios by file presence

        Scenario: That runs only when .\/skip_first_scenario.txt does not exist
          Given I skip this scenario if the file at ".\/skip_first_scenario.txt" exists  .*
      The first scenario ran!
      [\s\S]*
           Then I echo "The first scenario ran!"                                       .*

        Scenario: That runs only when .\/skip_second_scenario.txt does not exist
          Given I skip this scenario if the file at ".\/skip_second_scenario.txt" exists .*
      The second scenario ran!
      [\s\S]*
           Then I echo "The second scenario ran!"                                      .*

      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

     When I create a file at "./skip_first_scenario.txt" with the following:
      """
      bananas
      """
      And I run the command "cucu run data/features/feature_skipping_scenarios_by_file_presence.feature --results {CUCU_RESULTS_DIR}/skip_first_scenario_results --no-color-output" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      Feature: Feature with skipping scenarios by file presence

        Scenario: That runs only when ./skip_first_scenario.txt does not exist
      .* WARNING SKIP Scenario That runs only when .\/skip_first_scenario.txt does not exist: skipping scenario since file at "\{filepath\}" exists
          Given I skip this scenario if the file at ".\/skip_first_scenario.txt" exists

        Scenario: That runs only when ./skip_second_scenario.txt does not exist
          Given I skip this scenario if the file at ".\/skip_second_scenario.txt" exists .*
      The second scenario ran!

           Then I echo "The second scenario ran!"                                        .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 1 skipped
      2 steps passed, 0 failed, 2 skipped, 0 undefined
      [\s\S]*
      """

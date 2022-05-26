Feature: Run
  As a developer I want the user to

  Scenario: User gets an error when running an inexistent feature file
    Given I run the command "cucu run data/features/inexistent.feature --results {CUCU_RESULTS_DIR}/inexistent-results" and save stdout to "STDOUT", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
      And I should see "{STDOUT}" is equal to the following
      """
      FileNotFoundError: data/features/inexistent.feature

      """

  Scenario: User can get the version of the currently running cucu command
    Given I run the command "cucu --version" and save stdout to "STDOUT", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" matches the following
      """
      \d+.\d+.\d+
      """

  Scenario: User can stop the test execution upon the first failure
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --fail-fast --results {CUCU_RESULTS_DIR}/fail_fast_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
      And I should not see the directory at "{CUCU_RESULTS_DIR}/passing_feature_dry_run_results"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with mixed results

        Scenario: Scenario that passes
      passing

          Given I echo "passing"     #  .*

        Scenario: Scenario that fails
          Given I fail                             #  .*
      [\s\S]*
      RuntimeError: step fails on purpose
      [\s]*
      Failing scenarios:
        data/features/feature_with_mixed_results.feature:6  Scenario that fails

      0 features passed, 1 failed, 0 skipped
      1 scenario passed, 1 failed, 0 skipped, 3 untested
      1 step passed, 1 failed, 1 skipped, 0 undefined, 3 untested
      [\s\S]*
      """

  Scenario: User can run a specific scenario by name
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --name 'Scenario that also passes' --results {CUCU_RESULTS_DIR}/run_by_name_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should not see the directory at "{CUCU_RESULTS_DIR}/passing_feature_dry_run_results"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with mixed results

        Scenario: Scenario that also passes
      passing

          Given I echo "passing"     #  .*
      [\s]*
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 4 skipped
      1 step passed, 0 failed, 5 skipped, 0 undefined
      [\s\S]*
      """

  Scenario: User can run a simple test within a reasonable amount of time
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/simple_echo_runtime_results" and save stdout to "STDOUT", exit code to "EXIT_CODE"
     Then I should see the previous step took less than "6" seconds
      And I should see "{EXIT_CODE}" is equal to "0"

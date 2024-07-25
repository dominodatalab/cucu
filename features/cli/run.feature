Feature: Run
  As a developer I want the user to

  Scenario: User gets an error when running an inexistent feature file
    Given I run the command "cucu run data/features/inexistent.feature --results {CUCU_RESULTS_DIR}/inexistent-results" and save stdout to "STDOUT" and expect exit code "1"
      And I should see "{STDOUT}" is equal to the following
      """
      FileNotFoundError: data/features/inexistent.feature

      """

  Scenario: User can get the version of the currently running cucu command
    Given I run the command "cucu --version" and save stdout to "STDOUT" and expect exit code "0"
      And I should see "{STDOUT}" matches the following
      """
      \d+.\d+.\d+
      """

  Scenario: User can stop the test execution upon the first failure
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --fail-fast --results {CUCU_RESULTS_DIR}/fail_fast_results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     Then I should not see the directory at "{CUCU_RESULTS_DIR}/passing_feature_dry_run_results"
      And I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature with mixed results

        Scenario: Scenario that passes
      passing

          Given I echo "passing"     # .*

        Scenario: Scenario that fails
          Given I fail                             # .*
      [\s\S]*
      RuntimeError: step fails on purpose
      [\s]*
      Failing scenarios:
        data/features/feature_with_mixed_results.feature:\d+  Scenario that fails

      0 features passed, 1 failed, 0 skipped
      1 scenario passed, 1 failed, 0 skipped, 5 untested
      1 step passed, 1 failed, 1 skipped, 0 undefined, 8 untested
      [\s\S]*
      """

  Scenario: User can run a specific scenario by name
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --name 'Scenario that also passes' --results {CUCU_RESULTS_DIR}/run_by_name_results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should not see the directory at "{CUCU_RESULTS_DIR}/passing_feature_dry_run_results"
      And I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature with mixed results

        Scenario: Scenario that also passes
      passing

          Given I echo "passing"     # .*
      [\s]*
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 6 skipped
      1 step passed, 0 failed, 10 skipped, 0 undefined
      [\s\S]*
      """

  Scenario: User can run a simple test within a reasonable amount of time
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/simple_echo_runtime_results" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see the previous step took less than "6" seconds

  @runtime-timeout
  Scenario: User can run with a runtime timeout to avoid running over a certain amount of time
    Given I run the command "cucu run data/features/slow_features --runtime-timeout 5 --results {CUCU_RESULTS_DIR}/runtime_timeout_results" and save stdout to "STDOUT" and expect exit code "1"

     # TODO: QE-10912 Investigate why this is taking longer in python 3.11
     Then I should see the previous step took less than "11" seconds
      And I should see "{STDOUT}" contains the following:
      """
      runtime timeout reached, aborting run
      """

  @runtime-timeout
  Scenario: User can run with a runtime timeout and exit without having hit the timeout
    Given I run the command "cucu run data/features/echo.feature --runtime-timeout 300 --results {CUCU_RESULTS_DIR}/runtime_timeout_results" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" does not contain the following:
      """
      runtime timeout reached, aborting run
      """

  @runtime-timeout @workers
  Scenario: User can run with a runtime timeout and workers and exit without having hit the timeout
    Given I run the command "cucu run data/features/tagged_features --workers 2 --runtime-timeout 300 --results {CUCU_RESULTS_DIR}/runtime_timeout_with_workers_results" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" does not contain the following:
      """
      runtime timeout reached, aborting run
      """
  @runtime-timeout @workers
  Scenario: User can run with a runtime timeout and workers to avoid running over a certain amount of time
    Given I run the command "cucu run data/features/slow_features --workers 2 --runtime-timeout 10 --results {CUCU_RESULTS_DIR}/runtime_timeout_with_workers_timed_out_results" and save stdout to "STDOUT" and expect exit code "1"
     # add 14s as multiprocess overhead cost
     Then I should see the previous step took less than "25" seconds
      And I should see "{STDOUT}" contains the following:
      """
      runtime timeout reached, aborting run
      """
  @feature-timeout @workers
  Scenario: When using workers, user can run with a feature timeout to avoid a feature running over a certain amount of time
    Given I run the command "cucu run data/features/slow_features --workers 2 --feature-timeout 3 --results {CUCU_RESULTS_DIR}/runtime_timeout_results" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      .*task timed out.*timeout=3.0.*
      [\s\S]*
      """

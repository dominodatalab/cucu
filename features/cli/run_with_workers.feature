@runtime-timeout
@workers
Feature: Run with workers
  As a developer I want tests to be parallelized using workers and run as
  expected

  Scenario: User can parallelize a slow set of tests and speedup execution
    Given I run the command "cucu run data/features/slow_features --results {CUCU_RESULTS_DIR}/slow_features_without_workers" and expect exit code "0"
     Then I should see the previous step took more than "23" seconds
     When I run the command "cucu run data/features/slow_features --workers 3 --results {CUCU_RESULTS_DIR}/slow_features_with_workers" and expect exit code "0"
     Then I should see the previous step took less than "24" seconds

  Scenario: User gets a report even when running with workesr
    Given I run the command "cucu run data/features/slow_features --workers 3 --generate-report --report {CUCU_RESULTS_DIR}/generate_report_with_workers_report --results {CUCU_RESULTS_DIR}/generate_report_with_workers_results" and expect exit code "0"
     Then I should see a file at "{CUCU_RESULTS_DIR}/generate_report_with_workers_report/index.html"

  Scenario: User gets only dots in the output when running with workers
    Given I run the command "cucu run data/features/slow_features --workers 2 --results {CUCU_RESULTS_DIR}/dots_in_report_with_workers_results" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" is equal to the following:
     """
     ...
     """

  Scenario: User gets progress even when a step is in a retry() block
    Given I create a file at "{CUCU_RESULTS_DIR}/progress_when_in_retry/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/progress_when_in_retry/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/progress_when_in_retry/feature_with_wait_for_step.feature" with the following:
      """
      Feature: Feature with a failure

        Scenario: Scenario that definitely fails
          Given I wait to click the button "not there"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/progress_when_in_retry --workers 2 --results {CUCU_RESULTS_DIR}/progress_when_in_retry_results" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains the following:
      # should contain more than 3 and given its a step that will retry for the
      # 20s we're looking at 3 retries per second so easily 10's of dots
      """
      ............
      """

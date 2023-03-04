@workers
Feature: Run with workers
  As a developer I want tests to be parallelized using workers and run as
  expected

  Scenario: User can parallelize a slow set of tests and speedup execution
    Given I run the command "cucu run data/features/slow_features --results {CUCU_RESULTS_DIR}/slow_features_without_workers" and expect exit code "0"
     Then I should see the previous step took more than "15" seconds
     When I run the command "cucu run data/features/slow_features --workers 3 --results {CUCU_RESULTS_DIR}/slow_features_with_workers" and expect exit code "0"
     Then I should see the previous step took less than "10" seconds

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

  Scenario: User gets final results even when a test throws an exception
    Given I create a file at "{CUCU_RESULTS_DIR}/exception_with_workers/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/exception_with_workers/steps/__init__.py" with the following:
      """
      from cucu import step
      from cucu.steps import *

      @step('I throw an exception')
      def throw_an_exception(ctx):
          raise RuntimeError("something bad happened")
      """
      And I create a file at "{CUCU_RESULTS_DIR}/exception_with_workers/feature_with_exception.feature" with the following:
      """
      Feature: Feature with an exception

        Scenario: Scenario that throws an exception
          Given I throw an exception
      """
      And I create a file at "{CUCU_RESULTS_DIR}/exception_with_workers/feature_with_success.feature" with the following:
      """
      Feature: Feature with success

        Scenario: Scenario that succeeds
          Given I Sleep for "5" seconds
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/exception_with_workers --workers 2 --runtime-timeout 30 --results {CUCU_RESULTS_DIR}/progress_when_in_retry_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     Then I should see "{STDOUT}" matches the following
      """
      ..
      """
      And I should see "{STDERR}" matches the following
      """
      [\s\S]*
      RuntimeError: there are failures, see above for details
      [\s\S]*
      """

Feature: Run with workers
  As a developer I want tests to be parallelized using workers and run as
  expected

  Scenario: User can parallelize a slow set of tests and speedup execution
    Given I run the command "cucu run data/features/slow_features --results {CUCU_RESULTS_DIR}/slow_features_without_workers" and save exit code to "EXIT_CODE"
     Then I should see the previous step took more than "15" seconds
      And I should see "{EXIT_CODE}" is equal to "0"
     When I run the command "cucu run data/features/slow_features --workers 3 --results {CUCU_RESULTS_DIR}/slow_features_with_workers" and save exit code to "EXIT_CODE"
     Then I should see the previous step took less than "12" seconds
      And I should see "{EXIT_CODE}" is equal to "0"

  Scenario: User gets a report even when running with workesr
    Given I run the command "cucu run data/features/slow_features --workers 3 --generate-report --report {CUCU_RESULTS_DIR}/generate_report_with_workers_report --results {CUCU_RESULTS_DIR}/generate_report_with_workers_results" and save exit code to "EXIT_CODE"
      And I should see "{EXIT_CODE}" is equal to "0"
     Then I should see the file at "{CUCU_RESULTS_DIR}/generate_report_with_workers_report/index.html"

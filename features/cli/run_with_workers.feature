Feature: Run with workers
  As a developer I want tests to be parallelized using workers and run as
  expected

  Scenario: User can parallelize a slow set of tests and speedup execution
    Given I run the command "cucu run data/features/slow_features --results {CUCU_RESULTS_DIR}/slow_features_without_workers" and save exit code to "EXIT_CODE"
     Then I should see the previous step took more than "9" seconds
      And I should see "{EXIT_CODE}" is equal to "0"
     When I run the command "cucu run data/features/slow_features --workers 3 --results {CUCU_RESULTS_DIR}/slow_features_with_workers" and save exit code to "EXIT_CODE"
     Then I should see the previous step took less than "6" seconds
      And I should see "{EXIT_CODE}" is equal to "0"

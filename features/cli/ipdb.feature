Feature: ipdb
  As a developer I want the test writer to be able to use the ipdb console to
  debug test runs.

  Scenario: User gets the ipdb console to show when hitting a failure and quit
    Given I run the following script and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
      """
      echo 'quit\n' | cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/ipdb-debugging-results --ipdb-on-failure
      """
     Then I should see "{EXIT_CODE}" is equal to "1"
      # XXX: temporary solution as the ipdb output contains ansi codes we can't
      #      seem to make ipdb output stop producing those.
      And I strip ansi codes from "{STDOUT}" and save to the variable "STDOUT"
      And I should see "{STDOUT}" contains the following
      """
      ---> 55     raise RuntimeError("step fails on purpose")
      """

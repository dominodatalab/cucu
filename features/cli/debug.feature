Feature: debug
  As a developer I want the test writer to be able to use the debug console to
  debug test runs.

  Scenario: User gets the debug console to show when hitting a failure and quit
    Given I run the following script and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      """
      echo 'quit\n' | cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/debug-debugging-results --debug-on-failure
      """
    # XXX: temporary solution as the debug output contains ansi codes we can't
    #      seem to make debug output stop producing those.
    Then I strip ansi codes from "{STDOUT}" and save to the variable "STDOUT"
    And I should see "{STDOUT}" contains the following
      """
      -> raise AssertionError("step fails on purpose")
      """

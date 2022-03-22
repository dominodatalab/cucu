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
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with failing scenario

        Scenario: Just a scenario that fails
      [\s\S]*
           54 def i_fail\(_\):
      ---> 55     raise RuntimeError\("step fails on purpose"\)
      [\s\S]*
      ipdb>     Given I fail     #  .*
      Traceback \(most recent call last\):
      [\s\S]*
      RuntimeError: step fails on purpose
      [\s\S]*

      Failing scenarios:
        data/features/feature_with_failing_scenario.feature:3  Just a scenario that fails

      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 1 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

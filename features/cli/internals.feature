Feature: Internals
  As a developer I wan the user to see the right stacktrace when using steps
  that happen to use our src/cucu/helpers.py functions to define steps.

  Scenario: User can load cucurc values from a cucucrc file in
    Given I run the command "cucu run data/features/feature_with_failing_scenario_with_web.feature --results={CUCU_RESULTS_DIR}/helpers_stacktrace_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
      Then I should see "{EXIT_CODE}" is equal to "1"
       And I should see "{STDOUT}" matches the following:
       """
       [\s\S]*
       .*File ".*\/src\/cucu\/steps\/text_steps.py", line 25, in \<module\>
       [\s\S]*
       """

  Scenario: User can run a feature file that uses cucu behave types
    Given I run the command "cucu run data/features/feature_with_scenario_using_nth_type.feature --results={CUCU_RESULTS_DIR}/with_nth_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"

  Scenario: Running cucu in cucu without --results results in exception
    Given I run the command "cucu run data/features/echo.features" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is not equal to "0"
      And I should see "{STDERR}" contains the following:
      """
      running within cucu but --results was not used
      """

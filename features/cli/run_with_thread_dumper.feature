Feature: Run with thread dumper
  As a developer I want the framework to be able to run in a mode where we can
  get a periodic thread dump which can help debugging issues in CI.

  Scenario: User gets a single thread stacktrace dump and cucu exits cleanly
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/thread_dumper_results --periodic-thread-dumper=15 --no-color-output" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see the previous step took less than "10" seconds
      And I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      <_MainThread\(MainThread, started \d+\)>
      [\s\S]*

      <ThreadDumper\(Thread-1, started \d+\)>
      [\s\S]*
      Feature: Echo

        Scenario: Echo an environment variable
      [\s\S]*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      6 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

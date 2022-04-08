Feature: Run with logging
  As a developer I want the user to get the right logging when using the
  --logging-level option

  Scenario: User gets does not get debug logging by default
    Given I run the command "cucu run data/features/feature_with_logging.feature --results {CUCU_RESULTS_DIR}/default-logging-results" and save stdout to "STDOUT", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with logging

        Scenario: Logging at various levels
      .* INFO hello
          Given I log "hello" at level "info"      #  in .*
            And I log "cruel" at level "debug"     #  in .*
      .* WARNING world
            And I log "world" at level "warn"      #  in .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

  Scenario: User can expose debug logging when they want it
    Given I run the command "cucu run data/features/feature_with_logging.feature --logging-level debug --results {CUCU_RESULTS_DIR}/debug-logging-results" and save stdout to "STDOUT", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature with logging

        Scenario: Logging at various levels
      .* INFO hello
          Given I log "hello" at level "info"      #  in .*
      .* DEBUG cruel
            And I log "cruel" at level "debug"     #  in .*
      .* WARNING world
            And I log "world" at level "warn"      #  in .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

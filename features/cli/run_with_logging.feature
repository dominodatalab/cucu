Feature: Run with logging
  As a developer I want the user to get the right logging when using the
  --logging-level option

  Scenario: User gets does not get debug logging by default
    Given I run the command "cucu run data/features/feature_with_logging.feature --results {CUCU_RESULTS_DIR}/default-logging-results --no-color-output" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      [\s\S]*Feature: Feature with logging

        Scenario: Logging at various levels
      .* INFO hello
          Given I log "hello" at level "info" \s*# .*
            And I log "cruel" at level "debug" \s*# .*
      .* WARNING world
            And I log "world" at level "warning" \s*# .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped
      [\s\S]*
      """

  Scenario: User can expose debug logging when they want it
    Given I run the command "cucu run data/features/feature_with_logging.feature --logging-level debug --results {CUCU_RESULTS_DIR}/debug-logging-results --no-color-output" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature with logging
      [\s\S]*
        Scenario: Logging at various levels
      [\s\S]*.* INFO hello
          Given I log "hello" at level "info" \s*# .*
      .* DEBUG cruel
            And I log "cruel" at level "debug" \s*# .*
      .* WARNING world
            And I log "world" at level "warning" \s*# .*
      .* DEBUG No browsers - skipping MHT webpage snapshot
      .* DEBUG HOOK download_mht_data: passed ✅

      [\s\S]*
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped
      [\s\S]*
      """

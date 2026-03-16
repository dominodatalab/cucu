Feature: Pass-through exceptions
  Steps can let specific exceptions pass through without conversion to
  AssertionError, via CucuPassThroughError or the pass_through decorator.
  Each check runs in a sub-cucu and asserts on the command output.

  Scenario: Exception pass-through and conversion behavior
        * # AssertionError passes through unchanged
    Given I run the command "cucu run data/features/pass_through_assertion_error.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_assertion" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "ASSERT FAILED: assertion message"
      And I should see "{STDOUT}" contains "0 scenarios passed, 1 failed, 0 skipped"

        * # CucuPassThroughError passes through with its message
    Given I run the command "cucu run data/features/pass_through_cucu_passthrough.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_cucu" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "CucuPassThroughError: pass-through message"
      And I should see "{STDOUT}" contains "0 scenarios passed, 0 failed, 1 error, 0 skipped"

        * # CucuPassThroughError wrapping ValueError unwraps to ValueError
    Given I run the command "cucu run data/features/pass_through_unwrap.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_unwrap" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "ValueError: inner value error"
      And I should see "{STDOUT}" contains "0 scenarios passed, 0 failed, 1 error, 0 skipped"

        * # ValueError with pass_through decorator passes through
    Given I run the command "cucu run data/features/pass_through_value_error_passthrough.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_value_passthrough" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "ValueError: value error with passthrough"
      And I should see "{STDOUT}" contains "0 scenarios passed, 0 failed, 1 error, 0 skipped"

        * # ValueError without pass_through is converted to AssertionError
    Given I run the command "cucu run data/features/pass_through_value_error_converted.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_value_converted" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "ASSERT FAILED: value error converted"
      And I should see "{STDOUT}" contains "0 scenarios passed, 1 failed, 0 skipped"

Feature: Pass-through exceptions
  Steps can let specific exceptions pass through without conversion to
  AssertionError, via CucuPassThroughError or the exception_passthru decorator parameter.
  Each check runs in a sub-cucu and asserts on the command output.

  Scenario: AssertionError passes through unchanged
    Given I run the command "cucu run data/features/pass_through_assertion_error.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_assertion" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "ASSERT FAILED: assertion message"
      And I should see "{STDOUT}" contains "0 scenarios passed, 1 failed, 0 skipped"

  Scenario: CucuPassThroughError passes through with its message
    Given I run the command "cucu run data/features/pass_through_cucu_passthrough.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_cucu" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "0 scenarios passed, 0 failed, 1 error, 0 skipped"

  Scenario: CucuPassThroughError wrapping ValueError unwraps to ValueError
    Given I run the command "cucu run data/features/pass_through_unwrap.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_unwrap" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "0 scenarios passed, 0 failed, 1 error, 0 skipped"

  Scenario: ValueError with exception_passthru passes through
    Given I run the command "cucu run data/features/pass_through_value_error_passthrough.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_value_passthrough" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "0 scenarios passed, 0 failed, 1 error, 0 skipped"

  Scenario: ValueError without exception_passthru is converted to AssertionError
    Given I run the command "cucu run data/features/pass_through_value_error_converted.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_value_converted" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "ASSERT FAILED: value error converted"
      And I should see "{STDOUT}" contains "0 scenarios passed, 1 failed, 0 skipped"

  Scenario: ValueError with exception_passthru tuple passes through
    Given I run the command "cucu run data/features/pass_through_tuple_value.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_tuple_value" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "0 scenarios passed, 0 failed, 1 error, 0 skipped"

  Scenario: TypeError with exception_passthru tuple passes through
    Given I run the command "cucu run data/features/pass_through_tuple_type.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_tuple_type" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "0 scenarios passed, 0 failed, 1 error, 0 skipped"

  Scenario: RuntimeError not in exception_passthru tuple is converted to AssertionError
    Given I run the command "cucu run data/features/pass_through_tuple_runtime_converted.feature --no-color-output --results {CUCU_RESULTS_DIR}/pass_through_tuple_runtime" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see "{STDOUT}" contains "ASSERT FAILED: runtime not in passthrough tuple"
      And I should see "{STDOUT}" contains "0 scenarios passed, 1 failed, 0 skipped"

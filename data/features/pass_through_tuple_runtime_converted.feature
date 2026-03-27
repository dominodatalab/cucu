Feature: Pass-through tuple - unlisted type is converted
  Scenario: RuntimeError with exception_passthru tuple is converted to AssertionError
    Then I raise RuntimeError with exception_passthru tuple with message "runtime not in passthrough tuple"

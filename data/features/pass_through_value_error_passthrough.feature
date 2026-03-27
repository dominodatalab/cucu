Feature: Pass-through case - ValueError with exception_passthru
  Scenario: ValueError with exception_passthru passes through
    Then I raise ValueError with exception_passthru with message "value error with passthrough"

Feature: Pass-through case - ValueError converted
  Scenario: ValueError without exception_passthru is converted to AssertionError
    Then I raise ValueError with message "value error converted"

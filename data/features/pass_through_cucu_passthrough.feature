Feature: Pass-through case - CucuPassThroughError
  Scenario: CucuPassThroughError passes through with its message
    Then I raise CucuPassThroughError with message "pass-through message"

Feature: Pass-through case - AssertionError
  Scenario: AssertionError passes through unchanged
    Then I raise AssertionError with message "assertion message"

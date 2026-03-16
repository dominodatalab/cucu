Feature: Pass-through case - ValueError converted
  Scenario: ValueError without pass_through is converted to AssertionError
    Then I raise ValueError with message "value error converted"

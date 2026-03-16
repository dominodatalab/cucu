Feature: Pass-through case - ValueError with pass_through
  Scenario: ValueError with pass_through decorator passes through
    Then I raise ValueError with pass_through with message "value error with passthrough"

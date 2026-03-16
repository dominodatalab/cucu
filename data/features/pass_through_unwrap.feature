Feature: Pass-through case - unwrap
  Scenario: CucuPassThroughError wrapping ValueError unwraps to ValueError
    Then I raise CucuPassThroughError wrapping ValueError "inner value error"

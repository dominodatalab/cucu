Feature: Feature with tied cleanup hooks

  Scenario: Scenario with two near-instant after-scenario hooks
    Given I register two near-instant after-scenario hooks
      And I echo "pass"

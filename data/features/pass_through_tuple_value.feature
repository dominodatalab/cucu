Feature: Pass-through tuple - first listed type
  Scenario: ValueError with exception_passthru tuple passes through
    Then I raise ValueError with exception_passthru tuple with message "tuple passthrough value"

@substeps
Feature: Feature with substeps that sleep

  Scenario: Scenario that uses a step with substeps that sleep
    Given I echo "first!"
      And I use a step with substeps that sleep
      And I echo "last!"

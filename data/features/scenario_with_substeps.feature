@substeps
Feature: Feature with substeps

  Scenario: Scenario that uses a step with substeps
    Given I echo "first!"
      And I use a step with substeps
      And I echo "last!"

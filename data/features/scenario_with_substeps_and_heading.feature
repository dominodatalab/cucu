@substeps
Feature: Feature with substeps and heading

  Scenario: Scenario that uses a step with substeps and a heading
    Given I echo "first!"
      And I use a step with substeps and a heading
      And I echo "last!"

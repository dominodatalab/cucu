@substeps
Feature: Feature with substeps that waits to fail

  Scenario: Scenario that uses a step with substeps that waits to fail
    Given I use a step with substeps that waits to fail
     When I echo "I should never see this"

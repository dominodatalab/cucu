@substeps
Feature: Feature with substeps that fail

  Scenario: Scenario that uses a step with substeps that fail
    Given I use a step with substeps that fail
     # the step below should not be executed
     When I wait to fail

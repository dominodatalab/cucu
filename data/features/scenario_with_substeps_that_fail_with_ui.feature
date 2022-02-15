@substeps
Feature: Feature with substeps that fail with browser open

  Scenario: Scenario that uses a step with substeps that fail
    Given I open a browser at the url "https://www.google.com"
     When I use a step with substeps that fail
     # the step below should not be executed
     Then I wait to fail

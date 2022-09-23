Feature: Feature with background using substeps

  Background: Background that uses step with substeps
    Given I echo "first line of the background"
      And I use a step with substeps that log

  Scenario: Scenario which now has a background using a step with substeps
     When I echo "This is from the scenario"

Feature: Feature with background

  Background: Background applied to every scenario
    Given I echo "This is from the background"

  Scenario: Scenario which now has a background
    When I echo "This is from the scenario"

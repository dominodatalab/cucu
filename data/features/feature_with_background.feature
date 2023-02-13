Feature: Feature with background

  Background: Background applied to every scenario
    Given I echo "This is from the background"

  Scenario: Scenario which now has a background
     When I echo "This is from the scenario"

  @disabled
  Scenario: Scenario that is skipped
     When I echo "should never see this"

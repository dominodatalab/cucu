@all
Feature: Feature with tagging

  @first
  Scenario: Scenario that is tagged with @first
    Given I echo "first"

  @second
  Scenario: Scenario that is tagged with @second
    Given I echo "second"

  @disabled @testrail(123,456)
  Scenario: Scenario that is skipped
    Given I echo "should never see this"

Feature: Feature with mixed results

  Scenario: Scenario that passes
    Given I echo "passing"

  Scenario: Scenario that fails
    Given I fail
      And I echo "should never see this"

  @disabled
  Scenario: Scenario that is skipped
    Given I echo "should never see this"

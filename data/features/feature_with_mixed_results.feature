@mixed
Feature: Feature with mixed results

  Scenario: Scenario that passes
    Given I echo "passing"

  Scenario: Scenario that fails
    Given I fail
      And I echo "should never see this"

  Scenario: Scenario and after-hook both fail
    Given I error after-scenario hook
      And I fail
      And I echo "should never see this"   
      
  Scenario: Scenario with after-hook error
    Given I error after-scenario hook
      And I echo "should never see this"      

  Scenario: Scenario that also passes
    Given I echo "passing"

  Scenario: Scenario that has an undefined step
    Given I attempt to use an undefined step

  @disabled
  Scenario: Scenario that is skipped
    Given I echo "should never see this"        

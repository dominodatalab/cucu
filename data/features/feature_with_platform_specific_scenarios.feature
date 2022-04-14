Feature: Feature with passing scenario

  Scenario: That runs only on mac
    Given I skip this scenario if not on mac
     Then I echo "running test on mac"

  Scenario: That runs only on linux
    Given I skip this scenario if not on linux
     Then I echo "running test on linux"

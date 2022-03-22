Feature: cucu variables
  As a cucu test developer
  I want to be able to use cucus internal variables
  So that I can save some values and reference them later

  Scenario: Check a literal for equality
      Then I should see "Burns" is equal to "Burns"

  Scenario: Check a literal for a substring
       Then I should see "Burns" contains "urn"

  Scenario: Check a literal for a regex match
       Then I should see "Burns" matches the following
          """
          B?urn(?![abcdefghijklmnopqrtuvwxyz])
          """

  Scenario: Check a literal for lack of a regex match
       Then I should see "Burnz" does not match the following
          """
          B?urn(?![abcdefghijklmnopqrtuvwxyz])
          """

  Scenario: Set and check a variable
     When I set the variable "Robert" to "Burns"
     Then I should see the value of variable "Robert" is equal to "Burns"
      And I should see the value of variable "Robert" is not equal to "Frost"

  Scenario: Check inclusion in a variable
    When I set the variable "Robert" to "bertrand"
    Then I should see the value of variable "Robert" contains "tran"
     And I should see the value of variable "Robert" does not contain "ober"

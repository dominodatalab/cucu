Feature: variables
  As a cucu test developer
  I want to be able to use cucus internal variables
  So that I can save some values and reference them later

  Scenario: User can validate two strings are equal
     Then I should see "Burns" is equal to "Burns"

  Scenario: User can validate a string contains a substring
     Then I should see "Burns" contains "urn"

  Scenario: User can check a string matches a regular expression
     Then I should see "Burns" matches the following
          """
          B?urn(?![abcdefghijklmnopqrtuvwxyz])
          """

  Scenario: User can validate a string does not match a regular expression
     Then I should see "Burnz" does not match the following
          """
          B?urn(?![abcdefghijklmnopqrtuvwxyz])
          """

  Scenario: User can set and reference a variable
     When I set the variable "Robert" to "Burns"
     Then I should see "{Robert}" is equal to "Burns"
      And I should see "{Robert}" is not equal to "Frost"

  Scenario: User can validate a variable contains substrings
     When I set the variable "Robert" to "bertrand"
     Then I should see "{Robert}" contains "tran"
      And I should see "{Robert}" does not contain "ober"

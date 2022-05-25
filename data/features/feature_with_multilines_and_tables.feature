Feature: Feature with multilines and tables

  Scenario: Scenario with a step that has a multiline argument
    Given I set the variable "FOO" to "bar"
     Then I echo the following
      """
      This is a multiline text that
      can go on for a few lines
      and print variables like FOO={FOO}
      """

  Scenario: Scenario with a step that has a table argument
    Given I set the variable "FIZZ" to "buzz"
    Given I echo the following
      | header |
      | row 1  |
      | row 2  |
      | {FIZZ} |

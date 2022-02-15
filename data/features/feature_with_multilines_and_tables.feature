Feature: Feature with multilines and tables

  Scenario: Scenario with a step that has a multiline argument
    Given I echo the following
      """
      This is a multiline text that
      can go on for a few lines
      """

  Scenario: Scenario with a step that has a table argument
    Given I echo the following
      | header |
      | row 1  |
      | row 2  |
      | row 3  |

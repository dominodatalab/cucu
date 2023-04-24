Feature: Feature with comments

  Scenario: Scenario with comments
    * # First comment
    Given I set the variable "FOO" to "bar"
     Then I echo the following
          """
          This is a multiline text that
          can go on for a few lines
          and print variables like FOO={FOO}
          """

     * # Second comment about
     When I set the variable "FIZZ" to "buzz"
     * # Comment about {FIZZ}
     Then I echo the following
          | header |
          | row 1  |
          | row 2  |
          | {FIZZ} |

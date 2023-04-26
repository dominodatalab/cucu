Feature: Feature with comments

  Scenario: Scenario with comments
    * # First comment
    Given I set the variable "FOO" to "bar"
      And I echo "{FOO}"
     Then I echo the following
          """
          This is a multiline text that
          can go on for a few lines
          and print variables like FOO={FOO}
          """

     * # Second comment about
     When I set the variable "MY_SECRET" to "buzz"
     * # Comment about {MY_SECRET}
     Then I echo "{MY_SECRET}"

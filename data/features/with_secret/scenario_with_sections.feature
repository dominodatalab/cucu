Feature: Feature with sections

  Scenario: Scenario with sections
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"

        * # First section
     When I set the variable "FOO" to "bar"
      And I echo "{FOO}"

        * ## Subsection
     Then I echo the following
          """
          This is a multiline text that
          can go on for a few lines
          and print variables like FOO={FOO}
          """

        * # Second section about
        # we shouldn't set a secret this way in production because the secret will end up
        # in the source code. However, in test, this is a simple way to mimic a secret
        * ## Subsection Two
     When I set the variable "MY_SECRET" to "buzz"

        * ### Sub-subsection
        * #### Deep subsection
      And I write "{MY_SECRET}" into the input "input type=text"
     Then I should see the text "{MY_SECRET}"

        * # Section about {MY_SECRET}
     Then I echo "{MY_SECRET}"

        * # Cause an intended exception with secrets
     Then I click the button "{MY_SECRET}"

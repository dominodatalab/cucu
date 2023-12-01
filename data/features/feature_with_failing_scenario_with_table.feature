@failing
Feature: Feature with failing to find a table

  Scenario: Scenario that opens a page and fails to find a table
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should see a table that is the following:
        | nope | this | is | not | it |

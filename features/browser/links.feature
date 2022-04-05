Feature: Links
  As a developer I want to make sure the test writer can interact with links

  Background: HTML page with links
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"

  Scenario: User can interact with links
    Given I should see the link "buttons!"
      And I should see the link "checkboxes!"
      And I should see the link "dropdowns!"
     When I click the button "buttons!"
     Then I should not see the link "buttons!"

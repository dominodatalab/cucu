Feature: Links
  As a developer I want to make sure the test writer can interact with links

  Background: HTML page with links
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/links.html"

  Scenario: User can interact with links
    Given I should see the link "buttons!"
      And I should see the link "checkboxes!"
      And I should see the link "dropdowns!"
     When I click the button "buttons!"
     Then I should not see the link "buttons!"

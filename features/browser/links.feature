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

  Scenario: User can interact with duplicate links
    Given I should see the "1st" link "duplicate link!"
      And I should see the "2nd" link "duplicate link!"
     When I click the "1st" link "duplicate link!"
     Then I should see the browser title is "File!"
     When I go back on the browser
      And I click the "2nd" link "duplicate link!"
     Then I should see the browser title is "Iframes!"

  Scenario: User can not click a disabled link
    Given I should see the link "disabled link" is disabled
      And I expect the following step to fail with "unable to click the link, as it is disabled"
      """
      Then I click the link "disabled link"
      """

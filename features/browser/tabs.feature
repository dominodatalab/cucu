Feature: Tabs
  As a developer I want to make sure the test writer can interact with different
  tab elements.

  Background: HTML page with tabs
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tabs.html"

  Scenario: User can switch tabs and verify state
    Given I should see the tab "Joe" is selected
      And I should see the tab "Avery" is not selected
      And I should see the tab "Chris" is not selected
     When I click the tab "Avery"
     Then I should see the tab "Joe" is not selected
      And I should see the tab "Avery" is selected
      And I should see the tab "Chris" is not selected

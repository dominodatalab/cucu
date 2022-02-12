Feature: Duplicate Buttons
  As a developer I want to make sure the test writer can interact with duplicate
  buttons elements.

  Scenario: Can interact with various buttons with the same name
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/duplicate_buttons.html"
     Then I should see no value in the input "value:"
     When I click the "1st" button "button"
     Then I should see "1st button" in the input "value:"
     When I click the "2nd" button "button"
     Then I should see "2nd button" in the input "value:"
     When I click the "3rd" button "button"
     Then I should see "3rd button" in the input "value:"
     When I click the "4th" button "button"
     Then I should see "4th button" in the input "value:"

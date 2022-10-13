Feature: Duplicate Buttons
  As a developer I want to make sure the test writer can interact with duplicate
  buttons elements.

  Background:
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"

  Scenario: User can interact with various buttons with the same name
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/duplicate_buttons.html"
     Then I should see no value in the input "value:"
     When I click the "1st" button "button"
     Then I should see "1st button" in the input "value:"
     When I click the "2nd" button "button"
     Then I should see "2nd button" in the input "value:"
     When I click the "3rd" button "button"
     Then I should see "3rd button" in the input "value:"
     When I click the "4th" button "button"
     Then I should see "4th button" in the input "value:"

  Scenario: User can verify visibility of an nth button
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/duplicate_buttons.html"
      And I should see the "1st" button "button"
      And I should not see the "1st" button "inexistent"
     Then I expect the following step to fail with "unable to find the "3rd" button "inexistent""
      """
      Then I should see the "3rd" button "inexistent"
      """

  Scenario: User can wait to click nth button
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/duplicate_buttons.html?delay_page_load_ms=5000"
     Then I wait to click the "2nd" button "button"
      And I should see the previous step took more than "4" seconds
      And I should see "2nd button" in the input "value:"

  Scenario: User can wait to see the nth button
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/duplicate_buttons.html?delay_page_load_ms=5000"
     Then I wait to see the "2nd" button "button"
      And I should see the previous step took more than "4" seconds

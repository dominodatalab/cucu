Feature: Run steps on element visibility
  As a developer I want the test writers to be able to run steps based on
  element visibility.

  Scenario: User can run steps if a button is visible
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     When I run the following steps if I can see the button "button with child"
     """
     Then I click the button "button with child"
     """
     Then I should see "button with child was clicked" in the input "value:"

  Scenario: User won't run steps if the button is not visible
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     When I run the following steps if I can see the button "nonexistent button"
     """
     Then I click the button "button with child"
     """
     Then I should see the input "value:" is empty

  Scenario: User can run steps if a button is not visible
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     When I run the following steps if I can not see the button "nonexistent button"
     """
     Then I click the button "button with child"
     """
     Then I should see "button with child was clicked" in the input "value:"

  Scenario: User can won't run steps if the button is visible
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     When I run the following steps if I can not see the button "button with child"
     """
     Then I click the button "button with child"
     """
     Then I should see the input "value:" is empty

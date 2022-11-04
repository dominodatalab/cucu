Feature: Browser tab management
  As a developer I want to make sure the test writer can interact with different
  browser tabs and open and close them as necessary

  Scenario: User can open multiple tabs and switch between them
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I should see the browser title is "Links!"
     When I click the button "buttons! in a new tab"
      And I switch to the next browser tab
     Then I should see the browser title is "Buttons!"
     When I switch to the previous browser tab
     Then I should see the browser title is "Links!"
     When I close the current browser tab
     Then I should see the browser title is "Buttons!"

  Scenario: User can wait to switch to a new browser tab
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I should see the browser title is "Links!"
     When I click the button "buttons! in a new tab with a delay"
      And I wait to switch to the next browser tab
     Then I should see the previous step took more than "3" seconds
      And I should see the browser title is "Buttons!"

  Scenario: User gets an error when switching to an inexistent browser tab
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I expect the following step to fail with "no next browser tab available"
      """
      When I switch to the next browser tab
      """
      And I expect the following step to fail with "no previous browser tab available"
      """
      When I switch to the previous browser tab
      """

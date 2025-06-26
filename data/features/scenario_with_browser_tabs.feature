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

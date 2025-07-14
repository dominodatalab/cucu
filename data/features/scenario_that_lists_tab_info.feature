Feature: Browser tab management
  As a developer I want to make sure the test writer can interact with different
  browser tabs and open and close them as necessary

  Scenario: User can list all tabs info
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     When I click the button "buttons! in a new tab"
      And I list all browser tabs info

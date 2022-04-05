Feature: Browser management
  As a developer I want to make sure the test writer can interact with different
  browser windows and open and close them as necessary

  Scenario: User can open multiple browsers and close them
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see the browser title is "Buttons!"
     When I open a new browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I should see the browser title is "Inputs!"
     When I close the current browser
     Then I should see the browser title is "Buttons!"

  Scenario: User can reuse the same open browser and go back in the history
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see the browser title is "Buttons!"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I should see the browser title is "Inputs!"
     When I go back on the browser
     Then I should see the browser title is "Buttons!"
     When I refresh the browser
     Then I should see the browser title is "Buttons!"

  Scenario: User can open multiple browsers and switch between them
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see the browser title is "Buttons!"
     When I open a new browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I should see the browser title is "Inputs!"
     When I switch to the previous browser
     Then I should see the browser title is "Buttons!"
     When I switch to the next browser
     Then I should see the browser title is "Inputs!"

  Scenario: User can open multiple tabs and switch between them
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I should see the browser title is "Links!"
     When I click the button "buttons! in a new tab"
      And I switch to the next browser tab
     Then I should see the browser title is "Buttons!"
     When I switch to the previous browser tab
     Then I should see the browser title is "Links!"
     When I click the button "dropdowns! in a new tab"
      And I switch to the next browser tab
      And I switch to the next browser tab
     Then I should see the browser title is "Dropdowns!"
     When I close the current browser tab
     Then I should see the browser title is "Buttons!"
     When I close the current browser tab
     Then I should see the browser title is "Links!"

  Scenario: User gets appropriate error when checking browser title
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I expect the following step to fail with "unexpected browser title, got "Links!""
     """
     Then I should see the browser title is "foo"
     """

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

  Scenario: User gets an error when switching to an inexistent browser window
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I expect the following step to fail with "no next browser window available"
      """
      When I switch to the next browser
      """
      And I expect the following step to fail with "no previous browser window available"
      """
      When I switch to the previous browser
      """

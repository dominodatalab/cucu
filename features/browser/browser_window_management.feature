Feature: Browser window management
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
     When I close the current browser
     Then I expect the following step to fail with "browser not currently open"
     """
     Then I should see the browser title is "foo"
     """

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

  Scenario: User gets appropriate error when checking browser title
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I expect the following step to fail with "unexpected browser title, got "Links!"
     """
     Then I should see the browser title is "foo"
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

  Scenario: User can set the exact browser dimensions
    # We can set the browser window size but the viewport size may be slightly different (usually height is smaller)
    Given I set the variable "CUCU_BROWSER_WINDOW_WIDTH" to "1081"
      And I set the variable "CUCU_BROWSER_WINDOW_HEIGHT" to "1281"
     When I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
      And I get the browser window size and save it to the variable "WINDOW_SIZE"
      And I execute in the current browser the following javascript and save the result to the variable "VIEWPORT_SIZE"
      """
      return (window.innerWidth + "x" + window.innerHeight);
      """
     Then I should see "{WINDOW_SIZE}" is equal to "1081x1281"
      # on chrome and firefox the viewport height is always slightly shorter due to the way
      # that firefox makes the full window the size you specified and not the
      # viewport
      And I run the following steps if the current browser is "chrome":
      """
        Then I should see "{VIEWPORT_SIZE}" matches "1081x.*"
      """
      And I run the following steps if the current browser is "firefox":
      """
        Then I should see "{VIEWPORT_SIZE}" matches "1081x.*"
      """
      # so the next test doesn't end up with a silly tiny browser window
      And I close the current browser

  Scenario: User can save the current browser url to a variable
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see the browser title is "Buttons!"

     When I save the current browser url to the variable "CURRENT_URL"
      And I navigate to the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I should see the browser title is "Inputs!"

     When I navigate to the url "{CURRENT_URL}"
     Then I should see the browser title is "Buttons!"

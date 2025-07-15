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

  Scenario: User can switch tabs by tab number
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I should see the browser title is "Links!"
     When I click the button "buttons! in a new tab"
      And I switch to the "2nd" browser tab
     Then I should see the browser title is "Buttons!"
     When I switch to the "1st" browser tab
     Then I should see the browser title is "Links!"

  Scenario: User can switch tabs by title pattern
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I should see the browser title is "Links!"
     When I click the button "buttons! in a new tab"
      And I switch to the browser tab that matches "Button"
     Then I should see the browser title is "Buttons!"
     When I switch to the browser tab that matches "ink"
     Then I should see the browser title is "Links!"

  Scenario: User can list all tabs info
    Given I run the command "cucu run data/features/scenario_that_lists_tab_info.feature --results {CUCU_RESULTS_DIR}/browser-tab-info" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" contains the following:
     """
     tab(1): Links!
     """
      And I should see "{STDOUT}" contains the following:
      """
      tab(2): Buttons!
      """
      And I should see "{STDOUT}" contains the following:
      """
      /buttons.html
      """

  Scenario: User can save tab info to a variable
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/links.html"
     Then I should see the browser title is "Links!"
      And I click the button "buttons! in a new tab"
      And I save the browser tabs info to the variable "TABS_INFO"
      And I should see "{TABS_INFO}" contains "tab(2): Buttons!"

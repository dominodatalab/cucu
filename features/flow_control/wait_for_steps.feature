Feature: Wait for steps
  As a developer I want the test writers to be able to actively wait till a set
  of steps has passed or failed.

  Scenario: User can wait for a set of steps to succeed
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=3000"
     When I wait to see the following steps succeed:
      """
      Then I click the button "button with child"
      """
     Then I should see the previous step took more than "2" seconds

  Scenario: User can wait up to some seconds for a set of steps to succeed
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=3000"
     When I wait up to "3" seconds to see the following steps succeed:
      """
      Then I click the button "button with child"
      """
     Then I should see the previous step took more than "2" seconds

  Scenario: User can wait for a set of steps to fail
    # the below steps will successfully creates the directory and sleeps for 2s
    # but on a rerun will fail to create the directory and takes more than 2s
    # but less than 5s
    Given I wait to see the following steps fail:
      """
      Then I create the directory at "{SCENARIO_RESULTS_DIR}/steps_to_fail"
       And I sleep for "2" seconds
      """
     Then I should see the previous step took more than "2" seconds
      And I should see the previous step took less than "4" seconds

  Scenario: User can wait up to seconds for a set of steps to fail
    Given I expect the following step to fail with "underlying steps did not fail"
     """
     When I wait up to "3" seconds to see the following steps fail:
      '''
      Then I sleep for "1" seconds
      '''
     """
     Then I should see the previous step took more than "3" seconds

  Scenario: User can click a button immediately
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=100"
     When I immediately click the button "button with child"
     Then I should see the previous step took less than "1" seconds

  Scenario: User can click a button with a short delay
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=1500"
     When I click the button "button with child"
     Then I should see the previous step took more than "1" seconds

  Scenario: User can click a button after a long delay
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=2500"
     When I wait to click the button "button with child"
     Then I should see the previous step took more than "2" seconds

  Scenario: User can click a button after a set time
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=3500"
     When I wait up to "4" seconds to click the button "button with child"
     Then I should see the previous step took more than "3" seconds

  Scenario: User can run steps if a button is visible with a short delay
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=0"
     When I run the following steps if I can see the button "button with child"
     """
     Then I immediately click the button "button with child"
     """
     Then I should see "button with child was clicked" in the input "value:"

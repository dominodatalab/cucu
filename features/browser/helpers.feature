Feature: Helpers
  As a developer I want the helper steps to be well tested which includes
  making sure that when we fail to find an element we report the necessary
  information

  Scenario: User gets appropriate error when a button is not found
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I expect the following step to fail with "unable to find the button "foo""
      """
      When I click the button "foo"
      """
     When I set the variable "CUCU_STEP_WAIT_TIMEOUT_S" to "3000"
     Then I expect the following step to fail with "unable to find the button "foo""
      """
      When I wait to click the button "foo"
      """
      And I should see the previous step took more than "2" seconds
     Then I expect the following step to fail with "unable to find the button "foo""
      """
      When I wait up to "3" seconds to click the button "foo"
      """
      And I should see the previous step took more than "2" seconds

  Scenario: User gets appropriate error when a checkbox is not in the expected state
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/checkboxes.html"
     Then I expect the following step to fail with "checkbox "checkbox with inner label" is not checked"
      """
      Then I should see the checkbox "checkbox with inner label" is checked
      """

  Scenario: User gets appropriate error when waiting to see a checkbox is not in the expected state
    Given I set the variable "CUCU_STEP_WAIT_TIMEOUT_S" to "5000"
      And I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/checkboxes.html?delay_page_load_ms={CUCU_STEP_WAIT_TIMEOUT_S}"
     Then I expect the following step to fail with "checkbox "checkbox with inner label" is not checked"
      """
      Then I wait to see the checkbox "checkbox with inner label" is checked
      """
      And I should see the previous step took more than "4" seconds
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/checkboxes.html?delay_page_load_ms=10000"
     Then I expect the following step to fail with "checkbox "checkbox with inner label" is not checked"
      """
      Then I wait up to "10" seconds to see the checkbox "checkbox with inner label" is checked
      """
      And I should see the previous step took more than "9" seconds

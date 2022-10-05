Feature: Buttons
  As a developer I want to make sure the test writer can interact with different
  button elements

  Background: HTML page with buttons
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"

  Scenario: User can click a <button>
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "button"
     When I click the button "button"
     Then I should see "button was clicked" in the input "value:"

  Scenario: User can click a <button> with child
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "button with child"
     When I click the button "button with child"
     Then I should see "button with child was clicked" in the input "value:"

  Scenario: User can click a <input type="button">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "input type=button"
     When I click the button "input type=button"
     Then I should see "input type=button was clicked" in the input "value:"

  Scenario: User can click a <input type="submit">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "input type=submit"
     When I click the button "input type=submit"
     Then I should see "input type=submit was clicked" in the input "value:"

  Scenario: User can click a <a>
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "a link"
     When I click the button "a link"
     Then I should see "a link was clicked" in the input "value:"

  Scenario: User can click a <* role="button">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "* role=button"
     When I click the button "* role=button"
     Then I should see "* role=button was clicked" in the input "value:"

  Scenario: User can click a <button> with label for...
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "button with label for"
     When I click the button "button with label for"
     Then I should see "button with label for was clicked" in the input "value:"

  Scenario: User can wait the CUCU_STEP_WAIT_TIMEOUT_S to click a button
    Given I set the variable "CUCU_STEP_WAIT_TIMEOUT_S" to "5"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=5000"
     When I wait to click the button "button"
     Then I should see the previous step took more than "4" seconds

  Scenario: User can wait up to 10s to click a button
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=10000"
     When I wait up to "10" seconds to click the button "button"
     Then I should see the previous step took more than "9" seconds

  Scenario: User can wait the CUCU_STEP_WAIT_TIMEOUT_S to see a button
    Given I set the variable "CUCU_STEP_WAIT_TIMEOUT_S" to "5"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=5000"
     When I wait to see the button "button"
     Then I should see the previous step took more than "4" seconds

  Scenario: User can wait up to 10s to see a button
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?delay_page_load_ms=10000"
     When I wait up to "10" seconds to see the button "button"
     Then I should see the previous step took more than "9" seconds

  @negative
  Scenario: User can wait the CUCU_STEP_WAIT_TIMEOUT_S to not see a button
    Given I set the variable "CUCU_STEP_WAIT_TIMEOUT_S" to "5"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?clear_page_after_ms=5000"
     When I wait to not see the button "* role=button"
     Then I should see the previous step took more than "4" seconds

  @negative
  Scenario: User can wait up to 10s to not see a button
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html?clear_page_after_ms=10000"
     When I wait up to "10" seconds to not see the button "* role=button"
     Then I should see the previous step took more than "9" seconds

  Scenario: User can verify a button is disabled or not
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see the button "button" is not disabled
      And I should see the button "disabled button" is disabled
      And I expect the following step to fail with "button "button" is not disabled"
      """
      Then I should see the button "button" is disabled
      """
      # XXX: should fix up the `not not` situation
      And I expect the following step to fail with "button "disabled button" is not not disabled"
      """
      Then I should see the button "disabled button" is not disabled
      """

  Scenario: User can not click a disabled button
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
      And I should see the button "disabled button" is disabled
      And I expect the following step to fail with "unable to click the button, as it is disabled"
      """
      Then I click the button "disabled button"
      """

  Scenario: User can not click a aria-disabled button
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
      And I should see the button "aria-disabled button" is disabled
      And I expect the following step to fail with "unable to click the button, as it is disabled"
      """
      Then I click the button "aria-disabled button"
      """

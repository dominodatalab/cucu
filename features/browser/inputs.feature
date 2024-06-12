Feature: Inputs
  As a developer I want to make sure the test writer can interact with different
  input elements

  Background: HTML page with inputs
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"

  @disabled @QE-7005
  Scenario: User can write into an <input type="date">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I should see no value in the input "input type=date"
     When I write "01/01/2019" into the input "input type=date"
     Then I should see "2019-01-01" in the input "input type=date"
      And I should see "input type=date was modified" in the input "last touched input"

  @disabled
  Scenario: User can write into an <input type="datetime-local">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=datetime-local"
     When I write "01/01/2019 00:00:00" into the input "input type=datetime-local"
     Then I should see "2019-01-01 00:00:00" in the input "input type=datetime-local"
      And I should see "input type=datetime-local was modified" in the input "last touched input"

  Scenario: User can write into an <input type="email">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=email"
     When I write "foo@bar.com" into the input "input type=email"
     Then I should see "foo@bar.com" in the input "input type=email"
      And I should see "input type=email was modified" in the input "last touched input"

  @disabled
  Scenario: User can write into an <input type="month">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=month"
     When I write "August" into the input "input type=month"
     Then I should see "1980-08" in the input "input type=month"
      And I should see "input type=month was modified" in the input "last touched input"

  Scenario: User can write into an <input type="number">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=number"
     When I write "1234" into the input "input type=number"
     Then I should see "1234" in the input "input type=number"
      And I should see "input type=number was modified" in the input "last touched input"

  Scenario: User can write into an <input type="password">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=password"
     When I write "supersecret" into the input "input type=password"
     Then I should see "supersecret" in the input "input type=password"
      And I should see "input type=password was modified" in the input "last touched input"

  Scenario: User can write into an <input type="search">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=search"
     When I write "just a query" into the input "input type=search"
     Then I should see "just a query" in the input "input type=search"
      And I should see "input type=search was modified" in the input "last touched input"

  Scenario: User can write into an <input type="tel">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=tel"
     When I write "8675309" into the input "input type=tel"
     Then I should see "8675309" in the input "input type=tel"
      And I should see "input type=tel was modified" in the input "last touched input"

  Scenario: User can write into an <input type="text">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=text"
     When I write "some text" into the input "input type=text"
     Then I should see "some text" in the input "input type=text"
      And I should see "input type=text was modified" in the input "last touched input"

  @disabled @QE-7005
  Scenario: User can write into an <input type="time">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=time"
     When I write "0810AM" into the input "input type=time"
     Then I should see "08:10" in the input "input type=time"
      And I should see "input type=time was modified" in the input "last touched input"

  Scenario: User can write into an <input type="url">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=url"
     When I write "https://www.google.com" into the input "input type=url"
     Then I should see "https://www.google.com" in the input "input type=url"
      And I should see "input type=url was modified" in the input "last touched input"

  @disabled @QE-7005
  Scenario: User can write into an <input type="week">
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input type=week"
     When I write "022012" into the input "input type=week"
     Then I should see "2012-W02" in the input "input type=week"
      And I should see "input type=week was modified" in the input "last touched input"

  Scenario: User can write into an <textarea>
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "textarea with label"
     When I write the following into the input "textarea with label"
      """
      line 1
      line 2
      """
     Then I should see the following in the input "textarea with label"
      """
      line 1
      line 2
      """
      And I should see "textarea with label was modified" in the input "last touched input"

  Scenario: User can write into an <input> with label for
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input with label for"
     When I write "boop" into the input "input with label for"
     Then I should see "boop" in the input "input with label for"
      And I should see "input with label for was modified" in the input "last touched input"

  Scenario: User can clear an input
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input with label for"
     When I write "beep" into the input "input with label for"
      And I clear the input "input with label for"
     Then I should see no value in the input "input with label for"
     When I write "blup" into the input "input with label for"
     Then I should see "blup" in the input "input with label for"
      And I should see "input with label for was modified" in the input "last touched input"

  Scenario: User can send an enter key after content
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
      And I should see no value in the input "input accepting enter"
     When I write "beep" into the input "input accepting enter"
      And I send the "enter" key to the input "input accepting enter"
     Then I should see "beep" in the input "input accepting enter"
      And I should see "Enter was sent" in the input "last touched input"

  @wait
  Scenario: User can wait to clear an input
    Given I set the variable "CUCU_STEP_WAIT_TIMEOUT_S" to "5"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html?delay_page_load_ms=5000"
      And I wait to clear the input "input with label for"
     Then I should see the previous step took more than "4" seconds
      And I should see no value in the input "input with label for"

  @wait
  Scenario: User can wait up to 10s to clear an input
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html?delay_page_load_ms=10000"
      And I wait up to "10" seconds to clear the input "input with label for"
     Then I should see the previous step took more than "9" seconds
      And I should see no value in the input "input with label for"

  @wait
  Scenario: User can wait to see an input
    Given I set the variable "CUCU_STEP_WAIT_TIMEOUT_S" to "5"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html?delay_page_load_ms=5000"
     When I wait to see the input "input type=date"
     Then I should see the previous step took more than "4" seconds

  @wait
  Scenario: User can wait to write into an input
    Given I set the variable "CUCU_STEP_WAIT_TIMEOUT_S" to "5"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html?delay_page_load_ms=5000"
     When I wait to write "8675309" into the input "input type=tel"
     Then I should see the previous step took more than "4" seconds
      And I should see "8675309" in the input "input type=tel"

  @wait
  Scenario: User can wait up to 10s to write into an input
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html?delay_page_load_ms=10000"
     When I wait up to "10" seconds to write "8675309" into the input "input type=tel"
     Then I should see the previous step took more than "9" seconds
      And I should see "8675309" in the input "input type=tel"

  Scenario: User can write into an input with an @value set and the input is cleared correctly
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I write "bar" into the input "input with @value set"
      And I should see "bar" in the input "input with @value set"

  Scenario: User cannot write into a disabled input field
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I should see the input "disabled input" is disabled
      And I expect the following step to fail with "unable to write into the input, as it is disabled"
      """
      Then I write "foo" into the input "disabled input"
      """

  Scenario: User cannot clear a disabled input field
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I should see the input "disabled input" is disabled
      And I expect the following step to fail with "unable to clear the input, as it is disabled"
      """
      Then I clear the input "disabled input"
      """

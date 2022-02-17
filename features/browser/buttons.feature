Feature: Buttons
  As a developer I want to make sure the test writer can interact with different
  button elements

  Background: HTML page with buttons
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/buttons.html"

  Scenario: User can click a <button>
    Given I should see no value in the input "value:"
      And I should see the button "button"
     When I click the button "button"
     Then I should see "button" in the input "value:"

  Scenario: User can click a <button> with child
    Given I should see no value in the input "value:"
      And I should see the button "button with child"
     When I click the button "button with child"
     Then I should see "button with child" in the input "value:"

  Scenario: User can click a <input type="button">
    Given I should see no value in the input "value:"
      And I should see the button "input type=button"
     When I click the button "input type=button"
     Then I should see "input type=button" in the input "value:"

  Scenario: User can click a <input type="submit">
    Given I should see no value in the input "value:"
      And I should see the button "input type=submit"
     When I click the button "input type=submit"
     Then I should see "input type=submit" in the input "value:"

  Scenario: User can click a <a>
    Given I should see no value in the input "value:"
      And I should see the button "a link"
     When I click the button "a link"
     Then I should see "a link" in the input "value:"

  Scenario: User can click a <* role="button">
    Given I should see no value in the input "value:"
      And I should see the button "* role=button"
     When I click the button "* role=button"
     Then I should see "* role=button" in the input "value:"

  Scenario: User can click a <button> with label for...
    Given I should see no value in the input "value:"
      And I should see the button "button with label for"
     When I click the button "button with label for"
     Then I should see "button with label for" in the input "value:"

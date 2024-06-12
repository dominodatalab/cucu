Feature: Dropdowns
  As a developer I want to make sure the test writer can interact with different
  dropdowns

  Background: HTML page with dropdowns
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"

  Scenario: User can validate the state of a dropdown
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/dropdowns.html"
     Then I should see the dropdown "Pick a color"
      And I should see the option "blue" is not selected on the dropdown "Pick a color"
      And I should see the option "green" is not selected on the dropdown "Pick a color"
      And I should see the option "red" is selected on the dropdown "Pick a color"

  Scenario: User can select different options on a dropdown
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/dropdowns.html"
     Then I should see the dropdown "Pick a color"
      And I select the option "green" from the dropdown "Pick a color"
      And I should see the option "blue" is not selected on the dropdown "Pick a color"
      And I should see the option "green" is selected on the dropdown "Pick a color"
      And I should see the option "red" is not selected on the dropdown "Pick a color"

  Scenario: User can not select from a disabled dropdown
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/dropdowns.html"
     Then I should see the dropdown "Pick a pet"
      And I expect the following step to fail with "unable to select from the dropdown, as it is disabled"
      """
      Then I select the option "CheeseBall" from the dropdown "Pick a pet"
      """

  Scenario: User can select from the second dropdown with the same name
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/dropdowns.html"
     Then I should see the dropdown "Pick a color"
      And I select the option "ruby" from the "2nd" dropdown "Pick a color"
      And I should see the option "navy" is not selected on the "2nd" dropdown "Pick a color"
      And I should see the option "forrest" is not selected on the "2nd" dropdown "Pick a color"
      And I should see the option "ruby" is selected on the "2nd" dropdown "Pick a color"

  Scenario: User can wait to select from the second dropdown with the same name
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/dropdowns.html?delay_page_load_ms=5000"
     Then I should see the dropdown "Pick a color"
      And I wait to select the option "ruby" from the "2nd" dropdown "Pick a color"
      And I should see the option "navy" is not selected on the "2nd" dropdown "Pick a color"
      And I should see the option "forrest" is not selected on the "2nd" dropdown "Pick a color"
      And I should see the option "ruby" is selected on the "2nd" dropdown "Pick a color"

  Scenario: User can select from a dynamic dropdown
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/dynamic_dropdown.html"
     Then I should see the dropdown "Dynamic Dropdown"
      And I wait to select the option "abbc" from the dynamic dropdown "Dynamic Dropdown"

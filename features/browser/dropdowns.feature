Feature: Dropdowns
  As a developer I want to make sure the test writer can interact with different
  dropdowns

  Background: HTML page with dropdowns
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/dropdowns.html"

  Scenario: User can validate the state of a dropdown
    Given I should see the dropdown "Pick a color"
     Then I should see the option "blue" is not selected on the dropdown "Pick a color"
      And I should see the option "green" is not selected on the dropdown "Pick a color"
      And I should see the option "red" is selected on the dropdown "Pick a color"

  Scenario: User can select different options on a dropdown
    Given I should see the dropdown "Pick a color"
      And I select the option "green" from the dropdown "Pick a color"
     Then I should see the option "blue" is not selected on the dropdown "Pick a color"
      And I should see the option "green" is selected on the dropdown "Pick a color"
      And I should see the option "red" is not selected on the dropdown "Pick a color"

  Scenario: User can not select from a disabled dropdown
    Given I should see the dropdown "Pick a pet"
      And I expect the following step to fail with "unable to select from the dropdown, as it is disabled"
      """
      Then I select the option "CheeseBall" from the dropdown "Pick a pet"
      """

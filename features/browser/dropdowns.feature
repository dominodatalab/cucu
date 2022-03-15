Feature: Dropdowns
  As a developer I want to make sure the test writer can interact with different
  dropdowns

  Background: HTML page with buttons
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/dropdowns.html"

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

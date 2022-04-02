Feature: Comboboxes
  As a developer I want to make sure the test writer can interact with ARIA
  comboboxes

  Background: HTML page with comboboxes
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/comboboxes.html"

  Scenario: User can validate the state of a combox
    Given I should see the dropdown "Pick a Fruit"
     Then I should see the option "Apple" is selected on the dropdown "Pick a Fruit"
      And I should see the option "Banana" is not selected on the dropdown "Pick a Fruit"
      And I should see the option "Blueberry" is not selected on the dropdown "Pick a Fruit"
      And I should see the option "Cherry" is not selected on the dropdown "Pick a Fruit"

  Scenario: User can select different options on a combobox
    Given I should see the dropdown "Pick a Fruit"
     When I select the option "Banana" from the dropdown "Pick a Fruit"
     Then I should see the option "Apple" is not selected on the dropdown "Pick a Fruit"
      And I should see the option "Banana" is selected on the dropdown "Pick a Fruit"
      And I should see the option "Blueberry" is not selected on the dropdown "Pick a Fruit"
      And I should see the option "Cherry" is not selected on the dropdown "Pick a Fruit"

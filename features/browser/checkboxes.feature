Feature: Checkboxes
  As a developer I want to make sure the test writer can interact with different
  checkbox elements

  Background: HTML page with checkboxes
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/checkboxes.html"

  Scenario: User can check the checkbox with inner label
    Given I should see the checkbox "checkbox with inner label" is not checked
     When I check the checkbox "checkbox with inner label"
     Then I should see the checkbox "checkbox with inner label" is checked
  
  Scenario: User can check the checkbox with label after
    Given I should see the checkbox "checkbox with label after" is not checked
     When I check the checkbox "checkbox with label after"
     Then I should see the checkbox "checkbox with label after" is checked
  
  Scenario: User can check the checkbox with role=checkbox
    Given I should see the checkbox "checkbox with role=checkbox" is not checked
     When I check the checkbox "checkbox with role=checkbox"
     Then I should see the checkbox "checkbox with role=checkbox" is checked

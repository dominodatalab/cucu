Feature: Checkboxes
  As a developer I want to make sure the test writer can interact with different
  checkbox elements

  Background: HTML page with checkboxes
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/checkboxes.html"

  Scenario: User can check the checkbox with inner label
    Given I should see the checkbox "checkbox with inner label" is not checked
     When I check the checkbox "checkbox with inner label"
     Then I should see the checkbox "checkbox with inner label" is checked
      And I should see "checkbox with inner label" in the input "last touched checkbox:"

  Scenario: User can check the checkbox with label after
    Given I should see the checkbox "checkbox with label after" is not checked
     When I check the checkbox "checkbox with label after"
     Then I should see the checkbox "checkbox with label after" is checked
      And I should see "checkbox with label after" in the input "last touched checkbox:"

  Scenario: User can check the checkbox with role=checkbox
    Given I should see the checkbox "checkbox with role=checkbox" is not checked
     When I check the checkbox "checkbox with role=checkbox"
     Then I should see the checkbox "checkbox with role=checkbox" is checked
      And I should see "checkbox with role=checkbox" in the input "last touched checkbox:"

  Scenario: User can check the checkbox wrapped with a label
    Given I should see the checkbox "checkbox wrapped with label" is not checked
     When I check the checkbox "checkbox wrapped with label"
     Then I should see the checkbox "checkbox wrapped with label" is checked
      And I should see "checkbox wrapped with label" in the input "last touched checkbox:"

  Scenario: User can not check a disabled checkbox
    Given I should see the checkbox "disabled checkbox" is disabled
      And I expect the following step to fail with "unable to check the checkbox, as it is disabled"
      """
      Then I check the checkbox "disabled checkbox"
      """

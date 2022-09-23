Feature: Multiple scenarios with browser steps

  Scenario: Open our test buttons page
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
     Then I should see the button "button with child"

  Scenario: Open our test checkboxes page
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/checkboxes.html"
     Then I should see the checkbox "checkbox with inner label"

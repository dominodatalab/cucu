Feature: Buttons
  As a developer I want to make sure the test writer can interact with different
  elements inside an iframe without knowing something on screen is inside an
  iframe.

  Background: HTML page with buttons
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/frames.html"

  Scenario: User can see and interact with various elements in iframes
    Given I should see the button "button with child"
      And I should see no value in the input "value:"
      And I should see the checkbox "checkbox with inner label" is not checked
     When I click the button "button with child"
     Then I should see "button with child" in the input "value:"
     When I check the checkbox "checkbox with inner label"
     Then I should see the checkbox "checkbox with inner label" is checked

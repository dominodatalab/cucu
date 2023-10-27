Feature: Draggables
  As a developer I want to make sure the test writer can interact with different
  draggable elements

  Background: HTML page with draggables
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/draggables.html"

  Scenario: User can see that an element is draggable
     When I wait to see the text "Drag"
     Then I should immediately see the element "Drag Me 1" is draggable

  Scenario: User can see that an nth element is draggable
     When I wait to see the text "Drag"
     Then I should immediately see the "2nd" element "Drag Me" is draggable

  Scenario: User can see that an element is not draggable
     When I wait to see the text "Drag"
     Then I should immediately see the element "Drop Here 2" is not draggable

  Scenario: User can see that an nth element is not draggable
     When I wait to see the text "Drag"
     Then I should immediately see the "3rd" element "Drop Here" is not draggable

  Scenario: User can drag an element to an element
     When I wait to see the text "Drag"
     Then I drag the element "Drag Me 1" to the element "Drop Here 1"

  Scenario: User can drag an nth element to the same nth element
     When I wait to see the text "Drag"
     Then I drag the "1st" element "Drag Me" to the "1st" element "Drop Here"

  Scenario: User can drag an nth element to a different nth element
     When I wait to see the text "Drag"
     Then I drag the "2nd" element "Drag Me" to the "3rd" element "Drop Here"

Feature: Draggables
  As a developer I want to make sure the test writer can interact with different
  draggable elements

  Background: HTML page with draggables
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/draggables.html"

  Scenario: User can drag element
     When I wait to see the text "Drag"
     Then I should immediately see the "2nd" element "Drag Me" is draggable
      And I drag the element "Drag Me 1" to the element "Drop Here 2"
      And I drag the element "Drag Me 2" to the element "Drop Here 1"
      And I drag the element "Drag Me 3" to the element "Drop Here 3"
      And I should immediately see the "2nd" element "Drop Here" is not draggable

  @negative
  Scenario: User cannot drag element
     When I wait to see the text "Drag"
     Then I should immediately see the element "Drop Here 2" is not draggable
      And I expect the following step to fail with "Unable to find the element \"Nonexistent drop\""
     """
      When I drag the element "Drag Me 1" to the element "Nonexistent drop"
     """
      And I expect the following step to fail with "Unable to find the element \"Nonexistent drag\""
     """
      When I drag the element "Nonexistent drag" to the element "Drop Here 1"
     """
      And I expect the following step to fail with "Unable to find the element \"Nonexistent drag\", Unable to find the element \"Nonexistent drop\""
     """
      When I drag the element "Nonexistent drag" to the element "Nonexistent drop"
     """
      And I expect the following step to fail with "Drag element Drag Me 1 position did not change"
     """
      When I drag the element "Drag Me 1" to the element "Drop Here 4"
     """

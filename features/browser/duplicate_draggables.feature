Feature: Duplicate Draggables
  As a developer I want to make sure the test writer can interact with duplicate
  draggable elements.

  Background: HTML page with draggables
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/draggables.html"

  Scenario: User can drag nth element
     When I wait to see the text "Drag"
     Then I should immediately see the "2nd" element "Drag Me" is draggable
      And I drag the "1st" element "Drag Me" to the "2nd" element "Drop Here"
      And I drag the "2nd" element "Drag Me" to the "1st" element "Drop Here"
      And I should immediately see the "2nd" element "Drop Here" is not draggable

  @negative
  Scenario: User cannot drag nth elements
     Then I should immediately see the "3rd" element "Drop Here" is not draggable
      And I expect the following step to fail with "Unable to find the \"3rd\" element \"Nonexistent drop\""
     """
      When I drag the "2nd" element "Drag Me" to the "3rd" element "Nonexistent drop"
     """
      And I expect the following step to fail with "Unable to find the \"2nd\" element \"Nonexistent drag\""
     """
      When I drag the "2nd" element "Nonexistent drag" to the "3rd" element "Drop Here"
     """
      And I expect the following step to fail with "Unable to find the \"2nd\" element \"Nonexistent drag\", Unable to find the \"3rd\" element \"Nonexistent drop\""
     """
      When I drag the "2nd" element "Nonexistent drag" to the "3rd" element "Nonexistent drop"
     """
      And I expect the following step to fail with "Drag element Drag Me 1 position did not change"
     """
      When I drag the "1st" element "Drag Me" to the "4th" element "Drop Here"
     """

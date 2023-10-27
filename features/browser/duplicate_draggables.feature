Feature: Duplicate Draggables
  As a developer I want to make sure the test writer can interact with duplicate
  draggable elements.

  Background: HTML page with draggables
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/draggables.html"

  Scenario: User can see that an nth element is draggable
     When I wait to see the text "Drag"
     Then I should immediately see the "2nd" element "Drag Me" is draggable

  Scenario: User can see that an nth element is not draggable
     When I wait to see the text "Drag"
     Then I should immediately see the "3rd" element "Drop Here" is not draggable

  Scenario: User can see that a parent nth element is not draggable with a child nth element that is draggable
     When I wait to see the text "Drag"
     Then I drag the "2nd" element "Drag Me" to the "2nd" element "Drop Here"
      And I should immediately see the "2nd" element "Drop Here" is not draggable

  Scenario: User can drag an nth element to the same nth element
     When I wait to see the text "Drag"
     Then I drag the "3rd" element "Drag Me" to the "3rd" element "Drop Here"
      And I drag the "2nd" element "Drag Me" to the "2nd" element "Drop Here"
      And I drag the "1st" element "Drag Me" to the "1st" element "Drop Here"

  Scenario: User can drag an nth element to a different nth element
     When I wait to see the text "Drag"
     Then I drag the "3rd" element "Drag Me" to the "1st" element "Drop Here"
      And I drag the "2nd" element "Drag Me" to the "3rd" element "Drop Here"
      And I drag the "1st" element "Drag Me" to the "2nd" element "Drop Here"

  Scenario: User can drag nth element to nth element if they exist and they both exist
     When I wait to see the text "Drag"
     Then I drag the "3rd" element "Drag Me" to the "3rd" element "Drop Here" if they both exist

  @negative
  Scenario: User cannot drag nth element as the nth drop element does not exist
     When I wait to see the text "Drag"
     Then I expect the following step to fail with "Unable to find the \"3rd\" element \"Nonexistent drop\""
     """
      When I drag the "2nd" element "Drag Me" to the "3rd" element "Nonexistent drop"
     """

  @negative
  Scenario: User cannot drag nth element as the nth drag element does not exist
     When I wait to see the text "Drag"
     Then I expect the following step to fail with "Unable to find the \"2nd\" element \"Nonexistent drag\""
     """
      When I drag the "2nd" element "Nonexistent drag" to the "3rd" element "Drop Here"
     """

  @negative
  Scenario: User cannot perform drag action as neither nth elements exist
     When I wait to see the text "Drag"
     Then I expect the following step to fail with "Unable to find the \"2nd\" element \"Nonexistent drag\", Unable to find the \"3rd\" element \"Nonexistent drop\""
     """
      When I drag the "2nd" element "Nonexistent drag" to the "3rd" element "Nonexistent drop"
     """

  @negative
  Scenario: User can drag nth element to nth element if they exist but drag element does not exist
     When I wait to see the text "Drag"
     Then I drag the "2nd" element "Nonexistent drag" to the "3rd" element "Drop Here" if they both exist

  @negative
  Scenario: User can drag nth element to nth element if they exist but drop element does not exist
     When I wait to see the text "Drag"
     Then I drag the "2nd" element "Drag Me" to the "3rd" element "Nonexistent drop" if they both exist

Feature: Draggables
  As a developer I want to make sure the test writer can interact with different
  draggable elements

  Background: HTML page with draggables
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/draggables.html"

  Scenario: User can see that an element is draggable
     When I wait to see the text "Drag"
     Then I should immediately see the element "Drag Me 1" is draggable

  Scenario: User can see that an element is not draggable
     When I wait to see the text "Drag"
     Then I should immediately see the element "Drop Here 2" is not draggable

  Scenario: User can drag an element to an element
     When I wait to see the text "Drag"
     Then I drag the element "Drag Me 1" to the element "Drop Here 1"

  Scenario: User can drag an element to an element if they exist and they both exist
     When I wait to see the text "Drag"
     Then I drag the element "Drag Me 1" to the element "Drop Here 1" if they both exist

  @negative
  Scenario: User cannot drag element as the drop element does not exist
     When I wait to see the text "Drag"
     Then I expect the following step to fail with "Unable to find the element \"Nonexistent drop\""
     """
      When I drag the element "Drag Me 1" to the element "Nonexistent drop"
     """

  @negative
  Scenario: User cannot drag element as the drag element does not exist
     When I wait to see the text "Drag"
     Then I expect the following step to fail with "Unable to find the element \"Nonexistent drag\""
     """
      When I drag the element "Nonexistent drag" to the element "Drop Here 1"
     """

  @negative
  Scenario: User cannot perform drag action as neither elements exist
     When I wait to see the text "Drag"
     Then I expect the following step to fail with "Unable to find the element \"Nonexistent drag\", Unable to find the element \"Nonexistent drop\""
     """
      When I drag the element "Nonexistent drag" to the element "Nonexistent drop"
     """

  @negative
  Scenario: User can drag an element to an element if they exist but drag element does not exist
     When I wait to see the text "Drag"
     Then I drag the element "Nonexistent drag" to the element "Drop Here 1" if they both exist

  @negative
  Scenario: User can drag an element to an element if they exist but drop element does not exist
     When I wait to see the text "Drag"
     Then I drag the element "Drag Me 1" to the element "Nonexistent drop" if they both exist

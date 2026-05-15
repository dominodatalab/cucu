Feature: Frames
  As a developer I want to make sure the test writer can interact with different
  elements inside an iframe without knowing something on screen is inside an
  iframe.

  Background: HTML page with buttons
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/frames.html"

  Scenario: User can see and interact with Buttons in iframes
    Given I should see the button "button with child"
      And I should see no value in the input "value:"
      And I should see the checkbox "checkbox with inner label" is not checked
     When I click the button "button with child"
     Then I should see "button with child was clicked" in the input "value:"
     When I check the checkbox "checkbox with inner label"
     Then I should see the checkbox "checkbox with inner label" is checked

  Scenario: User can see and interact with inputs in iframes
     When I write "some text" into the input "input type=text"
     Then I should see "some text" in the input "input type=text"

  Scenario: User can see images in iframes
     Then I should see the image with the alt text "Stars"

  Scenario: User can see multiple things across iframes
     When I write "some text" into the input "input type=text"
     Then I should see "some text" in the input "input type=text"
      And I should see the image with the alt text "Stars"

  Scenario: User can see tables across iframes
     When I write "some text" into the input "input type=text"
      And I should see "some text" in the input "input type=text"
     Then I should see a table that is the following:
        | Name   | City          | Country       |
        | Alfred | Berlin        | Germany       |
        | Joe    | San Francisco | United States |
        | Maria  | Cancun        | Mexico        |

  Scenario: User can interact with elements in a nested iframe
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/nested_frames.html"
     Then I should see the button "button on default frame"
      And I should see the button "button on outer frame"
      And I should see the button "button with child"
     When I click the button "button with child"
     Then I should see "button with child was clicked" in the input "value:"

        * # User can find a shadow-rooted element inside a nested iframe
      And I set the variable "CUCU_SHADOW_DOM_SEARCH" to "enabled"
     Then I should see the button "shadow button in outer frame"

  Scenario: User can only see light DOM elements by default
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/shadow_dom.html"
     Then I should see the text "Shadow DOM Test Page"
      And I should not see the text "leaf one"

  Scenario: User can see both light and shadow DOM elements
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/shadow_dom.html"
      And I set the variable "CUCU_SHADOW_DOM_SEARCH" to "enabled"
     Then I should see the text "Shadow DOM Test Page"
      And I should see the text "leaf one"
      And I should see the button "shadow target"
      And I should see the image with the alt text "shadow image"

Feature: Shadow DOM
  As a developer I want to make sure standard text-finding steps render the
  light DOM normally and do not pierce open shadow roots.

  Background: HTML page with light DOM content and open shadow hosts
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/shadow_dom.html"

  Scenario: User can only see light DOM elements by default
     Then I should see the text "Shadow DOM Test Page"
      And I should not see the text "leaf one"

  Scenario: User can see both light and shadow DOM elements
     When I set the variable "CUCU_SHADOW_DOM_SEARCH" to "enabled"
     Then I should see the text "Shadow DOM Test Page"
      And I should see the text "leaf one"

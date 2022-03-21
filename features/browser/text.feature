Feature: Text
  As a developer I want to make sure the test writer can verify the visibilty
  of text on the page

  Background: HTML page with text
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/text.html"

  Scenario: User can see text within a simple label
     Then I should see the text "just some text in a label"

  Scenario: User can validate the inexistence of text
     Then I should not see the text "inexistent"

  Scenario: User can wait for text that isn't there and get appropriate error
    Given I expect the following step to fail with "unable to find the text "inexistent"":
     """
     When I wait up to "5" seconds to see the text "inexistent"
     """
     Then I should see the previous step took more than "5" seconds

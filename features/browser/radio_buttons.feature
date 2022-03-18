Feature: Radio Buttons
  As a developer I want to make sure the test writer can interact with different
  radio button elements

  Background: HTML page with radio butons
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/radio_buttons.html"

  Scenario: User can select and verify from a few radio buttons
    Given I should see the radio button "cat" is not selected
      And I should see the radio button "dog" is not selected
      And I should see the radio button "rat" is not selected
     When I select the radio button "dog"
     Then I should see the radio button "cat" is not selected
      And I should see the radio button "dog" is selected
      And I should see the radio button "rat" is not selected

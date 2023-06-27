Feature: Radio Buttons
  As a developer I want to make sure the test writer can interact with different
  radio button elements

  Background: HTML page with radio butons
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/radio_buttons.html"

  Scenario: User can select and verify from a few radio buttons
    Given I should see the radio button "cat" is not selected
      And I should see the radio button "dog" is not selected
      And I should see the radio button "rat" is not selected
     When I select the radio button "dog"
     Then I should see the radio button "cat" is not selected
      And I should see the radio button "dog" is selected
      And I should see the radio button "rat" is not selected

  Scenario: User can select a radio button and account for it being selected
    Given I should see the radio button "cat" is not selected
      And I should see the radio button "dog" is not selected
      And I should see the radio button "rat" is not selected
     When I select the radio button "dog" if it is not selected
     Then I should see the radio button "cat" is not selected
      And I should see the radio button "dog" is selected
      And I should see the radio button "rat" is not selected
     When I select the radio button "dog" if it is not selected
     Then I should see the radio button "cat" is not selected
      And I should see the radio button "dog" is selected
      And I should see the radio button "rat" is not selected

  Scenario: User can select a radio button with leading and trailing spaces in name
    Given I should see the radio button "Chicago" is not selected
      And I should see the radio button "Newyork" is not selected
     When I select the radio button "Chicago" if it is not selected
     Then I should see the radio button "Newyork" is not selected
      And I should see the radio button "Chicago" is selected
     When I select the radio button "Newyork" if it is not selected
     Then I should see the radio button "Chicago" is not selected
      And I should see the radio button "Newyork" is selected

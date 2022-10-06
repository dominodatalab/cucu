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

  Scenario: User can select radio button labelled by element with common grandparent
    Given I should see the radio button "Service Account" is not selected
      And I should see the radio button "Individual" is selected
     When I select the radio button "Service Account"
     Then I should see the radio button "Service Account" is selected
      And I should see the radio button "Individual" is not selected

  Scenario: User can select 2nd radio button with the same name
    Given I select the "2nd" radio button "blue" if it is not selected
     Then I should see the "2nd" radio button "blue" is selected

  Scenario: User can not select a disabled radio button
    Given I should see the radio button "red" is disabled
      And I expect the following step to fail with "unable to select the radio button, as it is disabled"
      """
      Then I select the radio button "red"
      """

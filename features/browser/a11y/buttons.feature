@a11y-mode
Feature: A11y Buttons
  As a developer I want to make sure the test writer can interact with different
  button using the various accessibility means that a screen reader would

  Background: Start webserver for data/www directory
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"

  Scenario: User can click a <button> with aria-labelledby using a11y mode
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/a11y/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "button with aria-labelledby"
     When I click the button "button with aria-labelledby"
     Then I should see "button with aria-labelledby was clicked" in the input "value:"

  Scenario: User can click a <button> with aria-label using a11y mode
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/a11y/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "button with aria-label"
     When I click the button "button with aria-label"
     Then I should see "button with aria-label was clicked" in the input "value:"

  Scenario: User can click a <button> with title using a11y mode
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/a11y/buttons.html"
     Then I should see no value in the input "value:"
      And I should see the button "button with title"
     When I click the button "button with title"
     Then I should see "button with title was clicked" in the input "value:"

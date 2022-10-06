Feature: Fuzzy rules
  As a developer I want to make sure the fuzzy rules match the expected elements
  in order.

  Background:
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/fuzzy_rules.html"
     Then I should see no value in the input "value:"

  Scenario: User matches on element with inner text
     When I click the button "button with inner text"
     Then I should see "button with inner text" in the input "value:"

  Scenario: User matches on element with inner aria-label
     When I click the button "button with aria-label"
     Then I should see "button with aria-label" in the input "value:"

  Scenario: User matches on element with child that has inner aria-label
     When I click the button "button with child that has aria-label"
     Then I should see "button with child that has aria-label" in the input "value:"

  Scenario: User matches on element with @title
     When I click the button "button with title"
     Then I should see "button with title" in the input "value:"

  Scenario: User matches on element with @placeholder
     When I click the button "button with placeholder"
     Then I should see "button with placeholder" in the input "value:"

  Scenario: User matches on element with common grandparent
     When I click the button "button with common grandparent"
     Then I should see "button with common grandparent" in the input "value:"

  Scenario: User matches on element with common great grandparent
     When I click the button "button with common great grandparent"
     Then I should see "button with common great grandparent" in the input "value:"

  Scenario: User matches on element with common great great grandparent
     When I click the button "button with common great great grandparent"
     Then I should see "button with common great great grandparent" in the input "value:"

  Scenario: User matches on element with next nested sibling
     When I write "foo" into the input "nested sibling input"
     Then I should see "next nested sibling input" in the input "value:"

  Scenario: User matches on element with previous nested sibling
     When I select the radio button "nested sibling radio"
     Then I should see "previous nested sibling radio button" in the input "value:"

  Scenario: User matches on element wrapped by a labelling element
     When I select the radio button "radio button wrapped with label"
     Then I should see "radio button wrapped with label" in the input "value:"

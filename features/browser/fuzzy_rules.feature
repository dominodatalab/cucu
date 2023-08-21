Feature: Fuzzy rules
  As a developer I want to make sure the fuzzy rules match the expected elements
  in order.

  Scenario: User gets the expected matching before from fuzzy
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/fuzzy_rules.html"
     Then I should see no value in the input "value:"
     When I click the button "button with inner text"
     Then I should see "button with inner text" in the input "value:"
     When I click the button "button with aria-label"
     Then I should see "button with aria-label" in the input "value:"
     When I click the button "button with child that has aria-label"
     Then I should see "button with child that has aria-label" in the input "value:"
     When I click the button "button with title"
     Then I should see "button with title" in the input "value:"
     When I click the button "button with placeholder"
     Then I should see "button with placeholder" in the input "value:"
     When I click the button "button with previous nested sibling label"
     Then I should see "button with previous nested sibling label" in the input "value:"
     When I should see the dropdown "Pick a color"
     Then I wait up to "1" seconds to see the following steps fail
       """
       When I select the option "Apple" from the dropdown "Pick a color"
       """

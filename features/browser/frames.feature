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
     Then I should see "button with child" in the input "value:"
     When I check the checkbox "checkbox with inner label"
     Then I should see the checkbox "checkbox with inner label" is checked

  Scenario: User can see and interact with inputs in iframes
     When I write "01/01/2019" into the input "input type=date"
     When I write "foo@bar.com" into the input "input type=email"
     When I write "1234" into the input "input type=number"
     When I write "supersecret" into the input "input type=password"
     When I write "supersecret" into the input "input type=search"
     When I write "8675309" into the input "input type=tel"
     When I write "some text" into the input "input type=text"
     When I write "0810AM" into the input "input type=time"
     When I write "https://www.google.com" into the input "input type=url"
     When I write "022012" into the input "input type=week"
     When I write "boop" into the input "input with label for"
     Then I should see "2019-01-01" in the input "input type=date"
     Then I should see "foo@bar.com" in the input "input type=email"
     Then I should see "1234" in the input "input type=number"
     Then I should see "supersecret" in the input "input type=password"
     Then I should see "supersecret" in the input "input type=search"
     Then I should see "8675309" in the input "input type=tel"
     Then I should see "some text" in the input "input type=text"
     Then I should see "08:10" in the input "input type=time"
     Then I should see "https://www.google.com" in the input "input type=url"
     Then I should see "2012-W02" in the input "input type=week"
     Then I should see "boop" in the input "input with label for"

Feature: Clipboard
  As a developer I want the test writer to be able to interact with the
  clipboard

  Scenario: User can interact with the clipboard
    Given I start a webserver on port "40000" at directory "data/www"
     When I open a browser at the url "http://{HOST_ADDRESS}:40000/clipboard.html"
      And I click the button "Copy to Clipboard"
      And I wait to see the button "Copied!"
      And I wait to see the button "Copy to Clipboard"
     Then I save the contents of the clipboard to the variable "CLIPBOARD_CONTENTS"
      And I should see "{CLIPBOARD_CONTENTS}" is equal to "Hello World"

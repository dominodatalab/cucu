Feature: Clipboard
  As a developer I want the test writer to be able to interact with the
  clipboard

  Scenario: User can interact with the clipboard
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/clipboard.html"
      And I click the button "Copy to Clipboard"
      And I wait to see the button "Copied!"
      And I wait to see the button "Copy to Clipboard"
     Then I save the contents of the clipboard to the variable "CLIPBOARD_CONTENTS"
      And I should see "{CLIPBOARD_CONTENTS}" is equal to "Hello World"

  Scenario: User can interact with the clipboard even when frames are involved
    For some unknown reason this always succeeds even though it should fail when
    not using the fix in browser_steps

    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/clipboard.html"
      And I click the button "Copy to Clipboard"
      And I wait to see the button "Copied!"
      And I wait to see the button "Copy to Clipboard"

      # Should still work even if brower is currently pointed to subframe
      And I click the button "button"

     Then I save the contents of the clipboard to the variable "CLIPBOARD_CONTENTS"
      And I should see "{CLIPBOARD_CONTENTS}" is equal to "Hello World"

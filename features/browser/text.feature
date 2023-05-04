Feature: Text
  As a developer I want to make sure the test writer can verify the visibilty
  of text on the page

  Scenario: User can see text within a simple label
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     Then I should see the text "just some text in a label"

  Scenario: User can validate the inexistence of text
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     Then I should not see the text "inexistent"

  Scenario: User can wait for text that isn't there and get appropriate error
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     When I expect the following step to fail with "unable to find the text "inexistent"":
      """
      Then I wait up to "5" seconds to see the text "inexistent"
      """
     Then I should see the previous step took more than "5" seconds

  Scenario: User should not match on text inside a <script> element
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     Then I should not see the text "here i am"

  Scenario: User can see text across elements
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     Then I should see the text "and some text with nested tags"

  Scenario: User can find and save text from the current page
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     Then I search for the regex "some text with (?P<word>[^ ]+)" on the current page and save the group "word" to the variable "WORD"
     Then I should see "{WORD}" is equal to "nested"

  Scenario: User can find and save text from all the frames in the current page
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     Then I search for the regex "(?P<word>[^ ]+) some files" on the current page and save the group "word" to the variable "WORD1"
     Then I should see "{WORD1}" is equal to "upload"
     Then I search for the regex "Copy to (?P<word>[^ ]+)" on the current page and save the group "word" to the variable "WORD2"
     Then I should see "{WORD2}" is equal to "Clipboard"

  Scenario: User can see text within an input that was changed at runtime
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
      And I should see the text "just some text in an input"
     When I write "changing this text here" into the input "just some text in an input"
      And I should see the text "changing this text here"

  Scenario: User can see text that partially matches an attribute
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     Then I should see the text "just some text in a textarea"

  Scenario: User can see text that matches a regex
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     Then I should see text matching the regex "just.*a.l[abcd]bel" on the current page

  Scenario: User can see text that matches a regex with nested tags
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     Then I should see text matching the regex "text with n.st.d" on the current page

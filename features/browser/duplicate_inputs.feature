Feature: Duplicate Inputs
  As a developer I want to make sure the test writer can interact with duplicate
  input elements.

  Scenario: User can interact with various inputs with the same name
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/duplicate_inputs.html"
     Then I should see no value in the input "modified input:"
     When I write "foo" into the "1st" input "input"
     Then I should see "input1" in the input "modified input:"
     When I write "foo" into the "2nd" input "input"
     Then I should see "input2" in the input "modified input:"
     When I write "foo" into the "3rd" input "input"
     Then I should see "input3" in the input "modified input:"
     When I write "foo" into the "4th" input "input"
     Then I should see "input4" in the input "modified input:"

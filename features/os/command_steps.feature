Feature: Command steps
  As a developer I want the user to be able to interact with commands and their
  output

  Scenario: User can execute a command and use its output
    Given I run the command "echo -n foobar" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" is equal to "foobar"

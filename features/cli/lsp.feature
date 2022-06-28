Feature: Lsp
  As a developer I want user to be able to start and stop the language server

  Scenario: User can start and stop the language server cleanly
    Given I run the following script and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      """
      cucu lsp < /dev/null
      """
     Then I should see "{STDOUT}" contains "Starting IO server"
      And I should see "{STDOUT}" contains "Closing the event loop"
      And I should see "{STDERR}" is empty

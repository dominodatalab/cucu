Feature: Lsp
  As a developer I want user to be able to start and stop the language server

  Scenario: User can start and stop the language server cleanly
    Given I run the following script and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
      """
      cucu lsp < /dev/null
      """
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDERR}" contains "Starting IO server"
      And I should see "{STDERR}" contains "Closing the event loop"
      And I should see "{STDOUT}" is empty

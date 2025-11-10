Feature: Lsp
  As a developer I want user to be able to start and stop the language server

  Scenario: User can start and stop the language server cleanly
    Given I run the following script and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      """
      cucu lsp < /dev/null
      """
     Then I should see "{STDOUT}" contains "Starting async IO server"
      And I should see "{STDOUT}" contains "Shutting down the server"
      And I should see "{STDERR}" is empty

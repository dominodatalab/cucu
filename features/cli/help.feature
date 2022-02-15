Feature: Run
  As a developer I want the user to 

  Scenario: User gets can get the help menu from cucu to show
    Given I run the command "cucu --help" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" is equal to the following:
      """
      Usage: cucu [OPTIONS] COMMAND [ARGS]...

        main entrypoint

      Options:
        --debug / --no-debug
        --help                Show this message and exit.

      Commands:
        debug   debug cucu library
        report  create an HTML test report from the results directory provided
        run     run a set of feature files
        steps   print available cucu steps

      """
      And I should see "{STDERR}" is empty

Feature: Help
  As a developer I want the user to

  Scenario: User gets can get the help menu from cucu to show
    Given I run the command "cucu --help" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" is equal to the following:
      """
      Usage: cucu [OPTIONS] COMMAND [ARGS]...

        cucu e2e testing framework

      Options:
        --version  Show the version and exit.
        --help     Show this message and exit.

      Commands:
        debug   debug cucu library
        lint    lint feature files
        lsp     start the cucu language server
        report  generate a test report from a results directory
        run     run a set of feature files
        steps   print available cucu steps
        vars    print built-in cucu variables

      """
      And I should see "{STDERR}" is empty

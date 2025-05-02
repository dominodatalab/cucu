Feature: Init
  As a developer I want the `cucu init` command to work as expected

  Scenario: User runs the `cucu init` command and gets a starter project
    Given I create the directory at "{CUCU_RESULTS_DIR}/cucu_init"
     When I run the command "cucu init {CUCU_RESULTS_DIR}/cucu_init" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" contains the following:
      """
      You can now start writing your tests
      """
      And I should see the directory at "{CUCU_RESULTS_DIR}/cucu_init/features"

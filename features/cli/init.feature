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

      * # User can cancel when there are existing files
     When I run the following script and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      """
      echo 'n\n' | cucu init {CUCU_RESULTS_DIR}/cucu_init
      """
     Then I should see "{STDOUT}" contains the following:
      """
      Overwrite existing files? [y/N]:Aborted!
      """

      * # User can overwrite existing files
     When I run the following script and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      """
      echo 'y\n' | cucu init {CUCU_RESULTS_DIR}/cucu_init
      """
     Then I should see "{STDOUT}" contains the following:
      """
      Overwrite existing files? [y/N]:You can now start writing your tests
      """

  Scenario: The example feature actually works
     When I run the following script and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      """
      export COVERAGE_RCFILE={CWD}/pyproject.toml
      cd src/cucu/init_data
      cucu run features --results={CUCU_RESULTS_DIR}/cucu_init_results --no-color-output
      """
     Then I should see "{STDOUT}" matches the following:
       """
       [\s\S]*Feature: Cucu init feature

         @example @another-tag @sid-314159
         Scenario: Example scenario
       [\s\S]*
       1 feature passed, 0 failed, 0 skipped
       1 scenario passed, 0 failed, 0 skipped
       4 steps passed, 0 failed, 0 skipped(, 0 undefined)?
       [\s\S]*
       """

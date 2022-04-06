Feature: Steps
  As a developer I want the user to be able to use the `cucu steps` command
  without any issues.

  Scenario: User can get the current set of available cucu steps
    Given I run the command "cucu steps" and save stdout to "STDOUT", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      # just validate some built-in steps show up
      And I should see "{STDOUT}" contains the following:
      """
      I open a browser at the url "{{url}}"
      """
      And I should see "{STDOUT}" contains the following:
      """
      I start a webserver at directory "{{directory}}" and save the port to the variable "{{variable}}"
      """

  Scenario: User can use `cucu steps` even if there are undefined steps
    Given I create a file at "{CUCU_RESULTS_DIR}/undefined_steps/features/environment.py" with the following:
      """
      import cucu
      cucu.init_environment()
      """
      And I create a file at "{CUCU_RESULTS_DIR}/undefined_steps/features/steps/__init__.py" with the following:
      """
      import cucu
      cucu.init_steps()
      """
      And I create a file at "{CUCU_RESULTS_DIR}/undefined_steps/features/cucurc.yml" with the following:
      """
      CUCU_SECRETS: MY_SECRET
      MY_SECRET: 'super secret'
      """
      And I create a file at "{CUCU_RESULTS_DIR}/undefined_steps/features/feature_that_spills_the_beans.feature" with the following:
      """
      Feature: Feature with an undefined step

        Scenario: This scenario with an undefined step
          Given I attempt to use an undefined step
      """
     When I run the following script and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
      """
      #!{SHELL}
      pushd {CUCU_RESULTS_DIR}/undefined_steps
      cucu steps
      """
     Then I should see "{EXIT_CODE}" is equal to "0"
      # just validate some built-in steps show up
      And I should see "{STDOUT}" contains the following:
      """
      I open a browser at the url "{{url}}"
      """
      And I should see "{STDOUT}" contains the following:
      """
      I start a webserver at directory "{{directory}}" and save the port to the variable "{{variable}}"
      """

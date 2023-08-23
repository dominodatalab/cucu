Feature: Steps
  As a developer I want the user to be able to use the `cucu steps` command
  without any issues.

  Scenario: User can get the current set of available cucu steps
    Given I run the command "cucu steps" and save stdout to "STDOUT" and expect exit code "0"
      # just validate some built-in steps show up
     Then I should see "{STDOUT}" contains the following:
      """
      I open a browser at the url "\{url\}"
      """
      And I should see "{STDOUT}" contains the following:
      """
      I start a webserver at directory "\{directory\}" and save the port to the variable "\{variable\}"
      """

  Scenario: User can use `cucu steps` and get an error when there are undefined steps
    Given I create a file at "{CUCU_RESULTS_DIR}/undefined_steps/features/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/undefined_steps/features/steps/__init__.py" with the following:
      """
      from cucu.steps import *
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
     When I run the command "cucu steps {CUCU_RESULTS_DIR}/undefined_steps/features/feature_that_spills_the_beans.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      # just validate some built-in steps show up
     Then I should see "{STDOUT}" contains the following:
      """
      You can implement step definitions for undefined steps with these snippets:
      """
      And I should see "{STDERR}" contains the following:
      """
      Failure loading some steps, see above for details
      """

  Scenario: User can use `cucu steps` to differentiate between cucu built-in and custom steps
    Given I run the command "cucu steps data/features/custom_step_test" and save stdout to "STDOUT" and expect exit code "0"
      # just validate some built-in steps show up
     Then I should see "{STDOUT}" contains the following:
      """
      cucu:   I open a browser at the url "\{url\}"
      """
      And I should see "{STDOUT}" contains the following:
      """
      custom: This is a custom step
      """

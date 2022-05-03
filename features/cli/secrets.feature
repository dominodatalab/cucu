Feature: Secrets
  As a developer I want the user to have control over what secrets are printed
  in logs and which are masked.

  Scenario: User can run a test while hiding secrets using their cucurc.yml file
    Given I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/cucurc.yml" with the following:
      """
      CUCU_SECRETS: MY_SECRET
      MY_SECRET: 'super secret'
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/features/feature_that_spills_the_beans.feature" with the following:
      """
      Feature: Feature that spills the beans

        Scenario: This scenario prints some secrets to the logs
         Given I echo "the current user is {{USER}}"
           And I echo "{{MY_SECRET}}"
           And I echo "your home directory is at {{HOME}}"
      """
      When I run the command "cucu run {CUCU_RESULTS_DIR}/features_with_secrets --results={CUCU_RESULTS_DIR}/features_with_secrets_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
      Then I should see "{EXIT_CODE}" is equal to "0"
       And I should see "{STDOUT}" does not contain "super secret"

  Scenario: User can run a test while hiding secrets identified by the command line option
    Given I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/cucurc.yml" with the following:
      """
      MY_SECRET: 'super secret'
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/features/feature_that_spills_the_beans.feature" with the following:
      """
      Feature: Feature that spills the beans

        Scenario: This scenario prints some secrets to the logs
         Given I echo "the current user is {{USER}}"
           And I echo "{{MY_SECRET}}"
           And I echo "your home directory is at {{HOME}}"
      """
      When I run the command "cucu run {CUCU_RESULTS_DIR}/features_with_secrets --secrets MY_SECRET --results={CUCU_RESULTS_DIR}/features_with_secrets_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
      Then I should see "{EXIT_CODE}" is equal to "0"
       And I should see "{STDOUT}" does not contain "super secret"

  Scenario: User gets expected behavior when not using variable passthru
    Given I create a file at "{CUCU_RESULTS_DIR}/substeps_without_variable_passthru/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/substeps_without_variable_passthru/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu import run_steps, step

      @step('I pass the secret "{{variable}}" to a substep')
      def step_with_substeps(context, variable):
          run_steps(
              context,
              f'''
              When I echo "{{variable}}"
              ''')
      """
      And I create a file at "{CUCU_RESULTS_DIR}/substeps_without_variable_passthru/cucurc.yml" with the following:
      """
      MY_SECRET: 'super secret'
      """
      And I create a file at "{CUCU_RESULTS_DIR}/substeps_without_variable_passthru/features/feature_that_spills_the_beans.feature" with the following:
      """
      Feature: Feature that spills the beans

        Scenario: This scenario prints some secrets to the logs
          Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
           When I open a browser at the url "http://{{HOST_ADDRESS}}:{{PORT}}/buttons.html"
           Then I pass the secret "{{MY_SECRET}}" to a substep
      """
      When I run the command "cucu run {CUCU_RESULTS_DIR}/substeps_without_variable_passthru --secrets MY_SECRET --results={CUCU_RESULTS_DIR}/substeps_without_variable_passthru_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      Then I should see the file at "{CUCU_RESULTS_DIR}/substeps_without_variable_passthru_results/Feature that spills the beans/This scenario prints some secrets to the logs/3 - I echo "super secret".png"

  Scenario: User gets expected behavior when using variable_passthru=True
    Given I create a file at "{CUCU_RESULTS_DIR}/substeps_with_variable_passthru/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/substeps_with_variable_passthru/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu import run_steps, step

      @step('I pass the secret "{{variable}}" to a substep', variable_passthru=True)
      def step_with_substeps(context, variable):
          run_steps(
              context,
              f'''
              When I echo "{{variable}}"
              ''')
      """
      And I create a file at "{CUCU_RESULTS_DIR}/substeps_with_variable_passthru/cucurc.yml" with the following:
      """
      MY_SECRET: 'super secret'
      """
      And I create a file at "{CUCU_RESULTS_DIR}/substeps_with_variable_passthru/features/feature_that_spills_the_beans.feature" with the following:
      """
      Feature: Feature that spills the beans

        Scenario: This scenario prints some secrets to the logs
          Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
           When I open a browser at the url "http://{{HOST_ADDRESS}}:{{PORT}}/buttons.html"
           Then I pass the secret "{{MY_SECRET}}" to a substep
      """
      When I run the command "cucu run {CUCU_RESULTS_DIR}/substeps_with_variable_passthru --secrets MY_SECRET --results={CUCU_RESULTS_DIR}/substeps_with_variable_passthru_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      Then I should see the file at "{CUCU_RESULTS_DIR}/substeps_with_variable_passthru_results/Feature that spills the beans/This scenario prints some secrets to the logs/3 - I echo "{{MY_SECRET}}".png"

Feature: Secrets
  As a developer I want the user to have control over what secrets are printed
  in logs and which are masked.

  Scenario: User can run a test while hiding secrets using their cucurc.yml file
    Given I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/environment.py" with the following:
      """
      import cucu
      cucu.init_environment()
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/steps/__init__.py" with the following:
      """
      import cucu
      cucu.init_steps()
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
      import cucu
      cucu.init_environment()
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/steps/__init__.py" with the following:
      """
      import cucu
      cucu.init_steps()
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

@cli
Feature: Tags
  As a developer
  I want to run the tags command
  So that I can see which tags are associated with a given `cucu run`

  Scenario: User can run the tags command
    Given I run the command "cucu tags data/features/tagged_features" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      disabled
      feature1
      feature2
      feature3
      scenario1
      """

  Scenario: User can filter on the tags command
    Given I run the command "cucu tags data/features/tagged_features --filter=fea" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      feature1
      feature2
      feature3
      """
      And I should see "{STDOUT}" does not contain "scenario1"
     When I run the command "cucu tags data/features/tagged_features --filter=scen" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      scenario1
      """
      And I should see "{STDOUT}" does not contain "feature1"
      And I should see "{STDOUT}" does not contain "feature2"
      And I should see "{STDOUT}" does not contain "feature3"

  Scenario: User can use the --tags argument with the tags command
    Given I run the command "cucu tags data/features/tagged_features --tags=feature1" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      feature1
      scenario1
      """
      And I should see "{STDOUT}" does not contain "feature2"
      And I should see "{STDOUT}" does not contain "feature3"

  Scenario: User can use the --tags argument and --filter argument on the tags command at the same time
    Given I run the command "cucu tags data/features/tagged_features --tags=feature1 --filter=fea" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      feature1
      """
      And I should see "{STDOUT}" does not contain "feature2"
      And I should see "{STDOUT}" does not contain "feature3"
      And I should see "{STDOUT}" does not contain "scenario1"

  Scenario: User is issued a reasonable error after providing an invalid filter
    Given I run the command "cucu tags data/features/tagged_features --tags=feature1 --filter=nope(" and save stdout to "STDOUT" and expect exit code "5"
     Then I should see "{STDOUT}" matches the following
      """
      Invalid filter expression .*
      Aborting.*
      """

  Scenario: User can collect tags without applying redaction to them
    Given I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/steps/__init__.py" with the following:
      """
      from cucu import run_steps
      from cucu.steps import *

      @step("I use a step with substeps that has secrets")
      def step_with_substeps_that_has_secrets(context):
          run_steps(
              context,
              \"\"\"
          When I echo "\{MY_SECRET\}"
          \"\"\",
          )
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/cucurc.yml" with the following:
      """
      CUCU_SECRETS: SECRET_NUMBER
      SECRET_NUMBER: '123'
      """
      And I create a file at "{CUCU_RESULTS_DIR}/features_with_secrets/features/feature_that_tags_the_beans.feature" with the following:
      """
      Feature: Feature with a tag that would be redacted

        @tag-555123555
        Scenario: This scenario prints some secrets to the logs
         Given I echo "This is not secret"
          Then I echo "Only the tag is secret"
      """
     When I run the command "cucu tags {CUCU_RESULTS_DIR}/features_with_secrets" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" contains "tag-555123555"
      And I should see "{STDOUT}" does not contain "555***555"

Feature: Command steps
  As a developer I want the user to be able to interact with commands and their
  output

  Scenario: User can execute a command and use its output
    Given I run the command "echo -n foobar" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" is equal to "foobar"

  Scenario: User can execute an expect script
    Given I create a file at "{CUCU_RESULTS_DIR}/interactive_script.sh" with the following
      """
      #!/bin/bash
      echo "What's your name?"
      read name
      echo "What's your favorite color?"
      read color
      echo "$name likes the color $color"
      """
      And I run the command "chmod +x {CUCU_RESULTS_DIR}/interactive_script.sh" and expect exit code "0"
     When I run the following script and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      """
      #!/usr/bin/expect

      spawn {CUCU_RESULTS_DIR}/interactive_script.sh
      expect "What's your name?\r"
      send -- "Peter\r"
      expect "What's your favorite color?\r"
      send -- "purple\r"
      expect "Peter likes the color purple\r"
      """

  @regression
  Scenario: User can execute multiple scripts without any unexpected issues
    Given I create a file at "{CUCU_RESULTS_DIR}/multiple_script_calls/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/multiple_script_calls/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/multiple_script_calls/multiple_script_steps.feature" with the following:
      """
      Feature: Feature with script steps

        Scenario: Scenario with multiple script calls
          Given I run the following script and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
            \"\"\"
            ls
            \"\"\"
            And I run the following script and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
            \"\"\"
            ls
            \"\"\"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/multiple_script_calls/multiple_script_steps.feature --results {CUCU_RESULTS_DIR}/multiple_script_calls_results/" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" does not contain the following:
      """
      FileNotFoundError: [Errno 2] No such file or directory:
      """
      And I should see "{STDERR}" does not contain the following:
      """
      FileNotFoundError: [Errno 2] No such file or directory:
      """

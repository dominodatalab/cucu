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

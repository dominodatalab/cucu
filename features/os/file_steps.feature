Feature: File steps
  As a developer I want the user to be able to interact with files on the
  filesystem

  Scenario: User can create a new file and verify its contents
    Given I create a file at "{CUCU_RESULTS_DIR}/create_file_test.txt" with the following
      """
      foobar
      """
     Then I should see the file at "{CUCU_RESULTS_DIR}/create_file_test.txt" is equal to the following
      """
      foobar
      """

  Scenario: User can create a new file and verify it contains specific pattern
    Given I create a file at "{CUCU_RESULTS_DIR}/create_file_pattern_test.txt" with the following
      """
      start
      id: 1234567890abcdef1234567890abcdef
      end
      """
     Then I should see the file at "{CUCU_RESULTS_DIR}/create_file_pattern_test.txt" contains the following pattern
      """
      id: [0-9a-f]\{32\}
      """

  Scenario: User can create a new file and read the contents to a variable
    Given I create a file at "{CUCU_RESULTS_DIR}/create_file_test.txt" with the following
      """
      foobar
      """
     When I read the contents of the file at "{CUCU_RESULTS_DIR}/create_file_test.txt" and save to the variable "DATA"
     Then I should see "{DATA}" is equal to the following
      """
      foobar
      """

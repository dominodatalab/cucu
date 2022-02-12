Feature: File steps
  As a developer I want the user to be able to interact with files on the
  filesystem

  Scenario: User can create a new file and verify its contents
    Given I create a file at "{CUCU_RESULTS_DIR}/create_file_test.txt" with the following
      """
      foobar
      """
     Then I should see the file at "{CUCU_RESULTS_DIR}/create_file_test.txt" has the following
      """
      foobar
      """

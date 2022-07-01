Feature: Feature with skipping scenarios by file presence

  Scenario: That runs only when ./skip_first_scenario.txt does not exist
    Given I skip this scenario if the file at "./skip_first_scenario.txt" exists
     Then I echo "The first scenario ran!"

  Scenario: That runs only when ./skip_second_scenario.txt does not exist
    Given I skip this scenario if the file at "./skip_second_scenario.txt" exists
     Then I echo "The second scenario ran!"

Feature: Feature with skipping scenarios by file presence

  Scenario: That runs only when {TMPDIR}/skip_first_scenario.txt does not exist
    Given I skip this scenario if the file at "{TMPDIR}/skip_first_scenario.txt" exists
     Then I echo "The first scenario ran!"

  Scenario: That runs only when {TMPDIR}/skip_second_scenario.txt does not exist
    Given I skip this scenario if the file at "{TMPDIR}/skip_second_scenario.txt" exists
     Then I echo "The second scenario ran!"

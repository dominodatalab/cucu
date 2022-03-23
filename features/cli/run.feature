Feature: Run
  As a developer I want the user to

  Scenario: User gets an error when running an inexistent feature file
    Given I run the command "cucu run data/features/inexistent.feature --results {CUCU_RESULTS_DIR}/inexistent-results" and save stdout to "STDOUT", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
      And I should see "{STDOUT}" is equal to the following
      """
      FileNotFoundError: data/features/inexistent.feature

      """

  Scenario: User can get the versino of the currently running cucu command
    Given I run the command "cucu --version" and save stdout to "STDOUT", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" matches the following
      """
      cucu, version \d+.\d+.\d+
      """

  Scenario: User gets expected output when running steps with substeps
    Given I run the command "cucu run data/features/scenario_with_substeps.feature --results {CUCU_RESULTS_DIR}/substeps-results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature with substeps

        Scenario: Scenario that uses a step with substeps
            ⤷ When I do nothing             .*
            ⤷  And I do nothing             .*
            ⤷  And I do nothing             .*
          Given I use a step with substeps  .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

  Scenario: User gets expected non zero exit code when a scenario fails
    Given I run the command "cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/failing-scenario-results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with failing scenario

        Scenario: Just a scenario that fails
          Given I fail .*s
      Traceback \(most recent call last\):
      [\s\S]*
      RuntimeError: step fails on purpose
      [\s\S]*
      Failing scenarios:
        data/features/feature_with_failing_scenario.feature:3  Just a scenario that fails
      [\s\S]*
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 1 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is equal to the following
      """
      Error: test run failed, see above for details

      """

  Scenario: User can run a scenario with background which uses a step with substeps
    Given I run the command "cucu run data/features/feature_with_background_using_substeps.feature --results {CUCU_RESULTS_DIR}/background-with-substeps-results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with background using substeps

        Scenario: Scenario which now has a background using a step with substeps
      first line of the background

          Given I echo "first line of the background"               #  in .*
            ⤷ When I open a browser at the url "https://www.google.com/search"  #  in .*
            ⤷  And I wait to write "define: kittens" into the input "Search"    #  in .*
            ⤷  And I click the button "Google Search"                           #  in .*
            And I search for "define: kittens" on google search                 #  in .*
      This is from the scenario

           When I echo "This is from the scenario"                              #  in .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

  Scenario: User can run a passing scenario and generate a report
    Given I run the command "cucu run data/features/feature_with_passing_scenario.feature --results {CUCU_RESULTS_DIR}/run_with_report_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_report_report" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I start a webserver on port "40000" at directory "{CUCU_RESULTS_DIR}/run_with_report_report/"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/index.html"
     Then I should see the link "Feature: Feature with passing scenario"
     When I click the link "Feature: Feature with passing scenario"
     Then I should see the link "Scenario: Just a scenario that passes"

  Scenario: User can run a failing scenario and generate a report
    Given I run the command "cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/run_with_report_results --generate-report --report {CUCU_RESULTS_DIR}/run_with_report_report" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
     When I start a webserver on port "40000" at directory "{CUCU_RESULTS_DIR}/run_with_report_report/"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/index.html"
     Then I should see the link "Feature: Feature with failing scenario"
     When I click the link "Feature: Feature with failing scenario"
     Then I should see the link "Scenario: Just a scenario that fails"

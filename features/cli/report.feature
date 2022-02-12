Feature: Report
  As a developer I want the user to be able to generate reports from tests runs

  Scenario: User can run a basic non UI test and get an HTML test report
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/non-ui-results" and save stdout to "STDOUT", stderr to "STDERR" and exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I run the command "cucu report {CUCU_RESULTS_DIR}/non-ui-results --output {CUCU_RESULTS_DIR}/non-ui-report" and save stdout to "STDOUT", stderr to "STDERR" and exit code to "EXIT_CODE" 
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I start a webserver on port "40000" at directory "{CUCU_RESULTS_DIR}/non-ui-report/"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/index.html"
     Then I should see the link "Feature: Echo"
     When I click the link "Feature: Echo"
     Then I should see the link "Scenario: Echo an environment variable"
     When I click the link "Scenario: Echo an environment variable"
     Then I should see the text "I echo \"current shell is '{{SHELL}}'\""

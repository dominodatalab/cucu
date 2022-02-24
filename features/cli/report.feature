# unclear of what is going on here but in circleci when shutting down the
# webserver things get stuck... I'll have to debug but not now
@disabled
Feature: Report
  As a developer I want the user to be able to generate reports from tests runs

  Scenario: User can run a basic non browser test and create a report
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/non-browser-results" and save exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I run the command "cucu report {CUCU_RESULTS_DIR}/non-browser-results --output {CUCU_RESULTS_DIR}/non-browser-report" and save exit code to "EXIT_CODE" 
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I start a webserver on port "40000" at directory "{CUCU_RESULTS_DIR}/non-browser-report/"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/index.html"
     Then I should see the link "Feature: Echo"
     When I click the link "Feature: Echo"
     Then I should see the link "Scenario: Echo an environment variable"
     When I click the link "Scenario: Echo an environment variable"
     Then I should see the text "I echo \"current shell is '{{SHELL}}'\""

  Scenario: User can run a basic browser test and create a report
    Given I run the command "cucu run data/features/google_kitten_search.feature --results {CUCU_RESULTS_DIR}/browser-results" and save exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I run the command "cucu report {CUCU_RESULTS_DIR}/browser-results --output {CUCU_RESULTS_DIR}/browser-report" and save exit code to "EXIT_CODE" 
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I start a webserver on port "40000" at directory "{CUCU_RESULTS_DIR}/browser-report/"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/index.html"
     Then I should see the link "Feature: Google kitten search"
     When I click the link "Feature: Google kitten search"
     Then I should see the link "Scenario: Search for kittens on www.google.com"
     When I click the link "Scenario: Search for kittens on www.google.com"
     Then I should see the text "And I wait to write \"define: kittens\" into the input \"Search\""

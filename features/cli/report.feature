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

  Scenario: User can run a multi scenario test with web steps and generate a valid report
    Given I run the command "cucu run data/features/multiple_scenarios_with_browser_steps.feature --results {CUCU_RESULTS_DIR}/multi-scenario-browser-results" and save exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I run the command "cucu report {CUCU_RESULTS_DIR}/multi-scenario-browser-results --output {CUCU_RESULTS_DIR}/multi-scenario-browser-report" and save exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I start a webserver on port "40000" at directory "{CUCU_RESULTS_DIR}/multi-scenario-browser-report/"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/index.html"
     Then I click the link "Feature: Multiple scenarios with browser steps"
     When I click the link "Scenario: Search for cat on www.google.com"
     Then I should not see the image with the alt text "Given I search for \"define: dog\" on google search"
      And I should see the image with the alt text "When I open a browser at the url \"https://www.google.com/search\""
      And I should see the image with the alt text "And I wait to write \"define: cat\" into the input \"Search\""
      And I should see the image with the alt text "And I click the button \"Google Search\""
      And I should see the image with the alt text "Then I should see the text \"/kat/\""
     When I click the link "Top"
      And I click the link "Feature: Multiple scenarios with browser steps"
      And I click the link "Scenario: Search for dog on www.google.com"
     Then I should not see the image with the alt text "Given I search for \"define: dog\" on google search"
      And I should see the image with the alt text "When I open a browser at the url \"https://www.google.com/search\""
      And I should see the image with the alt text "And I wait to write \"define: dog\" into the input \"Search\""
      And I should see the image with the alt text "And I click the button \"Google Search\""
      And I should see the image with the alt text "Then I should see the text \"/dôɡ/\""

  Scenario: User can run a scenario with console logs and see those logs linked in the report
    Given I run the command "cucu run data/features/scenario_with_console_logs.feature --results {CUCU_RESULTS_DIR}/console-log-reporting" and save stdout to "STDOUT", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I run the command "cucu report {CUCU_RESULTS_DIR}/console-log-reporting --output {CUCU_RESULTS_DIR}/console-log-reporting-report" and save exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I start a webserver on port "40000" at directory "{CUCU_RESULTS_DIR}/console-log-reporting-report/"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/index.html"
      And I click the link "Feature: Feature with console logs"
      And I click the button "Scenario: Scenario with console logs"
      And I click the button "Logs"
     Then I should see the button "browser_console.log"
     When I click the button "browser_console.log" 
     Then I should see the text "this is a regular log"
      And I should see the text "this is an error log"
      And I should see the text "this is a debug log"
      And I should see the text "this is a warn log"

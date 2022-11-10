@report
Feature: Report basics
  As a developer I want the user to be able to generate reports from tests runs
  in the most basic of situations

  Scenario: User can run a basic non browser test and create a report
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/non-browser-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/non-browser-results --output {CUCU_RESULTS_DIR}/non-browser-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/non-browser-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see the link "Echo"
     When I click the link "Echo"
     Then I should see the link "Echo an environment variable"
     When I click the link "Echo an environment variable"
     Then I should see the text "I echo \"current shell is '\{SHELL\}'\""

  Scenario: User can run a basic browser test and create a report
    Given I run the command "cucu run data/features/feature_with_passing_scenario_with_web.feature --results {CUCU_RESULTS_DIR}/browser-results --env CUCU_BROKEN_IMAGES_PAGE_CHECK=disabled" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/browser-results --output {CUCU_RESULTS_DIR}/browser-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/browser-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I wait to click the link "Feature with passing scenario with web"
     When I wait to click the link "Just a scenario that opens a web page"
     Then I wait to see the button "Given I start a webserver at directory "data/www" and save the port to the variable "PORT""
      And I should see the button "And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/buttons.html""
     When I run the command "ls "{SCENARIO_RESULTS_DIR}/"" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      [\s\S]*\.png
      [\s\S]*
      """

  @QE-6852
  Scenario: User can run a multi scenario test with web steps and generate report with a shareable url
    Given I run the command "cucu run data/features/multiple_scenarios_with_browser_steps.feature --env CUCU_BROKEN_IMAGES_PAGE_CHECK=disabled --results {CUCU_RESULTS_DIR}/multi-scenario-browser-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/multi-scenario-browser-results --output {CUCU_RESULTS_DIR}/multi-scenario-browser-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/multi-scenario-browser-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Multiple scenarios with browser steps"
      And I click the link "Open our test checkboxes page"
      And I should not see the image with the alt text "Given I start a webserver at directory "data/www" and save the port to the variable "PORT""
      And I should not see the image with the alt text "And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/checkboxes.html""
      And I should not see the image with the alt text "Then I should see the checkbox "checkbox with inner label""
     Then I click the button "Then I should see the checkbox "checkbox with inner label""
      And I should see the image with the alt text "Then I should see the checkbox "checkbox with inner label""
      And I should not see the image with the alt text "Given I start a webserver at directory "data/www" and save the port to the variable "PORT""
      And I should not see the image with the alt text "And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/checkboxes.html""
     When I save the current url to the variable "CURRENT_URL"
      And I click the link "Index"
     Then I navigate to the url "{CURRENT_URL}"
      And I wait to see the image with the alt text "Then I should see the checkbox "checkbox with inner label""
      And I should not see the image with the alt text "Given I start a webserver at directory "data/www" and save the port to the variable "PORT""
      And I should not see the image with the alt text "And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/checkboxes.html""

  Scenario: User can run a feature with mixed results and has all results reported correctly
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --results {CUCU_RESULTS_DIR}/mixed-results" and expect exit code "1"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/mixed-results --output {CUCU_RESULTS_DIR}/mixed-results-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/mixed-results-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see a table that matches the following:
       | Feature                    | Total | Passed | Failed | Skipped | Status | Duration |
       | Feature with mixed results | 5     | 2      | 2      | 1       | failed | .*       |
     When I click the button "Feature with mixed results"
     Then I should see a table that matches the following:
      | Scenario                            | Total Steps | Status  | Duration |
      | Scenario that fails                 | 2           | failed  | .*       |
      | Scenario that has an undefined step | 1           | failed  | .*       |
      | Scenario that passes                | 1           | passed  | .*       |
      | Scenario that also passes           | 1           | passed  | .*       |
      | Scenario that is skipped            | 1           | skipped | .*       |
      And I click the button "Scenario that fails"
     Then I should see the text "RuntimeError: step fails on purpose"
     When I click the button "Index"
      And I click the button "Feature with mixed results"
      And I click the button "Scenario that has an undefined step"
     Then I should see the button "Given I attempt to use an undefined step"

  @workaround @QE-7075
  @disabled
  Scenario: User can run a scenario with console logs and see those logs linked in the report
    Given I skip this scenario if the current browser is not "chrome"
     When I run the command "cucu run data/features/scenario_with_console_logs.feature --results {CUCU_RESULTS_DIR}/console-log-reporting" and save stdout to "STDOUT" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/console-log-reporting --output {CUCU_RESULTS_DIR}/console-log-reporting-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/console-log-reporting-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I click the link "Feature with console logs"
      And I click the button "Scenario with console logs"
      And I click the button "Logs"
     Then I should see the button "browser_console.log"
     When I click the button "browser_console.log"
     Then I wait to see the text "this is a regular log"
      And I should see the text "this is an error log"
      And I should see the text "this is a debug log"
      And I should see the text "this is a warn log"

  Scenario: User can run a scenario without debug logging on the console but still found the cucu.debug.log in the report
    Given I run the command "cucu run  data/features/feature_with_passing_scenario_with_web.feature --results {CUCU_RESULTS_DIR}/cucu_debug_results --generate-report --report {CUCU_RESULTS_DIR}/cucu_debug_report" and save stdout to "STDOUT" and expect exit code "0"
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/cucu_debug_report" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I click the link "Feature with passing scenario with web"
     Then I should not see the text "DEBUG executing page check \"wait for document.readyState\""
      And I should not see the text "DEBUG executing page check \"broken image checker\""
      And I click the button "Just a scenario that opens a web page"
     When I click the button "Logs"
      And I click the button "cucu.debug.console.log"
     Then I wait to see the text "DEBUG executing page check \"wait for document.readyState\""
      And I wait to see the text "DEBUG executing page check \"broken image checker\""

  Scenario: User can run a scenario with tags and see them in the test report
    Given I run the command "cucu run data/features/feature_with_tagging.feature --results {CUCU_RESULTS_DIR}/report_with_tags_results --generate-report --report {CUCU_RESULTS_DIR}/report_with_tags_report" and save stdout to "STDOUT" and expect exit code "0"
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/report_with_tags_report" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I wait to click the link "Feature with tagging"
     Then I wait to see the text "@all"
     When I click the link "Scenario that is tagged with @second"
     Then I wait to see the text "@second"
      And I should not see the text "@all"
      And I should not see the text "@first"

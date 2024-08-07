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
     Then I wait to see the button "Given I start a webserver at directory \"data/www\" and save the port to the variable \"PORT\""
      And I should see the button "And I open a browser at the url \"http://\{HOST_ADDRESS\}:\{PORT\}/buttons.html\""
     When I run the command "ls "{SCENARIO_RESULTS_DIR}/"" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      (\d\d\d\d - [\s\S]*)
      [\s\S]*
      """

  Scenario: User can run a test and see extended output
    Given I run the command "cucu run data/features/with_secret/scenario_with_comments.feature --results {CUCU_RESULTS_DIR}/browser-results --env CUCU_BROKEN_IMAGES_PAGE_CHECK=disabled" and expect exit code "1"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/browser-results --output {CUCU_RESULTS_DIR}/browser-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/browser-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/flat.html"
      And I wait to click the link "Scenario with comments"

        * # Can see inline comments
     Then I wait to see the text "# First comment"
      And I should see the text "# Second comment"
      And I should see the text "# Comment about \{MY_SECRET\}"

        * # Can see variable interpolation
      And I wait to see the text "# FOO=\"bar\""

        * # Cannot see secrets in variable interpolation
      And I wait to see the text "# MY_SECRET="****""

        * # Can see image for step with secret in name
     When I click the button "I should see the text "\{MY_SECRET\}""
     Then I should see the image with the alt text "After I should see the text MY_SECRET"

        * # Cannot see secrets in the exception message
     When I click the button "Then I click the button "\{MY_SECRET\}""
     Then I should see the text "unable to find the button "****""

  @QE-6852
  Scenario: User can run a multi scenario test with web steps and generate report with a shareable url
    Given I run the command "cucu run data/features/multiple_scenarios_with_browser_steps.feature --env CUCU_BROKEN_IMAGES_PAGE_CHECK=disabled --results {CUCU_RESULTS_DIR}/multi-scenario-browser-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/multi-scenario-browser-results --output {CUCU_RESULTS_DIR}/multi-scenario-browser-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/multi-scenario-browser-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"

     # Verify HTML report
     When I click the link "Multiple scenarios with browser steps"
      And I click the link "Open our test checkboxes page"
      And I should not see the image with the alt text "After I start a webserver at directory \"data/www\" and save the port to the variable \"PORT\""
      And I should not see the image with the alt text "After I open a browser at the url \"http://{HOST_ADDRESS}:{PORT}/checkboxes.html\""
      And I should not see the image with the alt text "After I should see the checkbox \"checkbox with inner label\""
     Then I click the button "Then I should see the checkbox \"checkbox with inner label\""
      And I should see the image with the alt text "After I should see the checkbox checkbox with inner label"
      And I should not see the image with the alt text "After I start a webserver at directory \"data/www\" and save the port to the variable \"PORT\""
      And I should not see the image with the alt text "After I open a browser at the url \"http://{HOST_ADDRESS}:{PORT}/checkboxes.html""
     When I save the current url to the variable "CURRENT_URL"
      And I click the link "Index"
     Then I navigate to the url "{CURRENT_URL}"
      And I wait to see the image with the alt text "After I should see the checkbox checkbox with inner label"
      And I should not see the image with the alt text "After I start a webserver at directory \"data/www\" and save the port to the variable \"PORT\""
      And I should not see the image with the alt text "After I open a browser at the url \"http://{HOST_ADDRESS}:{PORT}/checkboxes.html\""

  Scenario: User can run a feature with mixed results and has all results reported correctly without skips
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --results {CUCU_RESULTS_DIR}/mixed-results" and expect exit code "1"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/mixed-results --output {CUCU_RESULTS_DIR}/mixed-results-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/mixed-results-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see a table that matches the following:
       | Started at | Feature                    | Total | Passed | Failed | Skipped | Errored | Status | Duration |
       | .*         | Feature with mixed results | 6     | 3      | 3      | 0       | 0       | failed | .*       |
     When I click the button "Feature with mixed results"
     Then I should see a table that matches the following:
      | Offset | Scenario                            | Steps | Status  | Duration |
      | .*     | Scenario and after-hook both fail   | 3     | failed  | .*       |
      | .*     | Scenario that also passes           | 1     | passed  | .*       |
      | .*     | Scenario that fails                 | 2     | failed  | .*       |
      | .*     | Scenario that has an undefined step | 1     | failed  | .*       |
      | .*     | Scenario that passes                | 1     | passed  | .*       |
      | .*     | Scenario with after-hook error      | 2     | passed  | .*       |
      And I click the button "Scenario that fails"
     Then I should see the text "RuntimeError: step fails on purpose"
     When I click the button "Index"
      And I click the button "Feature with mixed results"
      And I click the button "Scenario that has an undefined step"
     Then I should see the button "Given I attempt to use an undefined step"

  @show-skips
  Scenario: User can run a feature with mixed results and has all results reported correctly
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --show-skips --results {CUCU_RESULTS_DIR}/mixed-results" and expect exit code "1"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/mixed-results --show-skips --output {CUCU_RESULTS_DIR}/mixed-results-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/mixed-results-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see a table that matches the following:
       | Started at | Feature                    | Total | Passed | Failed | Skipped | Errored | Status | Duration |
       | .*         | Feature with mixed results | 7     | 3      | 3      | 1       | 0       | failed | .*       |
     When I click the button "Feature with mixed results"
     Then I should see a table that matches the following:
      | Offset | Scenario                            | Steps | Status  | Duration |
      | .*     | Scenario and after-hook both fail   | 3     | failed  | .*       |
      | .*     | Scenario that also passes           | 1     | passed  | .*       |
      | .*     | Scenario that fails                 | 2     | failed  | .*       |
      | .*     | Scenario that has an undefined step | 1     | failed  | .*       |
      | .*     | Scenario that is skipped            | 1     | skipped | .*       |
      | .*     | Scenario that passes                | 1     | passed  | .*       |
      | .*     | Scenario with after-hook error      | 2     | passed  | .*       |

      And I click the button "Scenario that fails"
     Then I should see the text "RuntimeError: step fails on purpose"
     When I click the button "Index"
      And I click the button "Feature with mixed results"
      And I click the button "Scenario that has an undefined step"
     Then I should see the button "Given I attempt to use an undefined step"

  Scenario: User can run feature with background and has all results reported correctly without skips
    Given I run the command "cucu run data/features/feature_with_background.feature --results {CUCU_RESULTS_DIR}/feature_with_background" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/feature_with_background --output {CUCU_RESULTS_DIR}/feature_with_background-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/feature_with_background-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see a table that matches the following:
       | Started at | Feature                    | Total | Passed | Failed | Skipped | Errored | Status | Duration |
       | .*         | Feature with background    | 1     | 1      | 0      | 0       | 0       | passed | .*       |
     When I click the button "Feature with background"
     Then I should see a table that matches the following:
      | Offset | Scenario                            | Steps | Status  | Duration |
      | .*     | Scenario which now has a background | 2     | passed  | .*       |

  @show-skips
  Scenario: User can run feature with background and has all results reported correctly
    Given I run the command "cucu run data/features/feature_with_background.feature --show-skips --results {CUCU_RESULTS_DIR}/feature_with_background" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/feature_with_background --show-skips --output {CUCU_RESULTS_DIR}/feature_with_background-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/feature_with_background-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see a table that matches the following:
       | Started at | Feature                    | Total | Passed | Failed | Skipped | Errored | Status | Duration |
       | .*         | Feature with background    | 2     | 1      | 0      | 1       | 0       | passed | .*       |
     When I click the button "Feature with background"
     Then I should see a table that matches the following:
      | Offset | Scenario                            | Steps | Status  | Duration |
      | .*     | Scenario that is skipped            | 2     | skipped | .*       |
      | .*     | Scenario which now has a background | 2     | passed  | .*       |

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
     Then I should see the button "browser_console.log.txt"
     When I click the button "browser_console.log.txt"
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
      And I should see the text "@all"
      And I should not see the text "@first"

  @runtime-timeout
  Scenario: User can run with a runtime timeout and still produce a valid report
    Given I run the command "cucu run data/features/slow_features --runtime-timeout 9 --results {CUCU_RESULTS_DIR}/runtime_timeout_reporting_results" and expect exit code "1"
     Then I should see the previous step took less than "13" seconds
     When I run the command "cucu report {CUCU_RESULTS_DIR}/runtime_timeout_reporting_results --output {CUCU_RESULTS_DIR}/runtime_timeout_reporting_report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/runtime_timeout_reporting_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the button "Slow feature #1"
     Then I should see a table that matches the following:
      | Offset | Scenario      | Steps | Status | Duration |
      | .*     | Slow scenario | 1     | .*     |    >*    |
     When I go back on the browser
      And I click the button "Slow feature #2"
     Then I should see a table that matches the following:
      | Offset | Scenario      | Steps | Status | Duration |
      | .*     | Slow scenario | 1     | .*     |    >*    |

  Scenario: User can run results without skips in the HTML test report
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --results {CUCU_RESULTS_DIR}/report_without_skips --generate-report --report {CUCU_RESULTS_DIR}/report_without_skips_report" and expect exit code "1"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/report_without_skips_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see a table that matches the following:
      | Started at | Feature                    | Total | Passed | Failed | Skipped | Errored | Status | Duration |
      | .*         | Feature with mixed results | 6     | 3      | 3      | 0       | 0       | failed | .*       |
     When I click the button "Feature with mixed results"
     Then I should see a table that matches the following:
      | Offset | Scenario                            | Steps | Status  | Duration |
      | .*     | Scenario and after-hook both fail   | 3     | failed  | .*       |
      | .*     | Scenario that also passes           | 1     | passed  | .*       |
      | .*     | Scenario that fails                 | 2     | failed  | .*       |
      | .*     | Scenario that has an undefined step | 1     | failed  | .*       |
      | .*     | Scenario that passes                | 1     | passed  | .*       |
      | .*     | Scenario with after-hook error      | 2     | passed  | .*       |
      And I click the button "Scenario that fails"
     Then I should see the text "RuntimeError: step fails on purpose"
     When I click the button "Index"
      And I click the button "Feature with mixed results"
      And I click the button "Scenario that has an undefined step"
     Then I should see the button "Given I attempt to use an undefined step"

  Scenario: User can run results without skips in the HTML test report on a feature with background
    Given I run the command "cucu run data/features/feature_with_background.feature --results {CUCU_RESULTS_DIR}/report_without_skips_background --generate-report --report {CUCU_RESULTS_DIR}/report_without_skips_background_report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/report_without_skips_background_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see a table that matches the following:
      | Started at | Feature                 | Total | Passed | Failed | Skipped | Errored | Status | Duration |
      | .*         | Feature with background | 1     | 1      | 0      | 0       | 0       | passed | .*       |
     When I click the button "Feature with background"
     Then I should see a table that matches the following:
      | Offset | Scenario                            | Steps | Status  | Duration |
      | .*     | Scenario which now has a background | 2     | passed  | .*       |

  Scenario: User can run results without skips in the JUnit results
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --results {CUCU_RESULTS_DIR}/junit_without_skips" and expect exit code "1"
      And I read the contents of the file at "{CUCU_RESULTS_DIR}/junit_without_skips/Feature with mixed results.xml" and save to the variable "JUNIT"
     Then I should see "{JUNIT}" contains "skipped=\"0\""
      And I should see "{JUNIT}" does not contain "<skipped>"

  Scenario: User can run results without skips in the JUnit results when feature has background
    Given I run the command "cucu run data/features/feature_with_background.feature --results {CUCU_RESULTS_DIR}/junit_without_skips_background" and expect exit code "0"
      And I read the contents of the file at "{CUCU_RESULTS_DIR}/junit_without_skips_background/Feature with background.xml" and save to the variable "JUNIT"
     Then I should see "{JUNIT}" contains "skipped=\"0\""
      And I should see "{JUNIT}" does not contain "<skipped>"

  Scenario: User can run and generate reports from empty feature files
    Given I create a file at "{CUCU_RESULTS_DIR}/empty_features/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/empty_features/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/empty_features/blank_feature.feature" with the following:
      """
      """
      And I create a file at "{CUCU_RESULTS_DIR}/empty_features/no_scenario_feature.feature" with the following:
      """
      Feature: nothing to see here
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/empty_features --results {CUCU_RESULTS_DIR}/empty_features_results --generate-report --report {CUCU_RESULTS_DIR}/empty_features_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/empty_features_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see the text "No data available in table"

  Scenario: User can run and generate reports that perform highlighting
    Given I create a file at "{CUCU_RESULTS_DIR}/highlights/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/highlights/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I create a file at "{CUCU_RESULTS_DIR}/highlights/text.feature" with the following:
      """
      Feature: run a test with highlighting

        Scenario: See text that should be highlit
           When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
           Then I should see the text "just some text in a label"
      """
      And I run the command "cucu run {CUCU_RESULTS_DIR}/highlights --results {CUCU_RESULTS_DIR}/empty_features_results --env CUCU_SKIP_HIGHLIGHT_BORDER='False' --generate-report --report {CUCU_RESULTS_DIR}/highlights_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"

  @report-only-failures
  Scenario: User can generate a report with only failures
    Given I run the command "cucu run data/features --tags @passing,@failing --report-only-failures --results {CUCU_RESULTS_DIR}/report_only_failures --generate-report --report {CUCU_RESULTS_DIR}/report_only_failures_report" and expect exit code "1"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/report_only_failures_report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see a table that matches the following:
       | Started at | Feature                                | Total | Passed | Failed | Skipped | Errored | Status | Duration |
       | .*         | Feature with failing scenario          | 1     | 0      | 1      | 0       | 0       | failed | .*       |
       | .*         | Feature with failing to find a table   | 1     | 0      | 1      | 0       | 0       | failed | .*       |
       | .*         | Feature with failing scenario with web | 1     | 0      | 1      | 0       | 0       | failed | .*       |
     When I click the button "Feature with failing scenario with web"
     Then I should see a table that matches the following:
       | Offset | Scenario                              | Steps | Status | Duration |
       | .*     | Just a scenario that opens a web page | 3     | failed | .*       |
     When I click the button "Just a scenario that opens a web page"
      And I wait to click the button "show images"
      And I should see the image with the alt text "After I should see the text inexistent"

  Scenario: User can run a basic test and create a report with the report path in JUnit
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/junit-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/junit-results --output {CUCU_RESULTS_DIR}/junit-report --junit {CUCU_RESULTS_DIR}/junit-results" and expect exit code "0"
      And I should see the file at "{CUCU_RESULTS_DIR}/junit-results/Echo.xml" contains the following
      """
      report_path="results/junit-report/Echo/Echo an environment variable/index.html"
      """

  Scenario: User can run a basic test with report option and have the report path in JUnit
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/junit-generate-results --generate-report --report {CUCU_RESULTS_DIR}/junit-generate-report" and expect exit code "0"
      And I should see the file at "{CUCU_RESULTS_DIR}/junit-generate-results/Echo.xml" contains the following
      """
      report_path="results/junit-generate-report/Echo/Echo an environment variable/index.html"
      """

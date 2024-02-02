@report
Feature: Report search and sorting
  As a developer I want the user to be able to generate reports from tests runs
  and use the search and sorting features as expected

  Scenario: User can sort by various fields in the HTML test report
    Given I run the command "cucu run data/features/tagged_features --tags @feature2 --show-skips --results {CUCU_RESULTS_DIR}/sorting-in-reports-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/sorting-in-reports-results --show-skips --output {CUCU_RESULTS_DIR}/sorting-in-reports-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/sorting-in-reports-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I wait to see a table that matches the following:
       | Started at | Feature               | Total | Passed | Failed | Skipped | Errored | Status  | Duration |
       | .*         | First tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |
       | .*         | Second tagged feature | 1     | 1      | 0      | 0       | 0       | passed  | .*       |
       | .*         | Third tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |

  Scenario: User can sort by various fields in the HTML test report and share the exact state via the URL
    Given I run the command "cucu run data/features/tagged_features --tags @feature2 --show-skips --results {CUCU_RESULTS_DIR}/sorting-in-reports-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/sorting-in-reports-results --show-skips --output {CUCU_RESULTS_DIR}/sorting-in-reports-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/sorting-in-reports-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I wait to see a table that matches the following:
       | Started at | Feature               | Total | Passed | Failed | Skipped | Errored | Status  | Duration |
       | .*         | First tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |
       | .*         | Second tagged feature | 1     | 1      | 0      | 0       | 0       | passed  | .*       |
       | .*         | Third tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |
      And I click the table header "Status"
      And I wait to see a table that matches the following:
       | Started at | Feature               | Total | Passed | Failed | Skipped | Errored | Status  | Duration |
       | .*         | Second tagged feature | 1     | 1      | 0      | 0       | 0       | passed  | .*       |
       | .*         | First tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |
       | .*         | Third tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |
      And I save the current url to the variable "CURRENT_URL"
      And I refresh the browser
     Then I wait to see a table that matches the following:
       | Started at | Feature               | Total | Passed | Failed | Skipped | Errored | Status  | Duration |
       | .*         | Second tagged feature | 1     | 1      | 0      | 0       | 0       | passed  | .*       |
       | .*         | First tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |
       | .*         | Third tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |

  Scenario: User can search by various fields in the HTML test report
    Given I run the command "cucu run data/features/tagged_features --tags @feature2 --show-skips --results {CUCU_RESULTS_DIR}/searching-in-reports-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/searching-in-reports-results --show-skips --output {CUCU_RESULTS_DIR}/searching-in-reports-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/searching-in-reports-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I write "passed" into the input "Search:"
     Then I wait to see a table that matches the following:
       | Started at | Feature               | Total | Passed | Failed | Skipped | Errored | Status  | Duration |
       | .*         | Second tagged feature | 1     | 1      | 0      | 0       | 0       | passed  | .*       |
     When I write "skipped" into the input "Search:"
     Then I wait to see a table that matches the following:
       | Started at | Feature               | Total | Passed | Failed | Skipped | Errored | Status  | Duration |
       | .*         | First tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |
       | .*         | Third tagged feature  | 1     | 0      | 0      | 1       | 0       | skipped | .*       |

  Scenario: User can search by various fields in the HTML test report and share the exact state via the URL
    Given I run the command "cucu run data/features/tagged_features --tags @feature2 --results {CUCU_RESULTS_DIR}/searching-in-reports-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/searching-in-reports-results --output {CUCU_RESULTS_DIR}/searching-in-reports-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/searching-in-reports-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I write "passed" into the input "Search:"
     Then I wait to see a table that matches the following:
       | Started at | Feature               | Total | Passed | Failed | Skipped | Errored | Status  | Duration |
       | .*         | Second tagged feature | 1     | 1      | 0      | 0       | 0       | passed  | .*       |
     When I save the current url to the variable "CURRENT_URL"
      And I refresh the browser
     Then I wait to see a table that matches the following:
       | Started at | Feature               | Total | Passed | Failed | Skipped | Errored | Status  | Duration |
       | .*         | Second tagged feature | 1     | 1      | 0      | 0       | 0       | passed  | .*       |

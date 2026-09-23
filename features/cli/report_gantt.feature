@report
Feature: Report Gantt view
  As a developer I want to see every scenario in a run on a Gantt chart of
  wall-clock timespans, colored by outcome, with links to the scenario report

  Scenario: User can open the Gantt chart from the report index and follow a bar
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --results {CUCU_RESULTS_DIR}/gantt-mixed-results" and expect exit code "1"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/gantt-mixed-results --output {CUCU_RESULTS_DIR}/gantt-mixed-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/gantt-mixed-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I should see the link "Gantt"
     When I click the link "Gantt"
     Then I should see the text "Gantt HTML Test Report"
      And I should see the text "Scenario that passes"
      And I should see the text "Scenario that fails"
      And I should see the text "Scenario with after-hook error"
      And I should see the link "Index"
     When I click the link "Scenario that fails"
     Then I wait to see the button "I fail"
      And I should see the text "Scenario HTML Test Report"

@report
Feature: Report replay view
  As a developer I want the user to be able to view individual scenario reports
  in a replay timeline format for a more visual step-by-step experience

  Scenario: Replay view shows step text and navigation for a non-browser scenario
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/replay-echo-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-echo-results --output {CUCU_RESULTS_DIR}/replay-echo-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-echo-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Echo"
      And I click the link "Echo an environment variable"
      And I click the link "🔁 Replay"
     Then I wait to see the link "☑ Classic"

        * # Feature and scenario names shown in the header
      And I should see the text "Echo an environment variable"
      And I should see the text "Echo"

        * # Stage shows step text for non-browser tests
      And I should see the text "I echo the following"
      And I execute in the current browser the following javascript and save the result to the variable "STEP_COUNTER"
        """
        return document.getElementById('step-count').textContent.trim();
        """
      And I should see "{STEP_COUNTER}" is equal to "1 / 6"

        * # Step counter updates when navigating to the last step
     When I click the button "⏭"
     Then I wait to see the text "good bye {{USER}}"
      And I execute in the current browser the following javascript and save the result to the variable "STEP_COUNTER"
        """
        return document.getElementById('step-count').textContent.trim();
        """
      And I should see "{STEP_COUNTER}" is equal to "6 / 6"

        * # Return to the classic scenario view from the replay view
     When I click the link "☑ Classic"
     Then I wait to see the link "🔁 Replay"

  Scenario: Replay view auto-focuses the first failing step in a failed scenario
    Given I run the command "cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/replay-fail-results" and expect exit code "1"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-fail-results --output {CUCU_RESULTS_DIR}/replay-fail-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-fail-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Feature with failing scenario"
      And I click the link "Just a scenario that fails"
      And I click the link "🔁 Replay"
     Then I wait to see the link "☑ Classic"
      And I should see the text "failed"
      And I execute in the current browser the following javascript and save the result to the variable "STEP_COUNTER"
        """
        return document.getElementById('step-count').textContent.trim();
        """
      And I should see "{STEP_COUNTER}" is equal to "1 / 1"

  Scenario: Replay view renders correctly for a scenario with substeps
    Given I run the command "cucu run data/features/scenario_with_substeps.feature --results {CUCU_RESULTS_DIR}/replay-substeps-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-substeps-results --output {CUCU_RESULTS_DIR}/replay-substeps-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-substeps-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Feature with substeps"
      And I click the link "Scenario that uses a step with substeps"
      And I click the link "🔁 Replay"
     Then I wait to see the link "☑ Classic"
      And I should see the text "passed"
      And I execute in the current browser the following javascript and save the result to the variable "STEP_CUR"
        """
        return document.getElementById('step-cur').textContent.trim();
        """
      And I should see "{STEP_CUR}" is equal to "1"

  Scenario: Replay view renders screenshots for a browser scenario
    Given I run the command "cucu run data/features/feature_with_passing_scenario_with_web.feature --results {CUCU_RESULTS_DIR}/replay-browser-results --env CUCU_BROKEN_IMAGES_PAGE_CHECK=disabled" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-browser-results --output {CUCU_RESULTS_DIR}/replay-browser-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-browser-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I wait to click the link "Feature with passing scenario with web"
      And I wait to click the link "Just a scenario that opens a web page"
      And I wait to click the link "🔁 Replay"
     Then I wait to see the link "☑ Classic"
      And I should see the link "Flat"
      And I should see the link "Index"
      And I execute in the current browser the following javascript and save the result to the variable "STEP_CUR"
        """
        return document.getElementById('step-cur').textContent.trim();
        """
      And I should see "{STEP_CUR}" is equal to "1"

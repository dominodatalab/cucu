Feature: Download MHT archives
  As a user of web-based testing
  I want to download MHT archives
  So that I can bebug DOM-based failures more easily

  Scenario: Download an MHT file during a test
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/files.html"
     When I download an mht archive of the current page to "{SCENARIO_DOWNLOADS_DIR}/test_archive_{SCENARIO_RUN_ID}.mht"
     Then I should see a file at "{SCENARIO_DOWNLOADS_DIR}/test_archive_{SCENARIO_RUN_ID}.mht"

  Scenario: Download an MHT file automatically on Scenario failure
    Given I create a file at "{CUCU_RESULTS_DIR}/mht/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/mht/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I create a file at "{CUCU_RESULTS_DIR}/mht/fail.feature" with the following:
      """
      Feature: Download MHT on failure

        Scenario: Open a browser and then fail
           When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
           Then I should see "4" is equal to "5"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/mht/fail.feature --results {CUCU_RESULTS_DIR}/mht_results/ -l debug" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     Then I should see a file at "{CUCU_RESULTS_DIR}/mht_results/Download MHT on failure/Open a browser and then fail/logs/Open a browser and then fail_browser0.mht"

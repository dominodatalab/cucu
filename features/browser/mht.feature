Feature: Download MHT archives
  As a user of web-based testing
  I want to download MHT archives
  So that I can debug DOM-based failures more easily

  Scenario: Download an MHT file during a test
    Given I skip this scenario if the current browser is not "chrome"
      And I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/files.html"
     When I download an mht archive of the current page to "{SCENARIO_DOWNLOADS_DIR}/test_archive_{SCENARIO_RUN_ID}.mht"
     Then I should see a file at "{SCENARIO_DOWNLOADS_DIR}/test_archive_{SCENARIO_RUN_ID}.mht"

  Scenario: Download an MHT file automatically on Scenario failure
    Given I skip this scenario if the current browser is not "chrome"
      And I create a file at "{CUCU_RESULTS_DIR}/mht/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/mht/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I create a file at "{CUCU_RESULTS_DIR}/mht/one_browser.feature" with the following:
      """
      Feature: Download MHT automatically

        Scenario: Open a browser
           When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
           Then I should see the browser title is "Buttons!"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/mht/one_browser.feature --results {CUCU_RESULTS_DIR}/mht_results/ -l debug" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see a file at "{CUCU_RESULTS_DIR}/mht_results/Download MHT automatically/Open a browser/logs/browser_snapshot.mht"

  Scenario: Download multiple MHT files automatically on Scenario failure for every browser used
    Given I skip this scenario if the current browser is not "chrome"
      And I create a file at "{CUCU_RESULTS_DIR}/mht/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/mht/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I create a file at "{CUCU_RESULTS_DIR}/mht/two_browsers.feature" with the following:
      """
      Feature: Download MHT automatically

        Scenario: Open two browsers
           When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"
            And I should see the browser title is "Buttons!"
            # Open a second browser
            And I open a new browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
           Then I should see the browser title is "Inputs!"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/mht/two_browsers.feature --results {CUCU_RESULTS_DIR}/mht_results/ -l debug" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see a file at "{CUCU_RESULTS_DIR}/mht_results/Download MHT automatically/Open two browsers/logs/browser0_snapshot.mht"
      And I should see a file at "{CUCU_RESULTS_DIR}/mht_results/Download MHT automatically/Open two browsers/logs/browser1_snapshot.mht"

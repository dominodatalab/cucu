Feature: Page checks
  As a developer I want to make sure that our built in page checks report errors
  accordingly

  Scenario: User will get an error from the readyState page checker if the page never finishes loading
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     Then I expect the following step to fail with "document.readyState is in "loading""
      """
      When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/page_that_loads_forever.html"
      """
      And I should see the previous step took more than "10" seconds

  Scenario: User will get an error from the broken image page checker if there are broken images
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     Then I expect the following step to fail with "broken images were found on the page"
      """
      When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/broken_images.html"
      """

  Scenario: User can disable built in page checks
    Given I run the command "cucu run data/features/feature_with_passing_scenario_with_web.feature --logging-level debug --results {CUCU_RESULTS_DIR}/disabling_page_checks_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" contains the following
      """
      executing page check "wait for document.readyState"
      """
      And I should see "{STDOUT}" contains the following
      """
      executing page check "broken image checker"
      """
     When I run the command "cucu run data/features/feature_with_passing_scenario_with_web.feature --env CUCU_READY_STATE_PAGE_CHECK=false --logging-level debug --results {CUCU_RESULTS_DIR}/disabling_page_checks_results" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" does not contain the following
      """
      executing page check "wait for document.readyState"
      """
      And I should see "{STDOUT}" contains the following
      """
      executing page check "broken image checker"
      """

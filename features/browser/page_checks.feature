Feature: Page checks
  As a developer I want to make sure that our built in page checks report errors
  accordingly

  @wip
  Scenario: User will get an error from the readyState page checker if the page never finishes loading
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I set the variable "CUCU_STEP_WAIT_TIMEOUT_S" to "5"
     Then I expect the following step to fail with "document.readyState is in "loading""
      """
      When I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/page_that_loads_forever.html"
      """
      And I should see the previous step took more than "5" seconds

  Scenario: User will get an error from the broken image page checker if there are broken images
    Given I create a file at "{CUCU_RESULTS_DIR}/broken_image_checker/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/broken_image_checker/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/broken_image_checker/broken_images.feature.feature" with the following:
      """
      Feature: Feature loads page with broken images

        Scenario: That loads a page with broken images
          Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/broken_images.html"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/broken_image_checker/broken_images.feature.feature --results {CUCU_RESULTS_DIR}/broken_image_checker_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" contains the following:
      """
      WARNING broken image found: <img src="broken_image.jpg" alt="Broken Image">
      """
      And I should see "{STDOUT}" does not contain the following:
      """
      WARNING broken image found: <img src="broken_image.jpg" alt="Aria Hidden Broken Image" aria-hidden="true">
      """

  Scenario: User can disable built in page checks
    Given I run the command "cucu run data/features/feature_with_passing_scenario_with_web.feature --logging-level debug --results {CUCU_RESULTS_DIR}/disabling_page_checks_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      .* executing page check "wait for document.readyState"
      [\s\S]*
      .* executing page check "broken image checker"
      [\s\S]*
      """
     When I run the command "cucu run data/features/feature_with_passing_scenario_with_web.feature --env CUCU_READY_STATE_PAGE_CHECK=false --logging-level debug --results {CUCU_RESULTS_DIR}/disabling_page_checks_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      .* executing page check "wait for document.readyState"
      .* document.readyState check disabled
      [\s\S]*
      .* executing page check "broken image checker"
      [\s\S]*
      """

  Scenario: User can disable the broken image checker at runtime
    Given I start a webserver at directory "data/www/" and save the port to the variable "PORT"
      And I set the variable "CUCU_BROKEN_IMAGES_PAGE_CHECK" to "disabled"
     Then I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/broken_images.html"

  Scenario: User gets expected order on page checks due to order of insertion
    Given I create a file at "{CUCU_RESULTS_DIR}/ordered_page_checks/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import register_page_check_hook

      def wait_for_my_own_page_check(_):
        pass

      register_page_check_hook("my own page check", wait_for_my_own_page_check)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/ordered_page_checks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/ordered_page_checks/just_a_feature.feature" with the following:
      """
      Feature: Just a feature

        Scenario: That opens a web page
          Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/buttons.html"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/ordered_page_checks/just_a_feature.feature --results {CUCU_RESULTS_DIR}/ordered_page_checks_results -l debug" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" matches the following:
      """
      [\s\S]*
      .* DEBUG executing page check "wait for document.readyState"
      .* DEBUG executed page check "wait for document.readyState" in .*
      .* DEBUG executing page check "broken image checker"
      .* DEBUG executed page check "broken image checker" in .*
      .* DEBUG executing page check "my own page check"
      .* DEBUG executed page check "my own page check" in .*
      [\s\S]*
      """

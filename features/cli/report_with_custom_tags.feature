@report
Feature: Report with custom tags
  As a developer I want the user to be able to generate reports that contain
  custom tag handling

  Scenario: User can register a custom tag handler for reporting
    Given I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_tag_handling/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_tag_handling/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu import register_custom_tags_in_report_handling

      def link_to_something(tag):
          term = tag.replace("@link(", "").replace(")", "")
          return f'<a href="https://\{term\}">\{tag\}</a>'

      register_custom_tags_in_report_handling("@link\(.*\)", link_to_something)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_tag_handling/feature_with_custom_tag_handling.feature" with the following:
      """
      @link(google.com)
      Feature: Feature with custom tag handling

        @link(images.google.com)
        Scenario: Scenario with a custom tag handler
          Given I echo "nothing to see here"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/report_with_custom_tag_handling --results {CUCU_RESULTS_DIR}/custom_tag_handling_results --generate-report --report {CUCU_RESULTS_DIR}/custom_tag_handling_report" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/custom_tag_handling_report" and save the port to the variable "PORT"
      And I set the variable "CUCU_BROKEN_IMAGES_PAGE_CHECK" to "disabled"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I wait to click the link "Feature with custom tag handling"
      And I wait to click the link "@link(google.com)"
     Then I wait to see the current url is "google.com"
     When I go back on the browser
      And I wait to see the link "@link(google.com)"
      And I click the link "Scenario with a custom tag handler"
      And I wait to click the link "@link(images.google.com)"
     Then I wait to see the current url is "images.google.com"

  Scenario: User can register a custom tag handler for reporting and use "cucu report" after the run
    Given I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_tag_handling/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_tag_handling/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      from cucu import register_custom_tags_in_report_handling

      def link_to_something(tag):
          term = tag.replace("@link(", "").replace(")", "")
          return f'<a href="https://\{term\}">\{tag\}</a>'

      register_custom_tags_in_report_handling("@link\(.*\)", link_to_something)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/report_with_custom_tag_handling/feature_with_custom_tag_handling.feature" with the following:
      """
      @link(google.com)
      Feature: Feature with custom tag handling

        @link(images.google.com)
        Scenario: Scenario with a custom tag handler
          Given I echo "nothing to see here"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/report_with_custom_tag_handling --results {CUCU_RESULTS_DIR}/custom_tag_handling_results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/custom_tag_handling_results --output {CUCU_RESULTS_DIR}/custom_tag_handling_report" and expect exit code "0"
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/custom_tag_handling_report" and save the port to the variable "PORT"
      And I set the variable "CUCU_BROKEN_IMAGES_PAGE_CHECK" to "disabled"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I wait to click the link "Feature with custom tag handling"
      And I wait to click the link "@link(google.com)"
     Then I wait to see the current url is "google.com"
     When I go back on the browser
      And I wait to see the link "@link(google.com)"
      And I click the link "Scenario with a custom tag handler"
      And I wait to click the link "@link(images.google.com)"
     Then I wait to see the current url is "images.google.com"

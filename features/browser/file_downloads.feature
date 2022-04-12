Feature: File downloads
  As a developer I want to make sure the test writer can download files and
  verify when they're completely downloaded.

  Scenario: User can download a file through the browser
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I delete the file at "{CUCU_BROWSER_DOWNLOADS_PATH}/file.txt" if it exists
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/files.html"
     When I click the link "download this file"
     Then I wait to see the file at "{SCENARIO_DOWNLOADS_DIR}/file.txt"

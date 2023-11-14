Feature: File downloads
  As a developer I want to make sure the test writer can download files and
  verify when they're completely downloaded.

  Scenario: User can download a file through the browser
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/files.html"
     When I click the link "download this file"
     Then I wait to see the downloaded file "file.txt"
      And I wait to see a file at "{SCENARIO_DOWNLOADS_DIR}/file.txt"

  @disabled @QE-10005
  Scenario: User can download a file through the browser even when frames are involved
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/files.html"
     When I click the link "download this file"

     # Should still work even if brower is currently pointed to subframe
      And I click the button "button"

     Then I wait to see the downloaded file "file.txt"
      And I wait to see a file at "{SCENARIO_DOWNLOADS_DIR}/file.txt"

  Scenario: User can download a file through the browser as a regex filename and save the resulting filename
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/files.html"
     When I click the link "download this unique file"
      And I wait to see the downloaded filename matching the regex "file_\d+\.txt" and save the filename to the variable "FILE_NAME"
      And I wait to see a file at "{SCENARIO_DOWNLOADS_DIR}/{FILE_NAME}"

Feature: File upload
  As a developer I want to make sure the test writer can upload files to a
  web application

  Scenario: User can upload a file
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/files.html"
     When I upload the file "features/browser/file_upload.feature" to the file input "upload some files:"
      And I click the button "upload!"
      And I save the current url to the variable "URL"
     Then I should see "{URL}" matches ".*\?filename=file_upload.feature"

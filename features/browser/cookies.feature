Feature: Cookies
  As a developer I want to make sure the test writer can interact with the cookies on a page

  Background: HTML page with cookies
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"

  Scenario: User can retrieve the cookies on a page
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/cookies.html"
     When I save the browser cookie "username" to the variable "USERNAME"
      And I save the browser cookie "token" to the variable "TOKEN"
     Then I should see "{USERNAME}" is equal to "JohnDoe"
      And I should see "{TOKEN}" is equal to "xyz"

  Scenario: User can set the cookies on a page
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/cookies.html"
     When I set the browser cookie "new_cookie" a value of "snickerdoodle"
     Then I save the browser cookie "new_cookie" to the variable "NEW_COOKIE"
      And I should see "{NEW_COOKIE}" is equal to "snickerdoodle"

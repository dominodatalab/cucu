@passing
Feature: Feature with passing scenario with web

  Scenario: Just a scenario that opens a web page
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"

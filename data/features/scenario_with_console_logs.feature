Feature: Feature with console logs

  Scenario: Scenario with console logs
    Given I start a webserver on port "40000" at directory "data/www"
     When I open a browser at the url "http://{HOST_ADDRESS}:40000/console_logging.html"
  
  Scenario: Scenario without console logs
    Given I start a webserver on port "40000" at directory "data/www"
     When I open a browser at the url "http://{HOST_ADDRESS}:40000/buttons.html"

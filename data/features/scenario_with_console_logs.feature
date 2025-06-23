Feature: Feature with console logs

  Scenario: Scenario with console logs
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     Then I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/console_logging.html"
      And I should see the text "Console Logging!"

  Scenario: Scenario without console logs
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     Then I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html"

  Scenario: Scenario logging tab information to cucu console logs
    Given I set the variable "CUCU_LOG_TAB_INFO_TO_CONSOLE" to "true"
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
     Then I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/console_logging.html"
      And I should see the text "Console Logging!"   

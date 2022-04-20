Feature: Screenshot
  As a developer I want to make sure that I get screenshots from browser steps

  Background: HTML page with text
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"

  Scenario: User can see screenshot was generated
     Then I should see the file at "{CUCU_LAST_SCREENSHOT_PNG}"

  Scenario: User can see monitor screenshot was generated
     When I set the variable "CUCU_MONITOR_PNG" to ".monitor.png"
      And I delete the file at "{CUCU_MONITOR_PNG}" if it exists
      And I should see the text "just some text in a label"
     Then I should see the file at "{CUCU_MONITOR_PNG}"

Feature: Screenshot
  As a developer I want to make sure that I get screenshots from browser steps

  Scenario: User can see monitor screenshot was generated
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/text.html"
     When I set the variable "CUCU_MONITOR_PNG" to ".monitor.png"
      And I delete the file at "{CUCU_MONITOR_PNG}" if it exists
      And I should see the text "just some text in a label"
     Then I should see a file at "{CUCU_MONITOR_PNG}"

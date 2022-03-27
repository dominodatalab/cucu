Feature: Feature with failing scenario with web

  Scenario: Just a scenario that opens a web page
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/buttons.html"
      And I should see the text "inexistent"

Feature: Browser management
  As a developer I want to make sure the test writer can interact with different
  browser windows and open and close them as necessary

  Scenario: User can open multiple browsers and close them
    Given I start a webserver on port "40000" at directory "data/www"
     When I open a browser at the url "http://{HOST_ADDRESS}:40000/buttons.html"
     Then I should see the browser title is "Buttons!"
     When I open a new browser at the url "http://{HOST_ADDRESS}:40000/inputs.html"
     Then I should see the browser title is "Inputs!"
     When I close the current browser 
     Then I should see the browser title is "Buttons!"

  Scenario: User can open multiple browsers and switch between them
    Given I start a webserver on port "40000" at directory "data/www"
     When I open a browser at the url "http://{HOST_ADDRESS}:40000/buttons.html"
     Then I should see the browser title is "Buttons!"
     When I open a new browser at the url "http://{HOST_ADDRESS}:40000/inputs.html"
     Then I should see the browser title is "Inputs!"
     When I switch to the previous browser
     Then I should see the browser title is "Buttons!"
     When I switch to the next browser
     Then I should see the browser title is "Inputs!"

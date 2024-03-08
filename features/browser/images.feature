Feature: Images
  As a developer I want the test writer to be able to verify images on screen

  Scenario: User can verify the state of images on screen
    Given I run the command "cucu run data/features/multiple_scenarios_with_browser_steps.feature --env CUCU_BROKEN_IMAGES_PAGE_CHECK=disabled --results {CUCU_RESULTS_DIR}/multi-scenario-browser-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/multi-scenario-browser-results --output {CUCU_RESULTS_DIR}/multi-scenario-browser-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/multi-scenario-browser-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Multiple scenarios with browser steps"
      And I click the link "Open our test buttons page"
     Then I should not see the image with the alt text "After I start a webserver at directory "data/www" and save the port to the variable "PORT""
      And I should not see the image with the alt text "After I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html""
      And I should not see the image with the alt text "After I should see the button "button with child""
     When I click the button "I should see the button "button with child""
     Then I should not see the image with the alt text "After I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html""
      And I should not see the image with the alt text "After I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/buttons.html""
      And I should see the image with the alt text "After I should see the button button with child"

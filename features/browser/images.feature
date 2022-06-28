Feature: Images
  As a developer I want the test writer to be able to verify images on screen

  Scenario: User can verify the state of images on screen
    Given I run the command "cucu run data/features/multiple_scenarios_with_browser_steps.feature --env CUCU_BROKEN_IMAGES_PAGE_CHECK=disabled --results {CUCU_RESULTS_DIR}/scenario-with-images-results" and save exit code to "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/scenario-with-images-results --output {CUCU_RESULTS_DIR}/scenario-with-images-report" and save exit code to "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/scenario-with-images-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     Then I click the link "Multiple scenarios with browser steps"
     When I click the link "Search for cat on www.google.com"
     Then I should not see the image with the alt text "Given I search for \"define: dog\" on google search"
      And I should not see the image with the alt text "When I open a browser at the url \"https://www.google.com/search\""
      And I should not see the image with the alt text "And I wait to write \"define: cat\" into the input \"Search\""
      And I should not see the image with the alt text "And I click the button \"Google Search\""
      And I should not see the image with the alt text "Then I should see the text \"Cat\""
     When I click the button "And I wait to write \"define: cat\" into the input \"Search\""
     Then I should see the image with the alt text "And I wait to write \"define: cat\" into the input \"Search\""

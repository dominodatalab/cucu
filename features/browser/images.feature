Feature: Images
  As a developer I want the test writer to be able to verify images on screen

  Scenario: User can verify the state of images on screen
    Given I run the command "cucu run data/features/multiple_scenarios_with_browser_steps.feature --results {CUCU_RESULTS_DIR}/scenario-with-images-results" and save exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I run the command "cucu report {CUCU_RESULTS_DIR}/scenario-with-images-results --output {CUCU_RESULTS_DIR}/scenario-with-images-report" and save exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
     When I start a webserver on port "40000" at directory "{CUCU_RESULTS_DIR}/scenario-with-images-report/"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/index.html"
     Then I click the link "Feature: Multiple scenarios with browser steps"
     When I click the link "Scenario: Search for cat on www.google.com"
     Then I should not see the image with the alt text "Given I search for \"define: dog\" on google search"
      And I should not see the image with the alt text "When I open a browser at the url \"https://www.google.com/search\""
      And I should not see the image with the alt text "And I wait to write \"define: cat\" into the input \"Search\""
      And I should not see the image with the alt text "And I click the button \"Google Search\""
      And I should not see the image with the alt text "Then I should see the text \"Cat\""
     When I click the button "And I wait to write \"define: cat\" into the input \"Search\""
     Then I should see the image with the alt text "And I wait to write \"define: cat\" into the input \"Search\""

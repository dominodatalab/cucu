Feature: Inputs Limits
  As a developer I want to make sure that inputs can be interacted with while
  pushing the limits of what the browser and framework can handle.

  Scenario: User can write a large text into an input
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      # create a file with 4KB
      And I run the following script and expect exit code "0":
      """
      yes "" | tr "\n" "X" | dd of={CUCU_RESULTS_DIR}/input_data.txt bs=1024 count=4
      """
      And I read the contents of the file at "{CUCU_RESULTS_DIR}/input_data.txt" and save to the variable "DATA"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I should see no value in the input "input type=text"
     When I write "{DATA}" into the input "input type=text"
     Then I should see the previous step took less than "1" seconds
      And I should see "input type=text was modified" in the input "last touched input"
      And I should see "{DATA}" in the input "input type=text"

  Scenario: User can write a large text into a textarea
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      # create a file with 4KB
      And I run the following script and expect exit code "0":
      """
      yes "" | tr "\n" "X" | dd of={CUCU_RESULTS_DIR}/input_data.txt bs=1024 count=4
      """
      And I read the contents of the file at "{CUCU_RESULTS_DIR}/input_data.txt" and save to the variable "DATA"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/inputs.html"
     Then I should see no value in the input "textarea with label"
     When I write "{DATA}" into the input "textarea with label"
     Then I should see the previous step took less than "1" seconds
      And I should see "textarea with label was modified" in the input "last touched input"

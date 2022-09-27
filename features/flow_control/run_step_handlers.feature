Feature: Run step handlers
  As a developer I want the test writers to be able to reliably run before/after
  step handlers which can handle non deterministic actions

  Scenario: User can use after step handler to take actions at this point in the test execution
    Given I create a file at "{CUCU_RESULTS_DIR}/after_step_handlers/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/after_step_handlers/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/after_step_handlers/feature_with_after_step_handlers.feature" with the following:
      """
      Feature: Feature with scenarios using after step handlers

        Scenario: Scenario with an after step handler
          Given I create the after step handler "click that button" with the following steps
            \"\"\"
            When I click the button "buttons! in a new tab"
            \"\"\"
            And I start a webserver at directory "data/www" and save the port to the variable "PORT"
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/links.html"
            # somewhere here the "click that button" handler will kick in and open the other tab
           When I wait to switch to the next browser tab
           Then I should see the browser title is "Buttons!"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/after_step_handlers --results {CUCU_RESULTS_DIR}/after_step_handlers_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with scenarios using after step handlers

        Scenario: Scenario with an after step handler
          Given I create the after step handler "click that button" with the following steps .*
              \"\"\"
              When I click the button "buttons! in a new tab"
              \"\"\"
            And I start a webserver at directory "data/www" and save the port to the variable "PORT" .*
      .* INFO after step handler "click that button" ran successfully
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/links.html" .*
            [\s\S]*
           When I wait to switch to the next browser tab .*
           Then I should see the browser title is "Buttons!" .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      5 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

  Scenario: User can use before step handler to take actions at this point in the test execution
    Given I create a file at "{CUCU_RESULTS_DIR}/before_step_handlers/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/before_step_handlers/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/before_step_handlers/feature_with_before_step_handlers.feature" with the following:
      """
      Feature: Feature with scenarios using before step handlers

        Scenario: Scenario with an before step handler
          Given I create the before step handler "click that button" with the following steps
            \"\"\"
            When I click the button "buttons! in a new tab"
            \"\"\"
            And I start a webserver at directory "data/www" and save the port to the variable "PORT"
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/links.html"
            # somewhere here the "click that button" handler will kick in and open the other tab
           When I wait to switch to the next browser tab
           Then I should see the browser title is "Buttons!"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/before_step_handlers --results {CUCU_RESULTS_DIR}/before_step_handlers_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with scenarios using before step handlers

        Scenario: Scenario with an before step handler
          Given I create the before step handler "click that button" with the following steps .*
              \"\"\"
              When I click the button "buttons! in a new tab"
              \"\"\"
            And I start a webserver at directory "data/www" and save the port to the variable "PORT" .*
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/links.html" .*
            [\s\S]*
      .* INFO before step handler "click that button" ran successfully
           When I wait to switch to the next browser tab .*
           Then I should see the browser title is "Buttons!" .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      5 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

  Scenario: User can use before retry handler to take actions at this point in the test execution
    Given I create a file at "{CUCU_RESULTS_DIR}/before_retry_handlers/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/before_retry_handlers/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/before_retry_handlers/feature_with_before_retry_handlers.feature" with the following:
      """
      Feature: Feature with scenarios using before retry handlers

        Scenario: Scenario with an before retry handler
          Given I create the before retry handler "click that button" with the following steps
            \"\"\"
            When I click the button "buttons!"
            \"\"\"
            And I start a webserver at directory "data/www" and save the port to the variable "PORT"
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/links.html"
            # the before retry handler will be the one to click and switch to the next tab
           Then I wait to see the button "button with child"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/before_retry_handlers --results {CUCU_RESULTS_DIR}/before_retry_handlers_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with scenarios using before retry handlers

        Scenario: Scenario with an before retry handler
          Given I create the before retry handler "click that button" with the following steps .*
              \"\"\"
              When I click the button "buttons!"
              \"\"\"
            And I start a webserver at directory "data/www" and save the port to the variable "PORT" .*
      .* INFO before retry handler "click that button" ran successfully
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/links.html" .*
            [\s\S]*
           Then I wait to see the button "button with child" .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

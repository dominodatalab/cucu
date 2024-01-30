Feature: Before retry handlers
  As a developer I want the test writers to be able to run before retry handler
  code which can handle non-deterministic behavior of the underlying web
  application under test.

  Scenario: User can use before retry handler handle unexpected UI elements
    Given I create a file at "{CUCU_RESULTS_DIR}/before_retry_handlers/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import logger, register_before_retry_hook, run_steps
      from cucu.steps import button_steps

      def handle_the_button(ctx):
        if ctx.browser:
          button = button_steps.find_button(ctx, "buttons!")
          if button:
            button_steps.click_button(ctx, button)
            logger.info("handled the pesky button buttons!")

      register_before_retry_hook(handle_the_button)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/before_retry_handlers/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/before_retry_handlers/feature_with_before_retry_handlers.feature" with the following:
      """
      Feature: Feature with scenarios using before retry handlers

        Scenario: Scenario with an before retry handler
          Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/links.html"
            # the before retry handler will be the one to click and switch to the next tab
           Then I wait to see the button "button with child"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/before_retry_handlers --results {CUCU_RESULTS_DIR}/before_retry_handlers_results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with scenarios using before retry handlers

        Scenario: Scenario with an before retry handler
          Given I start a webserver at directory "data/www" and save the port to the variable "PORT" .*
            And I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/links.html" .*
            [\s\S]*
      .* INFO handled the pesky button buttons!
           Then I wait to see the button "button with child" .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

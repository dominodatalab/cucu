Feature: Run with hoks
  As a developer I want the user to be able to register various hooks and see
  them run at the expected times

  Scenario: User can run a simple scenario and launch their own feature, scenario and step hooks
    Given I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import logger, register_before_scenario_hook, register_after_scenario_hook, register_after_step_hook, register_before_step_hook, register_after_step_hook

      def before_scenario_log(ctx):
          logger.debug("just logging some stuff from my before scenario hook")

      def after_scenario_log(ctx):
          logger.debug("just logging some stuff from my after scenario hook")

      register_before_scenario_hook(before_scenario_log)
      register_after_scenario_hook(after_scenario_log)

      def before_step_log(ctx):
          logger.debug("just logging some stuff from my before step hook")

      def after_step_log(ctx):
          logger.debug("just logging some stuff from my after step hook")


      register_before_step_hook(before_step_log)
      register_after_step_hook(after_step_log)

      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/echo.feature" with the following:
      """
      Feature: Feature that simply echo's "Hello World"

        Scenario: This is a scenario that simply echo's hello world
          Given I echo "Hello"
            And I echo "World"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/custom_hooks/echo.feature --results {CUCU_RESULTS_DIR}/custom_hooks_results/ -l debug" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature that simply echo's "Hello World"
      .* DEBUG just logging some stuff from my before scenario hook

        Scenario: This is a scenario that simply echo's hello world
      .* DEBUG just logging some stuff from my before step hook
      Hello

      .* DEBUG just logging some stuff from my after step hook
          Given I echo "Hello"     #  in .*
      .* DEBUG just logging some stuff from my before step hook
      World

      .* DEBUG just logging some stuff from my after step hook
            And I echo "World"     #  in .*
      .* DEBUG just logging some stuff from my after scenario hook

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

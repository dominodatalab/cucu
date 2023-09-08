Feature: Run with hooks
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
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/custom_hooks/echo.feature --results {CUCU_RESULTS_DIR}/custom_hooks_results/ -l debug --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature that simply echo's "Hello World"
      .* DEBUG just logging some stuff from my before scenario hook

        Scenario: This is a scenario that simply echo's hello world
      .* DEBUG just logging some stuff from my before step hook
      Hello

      .* DEBUG just logging some stuff from my after step hook
          Given I echo "Hello"     # .*
      .* DEBUG just logging some stuff from my before step hook
      World

      .* DEBUG just logging some stuff from my after step hook
            And I echo "World"     # .*
      .* DEBUG No browsers - skipping MHT webpage snapshot
      .* DEBUG just logging some stuff from my after scenario hook

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty
  @current
  Scenario: User can run after this scenario hook and verify hooks are executed in LIFO order
    Given I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import logger, step, register_after_this_scenario_hook

      @step("I run the following steps after the current scenario-1")
      def after_scenario_log(ctx):
        def after_this_scenario_1(ctx):
            logger.debug("just logging some stuff from first_after_this_scenario_hook_1")

        register_after_this_scenario_hook(after_this_scenario_1)

      @step("I run the following steps after the current scenario-2")
      def after_scenario_log(ctx):
        def after_this_scenario_2(ctx):
            logger.debug("just logging some stuff from second_after_this_scenario_hook_2")

        register_after_this_scenario_hook(after_this_scenario_2)

      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/echo.feature" with the following:
      """
      Feature: Feature that runs after this scenario hooks in LIFO order.

        Scenario: This is a scenario that runs after this scenario hooks in LIFO order
          Given I run the following steps after the current scenario-1
            And I run the following steps after the current scenario-2
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/custom_hooks/echo.feature --results {CUCU_RESULTS_DIR}/custom_hooks_results/ -l debug --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature that runs after this scenario hooks in LIFO order.

        Scenario: This is a scenario that runs after this scenario hooks in LIFO order
          Given I run the following steps after the current scenario-1     # .*
            And I run the following steps after the current scenario-2     # .*
      .* DEBUG No browsers - skipping MHT webpage snapshot
      .* DEBUG just logging some stuff from second_after_this_scenario_hook_2
      .* DEBUG just logging some stuff from first_after_this_scenario_hook_1

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

  Scenario: User gets expected output when running a scenario with failing after hooks
    Given I create a file at "{CUCU_RESULTS_DIR}/failing_custom_hooks/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import register_after_scenario_hook

      def after_scenario_fail(ctx):
        raise RuntimeError("boom")

      register_after_scenario_hook(after_scenario_fail)

      """
      And I create a file at "{CUCU_RESULTS_DIR}/failing_custom_hooks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/failing_custom_hooks/echo.feature" with the following:
      """
      Feature: Feature that fails due to after scenario hook

        Scenario: Hello world scenario
          Given I echo "Hello World"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/failing_custom_hooks/echo.feature --results {CUCU_RESULTS_DIR}/failing_custom_hooks_results/ --generate-report --report {CUCU_RESULTS_DIR}/failing_custom_hooks_report/" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     Then I should see "{STDOUT}" contains the following
      """
      HOOK-ERROR in after_scenario: RuntimeError: boom
      """
      And I should see "{STDOUT}" contains the following
      """
      raise RuntimeError("boom")
      """
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/failing_custom_hooks_report" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I click the link "Feature that fails due to after scenario hook"
      And I click the link "Hello world scenario"
     Then I should see the text "HOOK-ERROR in after_scenario: RuntimeError: boom"

Feature: Run with hooks
  As a developer I want the user to be able to register various hooks and see
  them run at the expected times

  Scenario: User can run a simple scenario and launch their own feature, scenario and step hooks
    Given I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import logger, register_before_all_hook, register_after_all_hook, register_before_scenario_hook, register_after_scenario_hook, register_after_step_hook, register_before_step_hook, register_after_step_hook

      def before_all_log(ctx):
          logger.debug("just logging some stuff from my before all hook")

      def after_all_log(ctx):
          logger.debug("just logging some stuff from my after all hook")

      register_before_all_hook(before_all_log)
      register_after_all_hook(after_all_log)

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
      .* DEBUG just logging some stuff from my before all hook
      Feature: Feature that simply echo's "Hello World"
      .* DEBUG just logging some stuff from my before scenario hook
      .* DEBUG HOOK before_scenario_log: passed ✅

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
      .* DEBUG HOOK download_mht_data: passed ✅
      .* DEBUG just logging some stuff from my after scenario hook
      .* DEBUG HOOK after_scenario_log: passed ✅
      .* DEBUG HOOK download_browser_logs: passed ✅

      .* DEBUG just logging some stuff from my after all hook
      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      2 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

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
      .* DEBUG HOOK download_mht_data: passed ✅
      .* DEBUG just logging some stuff from second_after_this_scenario_hook_2
      .* DEBUG HOOK after_this_scenario_2: passed ✅
      .* DEBUG just logging some stuff from first_after_this_scenario_hook_1
      .* DEBUG HOOK after_this_scenario_1: passed ✅
      .* DEBUG HOOK download_browser_logs: passed ✅

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
     When I run the command "cucu run {CUCU_RESULTS_DIR}/failing_custom_hooks/echo.feature --results {CUCU_RESULTS_DIR}/failing_custom_hooks_results/ -l debug --no-color-output --generate-report --report {CUCU_RESULTS_DIR}/failing_custom_hooks_report/" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" contains the following
      """
      HOOK-ERROR in after_scenario_fail: RuntimeError: boom
      """
      And I should see "{STDOUT}" contains the following
      """
      raise RuntimeError("boom")
      """
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/failing_custom_hooks_report" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I click the link "Feature that fails due to after scenario hook"
      And I click the link "Hello world scenario"
     Then I should see the text "Hello World"

  Scenario: User gets expected output when running a scenario with failing before hooks
    Given I create a file at "{CUCU_RESULTS_DIR}/failing_before_hooks/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import register_before_scenario_hook

      def before_scenario_fail(ctx):
        raise RuntimeError("boom")

      register_before_scenario_hook(before_scenario_fail)

      """
      And I create a file at "{CUCU_RESULTS_DIR}/failing_before_hooks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/failing_before_hooks/echo.feature" with the following:
      """
      Feature: Feature that fails due to before scenario hook

        Scenario: Hello world scenario
          Given I echo "Hello World"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/failing_before_hooks/echo.feature --results {CUCU_RESULTS_DIR}/failing_before_hooks_results/ --generate-report --report {CUCU_RESULTS_DIR}/failing_before_hooks_report/" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     Then I should see "{STDOUT}" contains the following
      """
      HOOK-ERROR in before_scenario_fail: RuntimeError: boom
      """
      And I should see "{STDOUT}" contains the following
      """
      raise RuntimeError("boom")
      """

  Scenario: User gets expected output when running a scenario with multiple after hooks failing and passing in order
    Given I create a file at "{CUCU_RESULTS_DIR}/mixed_results_fail_pass_hooks/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import logger, register_after_scenario_hook

      def after_scenario_pass(ctx):
        logger.debug("This hook should execute and pass")

      register_after_scenario_hook(after_scenario_pass)

      def after_scenario_fail(ctx):
        raise RuntimeError("boom")

      register_after_scenario_hook(after_scenario_fail)

      """
      And I create a file at "{CUCU_RESULTS_DIR}/mixed_results_fail_pass_hooks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/mixed_results_fail_pass_hooks/echo.feature" with the following:
      """
      Feature: Feature that has failing and passing after scenario hooks

        Scenario: Hello world scenario
          Given I echo "Hello World"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/mixed_results_fail_pass_hooks/echo.feature --results {CUCU_RESULTS_DIR}/mixed_results_fail_pass_hooks_results/ -l debug --no-color-output --generate-report --report {CUCU_RESULTS_DIR}/mixed_results_fail_pass_hooks_report/" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" contains the following
      """
      HOOK-ERROR in after_scenario_fail: RuntimeError: boom
      """
      And I should see "{STDOUT}" contains the following
      """
      raise RuntimeError("boom")
      """
      And I should see "{STDOUT}" contains the following
      """
      HOOK after_scenario_pass: passed ✅
      """
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/mixed_results_fail_pass_hooks_report" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I click the link "Feature that has failing and passing after scenario hooks"
      And I click the link "Hello world scenario"
     Then I should see the text "Hello World"

  Scenario: User gets expected output when running a scenario with multiple after hooks passing and failing in order
    Given I create a file at "{CUCU_RESULTS_DIR}/mixed_results_pass_fail_hooks/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import logger, register_after_scenario_hook

      def after_scenario_fail(ctx):
        raise RuntimeError("boom")

      register_after_scenario_hook(after_scenario_fail)

      def after_scenario_pass(ctx):
        logger.debug("This hook should execute and pass")

      register_after_scenario_hook(after_scenario_pass)

      """
      And I create a file at "{CUCU_RESULTS_DIR}/mixed_results_pass_fail_hooks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/mixed_results_pass_fail_hooks/echo.feature" with the following:
      """
      Feature: Feature that has failing and passing after scenario hooks

        Scenario: Hello world scenario
          Given I echo "Hello World"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/mixed_results_pass_fail_hooks/echo.feature --results {CUCU_RESULTS_DIR}/mixed_results_pass_fail_hooks_results/ -l debug --no-color-output --generate-report --report {CUCU_RESULTS_DIR}/mixed_results_pass_fail_hooks_report/" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" contains the following
      """
      HOOK-ERROR in after_scenario_fail: RuntimeError: boom
      """
      And I should see "{STDOUT}" contains the following
      """
      raise RuntimeError("boom")
      """
      And I should see "{STDOUT}" contains the following
      """
      HOOK after_scenario_pass: passed ✅
      """
     When I start a webserver at directory "{CUCU_RESULTS_DIR}/mixed_results_pass_fail_hooks_report" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
      And I click the link "Feature that has failing and passing after scenario hooks"
      And I click the link "Hello world scenario"
     Then I should see the text "Hello World"

  @QE-16733
  Scenario: When a before_scenario hook fails, the Scenario is skipped, but reports as errored
    Given I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu import register_before_scenario_hook

      def before_scenario_error(ctx):
          raise RuntimeError("This error should be logged and reported.")

      register_before_scenario_hook(before_scenario_error)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_hooks/echo.feature" with the following:
      """
      Feature: Feature that simply echoes "Hello World"

        Scenario: This is a scenario that simply echoes hello world
          Given I echo "Hello"
            And I echo "World"
      """
     * # The --show-skips argument is necessary for both the `cucu run` command and the `cucu report` command
     When I run the command "cucu run {CUCU_RESULTS_DIR}/custom_hooks/echo.feature --show-skips --results {CUCU_RESULTS_DIR}/custom_hooks_results/ -l debug --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     When I run the command "cucu report {CUCU_RESULTS_DIR}/custom_hooks_results --show-skips --output {CUCU_RESULTS_DIR}/browser-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/browser-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/flat.html"
     Then I should see a table that contains rows matching the following
        | .* | Feature that simply echoes "Hello World" | This is a scenario that simply echoes hello world | .* | errored | .* |
      And I wait to click the link "This is a scenario that simply echoes hello world"
     * # Additional check of the log file itself here, when QE-16733 is resolved
     # When I wait to click the link "Logs"
     #  And I wait to click the link "cucu.debug.console.log"
     # Then I wait to see the text "This error should be logged and reported."

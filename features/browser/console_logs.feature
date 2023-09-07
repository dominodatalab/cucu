Feature: Browser console logs
  As a developer I want to be sure we collect at the end of each run the browser
  console logs

  @workaround @QE-7075
  Scenario: User will find per scenario executed a logs directory containing browser logs
    #
    # temporarily we'll only support log retrieval on chrome as other browsers
    # have issues we'll have to workaround
    #
    Given I skip this scenario if the current browser is not "chrome"
     When I run the command "cucu run data/features/scenario_with_console_logs.feature --results {CUCU_RESULTS_DIR}/console-logging" and save stdout to "STDOUT" and expect exit code "0"
      And I should see the file at "{CUCU_RESULTS_DIR}/console-logging/Feature with console logs/Scenario with console logs/logs/browser_console.log.txt" matches the following:
      """
      .* "INFO", "message": ".*/console_logging.html 4:12 \\"this is a regular log\\"", .*
      .* "SEVERE", "message": ".*/console_logging.html 5:12 \\"this is an error log\\"", .*
      .* "DEBUG", "message": ".*/console_logging.html 6:12 \\"this is a debug log\\"", .*
      .* "WARNING", "message": ".*/console_logging.html 7:12 \\"this is a warn log\\"", .*
      """
      And I should see the file at "{CUCU_RESULTS_DIR}/console-logging/Feature with console logs/Scenario without console logs/logs/browser_console.log.txt" is equal to the following:
      """
      """

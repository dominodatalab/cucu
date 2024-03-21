Feature: Run outputs
  As a developer I want the user to the expected console and filesystem outputs
  when running with certain flags/feature files.

  Scenario: User can --dry-run a passing scenario
    Given I run the command "cucu run data/features/feature_with_passing_scenario.feature --dry-run --results {CUCU_RESULTS_DIR}/passing_feature_dry_run_results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should not see the directory at "{CUCU_RESULTS_DIR}/passing_feature_dry_run_results"
      And I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature with passing scenario

        Scenario: Just a scenario that passes
          Given I echo "nothing to see here"

      0 features passed, 0 failed, 0 skipped, 1 untested
      0 scenarios passed, 0 failed, 0 skipped, 1 untested
      0 steps passed, 0 failed, 0 skipped, 0 undefined, 1 untested
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

  Scenario: User gets expected output when running steps with substeps
    Given I run the command "cucu run data/features/scenario_with_substeps.feature --results {CUCU_RESULTS_DIR}/substeps-results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature with substeps

        Scenario: Scenario that uses a step with substeps
            ⤷ When I do nothing             .*
            ⤷  And I do nothing             .*
            ⤷  And I do nothing             .*
          Given I use a step with substeps  .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      1 step passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

  Scenario: User gets expected non zero exit code when a scenario fails
    Given I run the command "cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/failing-scenario-results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     Then I should see "{STDOUT}" matches the following
      """
      [\s\S]*
      Feature: Feature with failing scenario

        Scenario: Just a scenario that fails
          Given I fail .*s
      Traceback \(most recent call last\):
      [\s\S]*
      RuntimeError: step fails on purpose
      [\s\S]*
      Failing scenarios:
        data/features/feature_with_failing_scenario.feature:\d+  Just a scenario that fails
      [\s\S]*
      0 features passed, 1 failed, 0 skipped
      0 scenarios passed, 1 failed, 0 skipped
      0 steps passed, 1 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is equal to the following
      """
      Error: test run failed, see above for details

      """

  Scenario: User can run a scenario with background which uses a step with substeps
    Given I run the command "cucu run data/features/feature_with_background_using_substeps.feature --results {CUCU_RESULTS_DIR}/background-with-substeps-results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following
      """
      Feature: Feature with background using substeps

        Scenario: Scenario which now has a background using a step with substeps
      first line of the background

          Given I echo "first line of the background"     # .*
      hello

            ⤷ When I echo "hello"                         # .*
      cruel

            ⤷  And I echo "cruel"                         # .*
      world

            ⤷  And I echo "world"                         # .*
            And I use a step with substeps that log       # .*
      This is from the scenario

           When I echo "This is from the scenario"        # .*

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      3 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

  Scenario: User can run a scenario with various types of output and see the variable values expanded at runtime
    Given I run the command "cucu run data/features/feature_with_multilines_and_tables.feature --results {CUCU_RESULTS_DIR}/variable_values_expanded_results --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" matches the following
      """
      Feature: Feature with multilines and tables

        Scenario: Scenario with a step that has a multiline argument
          Given I set the variable "FOO" to "bar" .*
      This is a multiline text that
      can go on for a few lines
      and print variables like FOO=bar

           Then I echo the following .*
              \"\"\"
              This is a multiline text that
              can go on for a few lines
              and print variables like FOO=\{FOO\}
              \"\"\"
           # FOO="bar"

        Scenario: Scenario with a step that has a table argument
          Given I set the variable "FIZZ" to "buzz" .*
      | header |
      | row 1  |
      | row 2  |
      | buzz   |

          Given I echo the following .*
              | header |
              | row 1  |
              | row 2  |
              | \{FIZZ\} |
          # FIZZ="buzz"

      1 feature passed, 0 failed, 0 skipped
      2 scenarios passed, 0 failed, 0 skipped
      4 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """
      And I should see "{STDERR}" is empty

  Scenario: User gets JUnit XML results file as expected
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature --show-skips --results {CUCU_RESULTS_DIR}/validate_junit_xml_results" and save stdout to "STDOUT" and expect exit code "1"
     Then I should see a file at "{CUCU_RESULTS_DIR}/validate_junit_xml_results/Feature with mixed results.xml"
      And I should see the file at "{CUCU_RESULTS_DIR}/validate_junit_xml_results/Feature with mixed results.xml" matches the following:
      """
      <testsuite name="Feature with mixed results" foldername="Feature with mixed results" tests="7" errors="0" failures="3" skipped="1" timestamp=".*" tags="mixed">
       <testcase classname="Feature with mixed results" name="Scenario that passes" foldername="Scenario that passes" status="passed" time=".*">
       </testcase>
       <testcase classname="Feature with mixed results" name="Scenario that fails" foldername="Scenario that fails" status="failed" time=".*">
        <failure>
        [\s\S]*
        </failure>
       </testcase>
       <testcase classname="Feature with mixed results" name="Scenario and after-hook both fail" foldername="Scenario and after-hook both fail" status="failed" time=".*">
        <failure>
        [\s\S]*
        </failure>
       </testcase>
       <testcase classname="Feature with mixed results" name="Scenario with after-hook error" foldername="Scenario with after-hook error" status="passed" time=".*">
       </testcase>
       <testcase classname="Feature with mixed results" name="Scenario that also passes" foldername="Scenario that also passes" status="passed" time=".*">
       </testcase>
       <testcase classname="Feature with mixed results" name="Scenario that has an undefined step" foldername="Scenario that has an undefined step" status="failed" time=".*">
       </testcase>
       <testcase classname="Feature with mixed results" name="Scenario that is skipped" foldername="Scenario that is skipped" status="skipped" time=".*" tags="disabled">
        <skipped>
        </skipped>
       </testcase>
      </testsuite>
      """

  Scenario: User gets exact expected output from various console outputs
    Given I run the command "cucu run data/features/echo.feature --env SHELL=/foo/bar/zsh --env USER=that_guy --env PWD=/some/place/nice --results {CUCU_RESULTS_DIR}/validate_junit_xml_results  --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      # {SHELL} and {PWD} contain slashes which we don't have a good way of
      # escaping in the tests yet so we'll just .* to match them and for the
      # crazy looking 4 backslashes its because the original test has 2
      # backslashes and in order to escape each one we need another 2 so we end
      # up with 4 backlslashes
      And I should see "{STDOUT}" matches the following
      """
      Feature: Echo

        Scenario: Echo an environment variable
      current shell is '/foo/bar/zsh'

          Given I echo "current shell is '\{SHELL\}'" .*
          # SHELL="/foo/bar/zsh"
      current user is 'that_guy'

            And I echo the following .*
              \"\"\"
              current user is '\{USER\}'
              \"\"\"
            # USER="that_guy"
      current working directory is '/some/place/nice'

            And I echo "current working directory is '\{PWD\}'" .*
            # PWD="/some/place/nice"
      \{
        "user": "that_guy"
      \}
            And I echo the following .*
              \"\"\"
              \\\\{
                "user": "\{USER\}"
              \\\\}
              \"\"\"
            # USER="that_guy"
      .* INFO hello that_guy
            And I log "hello \{USER\}" at level "info" .*
            # USER="that_guy"
      .* INFO good bye that_guy
            And I log the following at level "info" .*
              \"\"\"
              good bye \{USER\}
              \"\"\"
            # USER="that_guy"

      1 feature passed, 0 failed, 0 skipped
      1 scenario passed, 0 failed, 0 skipped
      6 steps passed, 0 failed, 0 skipped, 0 undefined
      [\s\S]*
      """

  Scenario: User gets expected table representation in console output
    Given I run the command "cucu run data/features/feature_with_failing_scenario_with_table.feature --results {CUCU_RESULTS_DIR}/tables_in_output_results" and save stdout to "STDOUT" and expect exit code "1"
      And I should see "{STDOUT}" contains the following
      """
      RuntimeError: unable to find desired table
      expected:
        | nope | this | is | not | it |

      found:
      "1st" table:
        | Name   | City          | Country       |
        | Alfred | Berlin        | Germany       |
        | Joe    | San Francisco | United States |
        | Maria  | Cancun        | Mexico        |
      "2nd" table:
        | Name   | Age |
        | Alfred | 31  |
        | Joe    | 35  |
        | Maria  | 33  |
      "3rd" table:
        | Name (last name optional) | Age (in years) |
        | Alfred                    | 31             |
        | Maria Lopez               | 33             |
      "4th" table:
        | User Title   | Yearly Salary |
        | Alfred White | 120,000       |
        | Maria Lopez  | 133,000       |
      """

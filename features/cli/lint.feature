Feature: Lint
  As a developer I want the `cucu lint` command to work as expected

  Scenario: User gets error message when violation can not be fixed
    Given I create a file at "{CUCU_RESULTS_DIR}/undefined_step_lint/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/undefined_step_lint/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/undefined_step_lint/undefined_step_feature.feature" with the following:
      """
      Feature: Feature with undefined step

        Scenario: This is a scenario that is using an undefined step
          Given I use an undefined step
      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/undefined_step_lint/undefined_step_feature.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" contains the following:
      """
      You can implement step definitions for undefined steps with these snippets
      """
      And I should see "{STDOUT}" contains the following:
      """
      failure loading some steps, see above for details
      """
      And I should see "{STDERR}" contains the following:
      """
      Error: linting errors found, but not fixed, see above for details
      """

  Scenario: User can find and fix indentation violations
    Given I create a file at "{CUCU_RESULTS_DIR}/indent_lint/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/indent_lint/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/indent_lint/bad_feature_indentation.feature" with the following:
      """
        Feature: Badly indented feature

            @tag_badly_indented
          Scenario: This is a scenario in a badly indented feature name line
        Given I echo "foo"
        When I echo "bar"
        And I echo "fizz"
        Then I echo "buzz"
      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/indent_lint/bad_feature_indentation.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/indent_lint/bad_feature_indentation.feature:1: W feature name should not have any indentation
      results/indent_lint/bad_feature_indentation.feature:3: W scenario tags should be indented with 2 spaces
      results/indent_lint/bad_feature_indentation.feature:4: W scenario name should be indented with 2 spaces
      results/indent_lint/bad_feature_indentation.feature:5: W given keyword should be indented with 4 spaces
      results/indent_lint/bad_feature_indentation.feature:6: W when keyword should be indented with 5 spaces
      results/indent_lint/bad_feature_indentation.feature:7: W and keyword should be indented with 6 spaces
      results/indent_lint/bad_feature_indentation.feature:8: W then keyword should be indented with 5 spaces
      
      """
      And I should see "{STDERR}" is equal to the following:
      """
      Error: linting errors found, but not fixed, see above for details

      """
     Then I run the command "cucu lint --fix {CUCU_RESULTS_DIR}/indent_lint/bad_feature_indentation.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/indent_lint/bad_feature_indentation.feature:1: W feature name should not have any indentation ✓
      results/indent_lint/bad_feature_indentation.feature:3: W scenario tags should be indented with 2 spaces ✓
      results/indent_lint/bad_feature_indentation.feature:4: W scenario name should be indented with 2 spaces ✓
      results/indent_lint/bad_feature_indentation.feature:5: W given keyword should be indented with 4 spaces ✓
      results/indent_lint/bad_feature_indentation.feature:6: W when keyword should be indented with 5 spaces ✓
      results/indent_lint/bad_feature_indentation.feature:7: W and keyword should be indented with 6 spaces ✓
      results/indent_lint/bad_feature_indentation.feature:8: W then keyword should be indented with 5 spaces ✓

      linting errors found and fixed, see above for details

      """

      And I should see the file at "{CUCU_RESULTS_DIR}/indent_lint/bad_feature_indentation.feature" is equal to the following:
      """
      Feature: Badly indented feature

        @tag_badly_indented
        Scenario: This is a scenario in a badly indented feature name line
          Given I echo "foo"
           When I echo "bar"
            And I echo "fizz"
           Then I echo "buzz"
      """
      # nothing to fix at this point
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/indent_lint/bad_feature_indentation.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" is empty
      And I should see "{STDERR}" is empty

  Scenario: User can find and fix unnecessary whitespace
    Given I create a file at "{CUCU_RESULTS_DIR}/whitespace_lint/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/whitespace_lint/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/whitespace_lint/extraneous_whitespace.feature" with the following:
      """
      Feature: Feature with extraneous whitespace 


        Scenario: Scenario with extraneous whitespace  
          Given I echo "foo" 

      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/whitespace_lint/extraneous_whitespace.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/whitespace_lint/extraneous_whitespace.feature:1: W line has extraneous whitespace at the end
      results/whitespace_lint/extraneous_whitespace.feature:3: W too many blank lines
      results/whitespace_lint/extraneous_whitespace.feature:4: W line has extraneous whitespace at the end
      results/whitespace_lint/extraneous_whitespace.feature:5: W line has extraneous whitespace at the end

      """
      And I should see "{STDERR}" is equal to the following:
      """
      Error: linting errors found, but not fixed, see above for details

      """
     Then I run the command "cucu lint --fix {CUCU_RESULTS_DIR}/whitespace_lint/extraneous_whitespace.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/whitespace_lint/extraneous_whitespace.feature:1: W line has extraneous whitespace at the end ✓
      results/whitespace_lint/extraneous_whitespace.feature:3: W too many blank lines ✓
      results/whitespace_lint/extraneous_whitespace.feature:4: W line has extraneous whitespace at the end ✓
      results/whitespace_lint/extraneous_whitespace.feature:5: W line has extraneous whitespace at the end ✓

      linting errors found and fixed, see above for details

      """
      And I should see the file at "{CUCU_RESULTS_DIR}/whitespace_lint/extraneous_whitespace.feature" is equal to the following:
      """
      Feature: Feature with extraneous whitespace

        Scenario: Scenario with extraneous whitespace
          Given I echo "foo"

      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/whitespace_lint/extraneous_whitespace.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" is empty
      And I should see "{STDERR}" is empty

  Scenario: User gets error when cucu lint has an issue in the underlying step code
    Given I create a file at "{CUCU_RESULTS_DIR}/broken_step_lint/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/broken_step_lint/steps/__init__.py" with the following:
      """
      from cucu.steps import *

      raise RuntimeError("boom")
      """
      And I create a file at "{CUCU_RESULTS_DIR}/broken_step_lint/broken_step_feature.feature" with the following:
      """
      Feature: Just a place holder
      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/broken_step_lint/broken_step_feature.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDERR}" contains the following:
      """
      RuntimeError: boom
      """

  Scenario: User gets a lint error when there are duplicate feature names
    Given I create a file at "{CUCU_RESULTS_DIR}/unique_feature_lint/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/unique_feature_lint/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/unique_feature_lint/first_feature.feature" with the following:
      """
      Feature: Feature with non unique name

        Scenario: Scenario that just passes
          Given I echo "foo"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/unique_feature_lint/second_feature.feature" with the following:
      """
      Feature: Feature with non unique name

        Scenario: Another scenario that just passes
          Given I echo "foo"
      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/unique_feature_lint" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      {CUCU_RESULTS_DIR}/unique_feature_lint/second_feature.feature:1: E feature name must be unique, "Feature with non unique name" also used in "{CUCU_RESULTS_DIR}/unique_feature_lint/first_feature.feature"

      """
      And I should see "{STDERR}" is equal to the following:
      """
      Error: linting errors found, but not fixed, see above for details

      """
     Then I run the command "cucu lint --fix {CUCU_RESULTS_DIR}/unique_feature_lint" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      {CUCU_RESULTS_DIR}/unique_feature_lint/second_feature.feature:1: E feature name must be unique, "Feature with non unique name" also used in "{CUCU_RESULTS_DIR}/unique_feature_lint/first_feature.feature" ✗ (must be fixed manually)

      """
      And I should see "{STDERR}" is equal to the following:
      """
      Error: linting errors found, but not fixed, see above for details

      """

  Scenario: User gets a lint error when there are duplicate scenario names
    Given I create a file at "{CUCU_RESULTS_DIR}/unique_scenario_lint/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/unique_scenario_lint/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/unique_scenario_lint/first_feature.feature" with the following:
      """
      Feature: First Feature

        Scenario: Scenario with non unique name
          Given I echo "foo"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/unique_scenario_lint/second_feature.feature" with the following:
      """
      Feature: Second Feature

        Scenario: Scenario with non unique name
          Given I echo "foo"
      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/unique_scenario_lint" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      {CUCU_RESULTS_DIR}/unique_scenario_lint/second_feature.feature:3: E scenario name must be unique, "Scenario with non unique name" also used in "{CUCU_RESULTS_DIR}/unique_scenario_lint/first_feature.feature:2" Scenario: "Scenario with non unique name"

      """
      And I should see "{STDERR}" is equal to the following:
      """
      Error: linting errors found, but not fixed, see above for details

      """
     Then I run the command "cucu lint --fix {CUCU_RESULTS_DIR}/unique_scenario_lint" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      {CUCU_RESULTS_DIR}/unique_scenario_lint/second_feature.feature:3: E scenario name must be unique, "Scenario with non unique name" also used in "{CUCU_RESULTS_DIR}/unique_scenario_lint/first_feature.feature:2" Scenario: "Scenario with non unique name" ✗ (must be fixed manually)

      """
      And I should see "{STDERR}" is equal to the following:
      """
      Error: linting errors found, but not fixed, see above for details

      """

  @regression
  Scenario: User can lint and fix a file with no indentation
    Given I create a file at "{CUCU_RESULTS_DIR}/no_indent/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/no_indent/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/no_indent/bad_feature_indentation.feature" with the following:
      """
      Feature: Badly indented feature

      @tag_badly_indented
      Scenario: This is a scenario in a badly indented feature name line
      Given I echo "foo"
      When I echo "bar"
      And I echo "fizz"
      Then I echo "buzz"
      """
     Then I run the command "cucu lint --fix {CUCU_RESULTS_DIR}/no_indent/bad_feature_indentation.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see the file at "{CUCU_RESULTS_DIR}/no_indent/bad_feature_indentation.feature" is equal to the following:
      """
      Feature: Badly indented feature

        @tag_badly_indented
        Scenario: This is a scenario in a badly indented feature name line
          Given I echo "foo"
           When I echo "bar"
            And I echo "fizz"
           Then I echo "buzz"
      """

  Scenario: User can define custom linting rules
    Given I create a file at "{CUCU_RESULTS_DIR}/custom_linting_rules/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu.config import CONFIG
      
      CONFIG["CUCU_LINT_RULES_PATH"] = "{CUCU_RESULTS_DIR}/custom_linting_rules/lint_rules"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_linting_rules/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_linting_rules/custom_linting_feature.feature" with the following:
      """
      Feature: Feature in need of linting

        Scenario: This is a scenario with a custom linting violation
          Given I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/buttons.html"
            And I click the button "button"
            And I click the button "button"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_linting_rules/lint_rules/custom_rules.yaml" with the following:
      """
      # custom cucu lint rules
      ---

      click_step_must_be_followed_by_wait_to:
        message: a click step must be followed by a `wait to` step
        type: error
        previous_line:
          match: '.* I click the (.*)'
        current_line:
          # match if the next line does not contain `wait to` in it
          match: '^((?!wait to).)*$'
        fix:
          match: 'I (.*)'
          replace: 'I wait to \1'
      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/custom_linting_rules/custom_linting_feature.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" contains the following:
      """
      results/custom_linting_rules/custom_linting_feature.feature:6: E a click step must be followed by a `wait to` step
      """
      And I should see "{STDERR}" contains the following:
      """
      Error: linting errors found, but not fixed, see above for details
      """

  Scenario: User can exclude attribute when defining custom rules
    Given I create a file at "{CUCU_RESULTS_DIR}/custom_linting_with_exclusions/environment.py" with the following:
      """
      from cucu.environment import *
      from cucu.config import CONFIG
      
      CONFIG["CUCU_LINT_RULES_PATH"] = "{CUCU_RESULTS_DIR}/custom_linting_with_exclusions/lint_rules"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_linting_with_exclusions/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_linting_with_exclusions/custom_linting_feature.feature" with the following:
      """
      Feature: Feature that will be excluded

        Scenario: This is a scenario with a custom linting violation
          Given I open a browser at the url "http://\{HOST_ADDRESS\}:\{PORT\}/buttons.html"
            And I click the button "button"
            And I click the button "button"
      """
      And I create a file at "{CUCU_RESULTS_DIR}/custom_linting_with_exclusions/lint_rules/custom_rules.yaml" with the following:
      """
      # custom cucu lint rules
      ---

      click_step_must_be_followed_by_wait_to:
        message: a click step must be followed by a `wait to` step
        type: error
        exclude: .*/custom_linting_feature.feature
        previous_line:
          match: '.* I click the (.*)'
        current_line:
          # match if the next line does not contain `wait to` in it
          match: '^((?!wait to).)*$'
        fix:
          match: 'I (.*)'
          replace: 'I wait to \1'
      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/custom_linting_with_exclusions/custom_linting_feature.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
      And I should see "{STDOUT}" is empty
      And I should see "{STDERR}" is empty

  Scenario: User gets appropriate exit code when cucu can not parse the file
    Given I create a file at "{CUCU_RESULTS_DIR}/broken_feature_file_lint/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/broken_feature_file_lint/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/broken_feature_file_lint/broken_feature.feature" with the following:
      """
      This is just garbage
      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/broken_feature_file_lint/broken_feature.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" contains the following:
      """
      Parser failure in state init, at line 1: "This is just garbage"
      """

  Scenario: User gets an error when using invalid feature or scenario names
    Given I create a file at "{CUCU_RESULTS_DIR}/invalid_names_lint/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/invalid_names_lint/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/invalid_names_lint/bad_name_usage.feature" with the following:
      """
      Feature: Feature with invalid characters /\:"'

        Scenario: Scenario with invalid characters /\:"'
          Given I echo "buzz"
      """
     Then I run the command "cucu lint {CUCU_RESULTS_DIR}/invalid_names_lint/bad_name_usage.feature" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/invalid_names_lint/bad_name_usage.feature:1: E feature name must not contain the characters '/\:?'
      results/invalid_names_lint/bad_name_usage.feature:3: E scenario name must not contain the characters '/\:?'

      """
      And I should see "{STDERR}" is equal to the following:
      """
      Error: linting errors found, but not fixed, see above for details

      """

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
     When I run the command "cucu lint {CUCU_RESULTS_DIR}/undefined_step_lint/undefined_step_feature.feature" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/undefined_step_lint/undefined_step_feature.feature:4: E undefined step "I use an undefined step"

      """
      And I should see "{STDERR}" is equal to the following:
      """
      Error: linting errors found, but not fixed, see above for details

      """
     When I run the command "cucu lint --fix {CUCU_RESULTS_DIR}/undefined_step_lint/undefined_step_feature.feature" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/undefined_step_lint/undefined_step_feature.feature:4: E undefined step "I use an undefined step" ✗ (must be fixed manually)

      """
      And I should see "{STDERR}" is equal to the following:
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
      
          Scenario: This is a scenario in a badly indented feature name line
            Given I echo "I should never see this"
      """
     When I run the command "cucu lint {CUCU_RESULTS_DIR}/indent_lint/bad_feature_indentation.feature" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/indent_lint/bad_feature_indentation.feature:1: W feature name should not have any indentation
      results/indent_lint/bad_feature_indentation.feature:3: W scenario name should be indented with 2 spaces
      results/indent_lint/bad_feature_indentation.feature:4: W given keyword should be indented with 4 spaces

      """
      And I should see "{STDERR}" is equal to the following:
      """
      Error: linting errors found, but not fixed, see above for details

      """
     When I run the command "cucu lint --fix {CUCU_RESULTS_DIR}/indent_lint/bad_feature_indentation.feature" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/indent_lint/bad_feature_indentation.feature:1: W feature name should not have any indentation ✓
      results/indent_lint/bad_feature_indentation.feature:3: W scenario name should be indented with 2 spaces ✓
      results/indent_lint/bad_feature_indentation.feature:4: W given keyword should be indented with 4 spaces ✓

      linting errors found and fixed, see above for details

      """

      And I should see the file at "{CUCU_RESULTS_DIR}/indent_lint/bad_feature_indentation.feature" has the following:
      """
      Feature: Badly indented feature

        Scenario: This is a scenario in a badly indented feature name line
          Given I echo "I should never see this"
      """
      # nothing to fix at this point
     When I run the command "cucu lint {CUCU_RESULTS_DIR}/indent_lint/bad_feature_indentation.feature" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
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
     When I run the command "cucu lint {CUCU_RESULTS_DIR}/whitespace_lint/extraneous_whitespace.feature" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "1"
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
     When I run the command "cucu lint --fix {CUCU_RESULTS_DIR}/whitespace_lint/extraneous_whitespace.feature" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" is equal to the following:
      """
      results/whitespace_lint/extraneous_whitespace.feature:1: W line has extraneous whitespace at the end ✓
      results/whitespace_lint/extraneous_whitespace.feature:3: W too many blank lines ✓
      results/whitespace_lint/extraneous_whitespace.feature:4: W line has extraneous whitespace at the end ✓
      results/whitespace_lint/extraneous_whitespace.feature:5: W line has extraneous whitespace at the end ✓
     
      linting errors found and fixed, see above for details

      """
      And I should see the file at "{CUCU_RESULTS_DIR}/whitespace_lint/extraneous_whitespace.feature" has the following:
      """
      Feature: Feature with extraneous whitespace

        Scenario: Scenario with extraneous whitespace
          Given I echo "foo"

      """
     When I run the command "cucu lint {CUCU_RESULTS_DIR}/whitespace_lint/extraneous_whitespace.feature" and save stdout to "STDOUT", stderr to "STDERR", exit code to "EXIT_CODE"
     Then I should see "{EXIT_CODE}" is equal to "0"
      And I should see "{STDOUT}" is empty
      And I should see "{STDERR}" is empty

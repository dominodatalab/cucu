Feature: Config
  As a developer I want the user to get the expected variable and config
  behavior when using cucu

  Scenario: User can load cucurc values from cucurc files at various levels
    Given I create a file at "{CUCU_RESULTS_DIR}/load/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load/cucurc.yml" with the following:
      """
      FOO: bar
      BUZZ: wah
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load/nested/cucurc.yml" with the following:
      """
      FIZZ: booze
      BUZZ: wah
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load/nested/cucurc/cucurc.yml" with the following:
      """
      FIZZ: buzz
      BUZZ: wat
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load/nested/cucurc/feature_that_prints.feature" with the following:
      """
      Feature: Feature file that prints some variables

        Scenario: This scenario prints a bunch of variables
         Given I echo "\{FOO\}"
           And I echo "\{FIZZ\}"
           And I echo "\{BUZZ\}"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/load/nested/cucurc --results={CUCU_RESULTS_DIR}/nested_cucurc_from_parent_directory_results --env BUZZ=buzz --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
       """
       [\s\S]*Feature: Feature file that prints some variables

         Scenario: This scenario prints a bunch of variables
       bar

           Given I echo "\{FOO\}" \s*# .*
           # FOO="bar"
       booze

             And I echo "\{FIZZ\}" \s*# .*
             # FIZZ="booze"
       buzz

             And I echo "\{BUZZ\}" \s*# .*
             # BUZZ="buzz"

       1 feature passed, 0 failed, 0 skipped
       1 scenario passed, 0 failed, 0 skipped
       3 steps passed, 0 failed, 0 skipped(, 0 undefined)?
       [\s\S]*
       """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/load --results={CUCU_RESULTS_DIR}/nested_cucurc_from_top_level_directory_results --env BUZZ=buzz --no-color-output" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
       """
       [\s\S]*Feature: Feature file that prints some variables

         Scenario: This scenario prints a bunch of variables
       bar

           Given I echo "\{FOO\}" \s*# .*
           # FOO="bar"
       booze

             And I echo "\{FIZZ\}" \s*# .*
             # FIZZ="booze"
       buzz

             And I echo "\{BUZZ\}" \s*# .*
             # BUZZ="buzz"

       1 feature passed, 0 failed, 0 skipped
       1 scenario passed, 0 failed, 0 skipped
       3 steps passed, 0 failed, 0 skipped(, 0 undefined)?
       [\s\S]*
       """

  @workers
  Scenario: User can load cucurc values from cucurc files at various levels when using workers
    Given I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc_with_workers/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc_with_workers/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc_with_workers/cucurc.yml" with the following:
      """
      FOO: bar
      FIZZ: booze
      BUZZ: wah
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc_with_workers/directory/cucurc.yml" with the following:
      """
      FIZZ: buzz
      BUZZ: wat
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc_with_workers/directory/feature_that_prints.feature" with the following:
      """
      Feature: Feature file that prints some variables

        Scenario: This scenario prints a bunch of variables
         Given I echo "\{FOO\}"
           And I echo "\{FIZZ\}"
           And I echo "\{BUZZ\}"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/load_nested_cucurc_with_workers --results={CUCU_RESULTS_DIR}/nested_cucurc_with_workers_results --env BUZZ=buzz --workers 2 --no-color-output" and expect exit code "0"
     Then I should see the file at "{CUCU_RESULTS_DIR}/nested_cucurc_with_workers_results/Feature file that prints some variables.log" matches the following:
       """
       [\s\S]*Feature: Feature file that prints some variables

         Scenario: This scenario prints a bunch of variables
       bar

           Given I echo "\{FOO\}" \s*# .*
           # FOO="bar"
       booze

             And I echo "\{FIZZ\}" \s*# .*
             # FIZZ="booze"
       buzz

             And I echo "\{BUZZ\}" \s*# .*
             # BUZZ="buzz"

       1 feature passed, 0 failed, 0 skipped
       1 scenario passed, 0 failed, 0 skipped
       3 steps passed, 0 failed, 0 skipped(, 0 undefined)?
       [\s\S]*
       """

  Scenario: User gets an appropriate error when cucurc has invalid syntax
    Given I create a file at "{CUCU_RESULTS_DIR}/load_bad_cucurc/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_bad_cucurc/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_bad_cucurc/cucurc.yml" with the following:
      """
      FOO: bar
      completely=broken
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_bad_cucurc/directory/feature_that_prints.feature" with the following:
      """
      Feature: Feature tries to print something

        Scenario: This scenario prints the value of FOO
         Given I echo "\{FOO\}"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/load_bad_cucurc --results={CUCU_RESULTS_DIR}/nested_cucurc_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     Then I should see "{STDOUT}" is empty
      And I should see "{STDERR}" contains "yaml.scanner.ScannerError: while scanning a simple key"

  Scenario: User can have a register_custom_variable_handling rely on a CONFIG value defined in enviroment.py at import time
    Given I create a file at "{CUCU_RESULTS_DIR}/defined_in_import/environment.py" with the following:
      """
      from cucu import register_custom_variable_handling
      from cucu.environment import *
      from cucu.config import CONFIG
      CONFIG["DEFINED_AT_IMPORT_TIME"] = "defined at import time"

      def my_custom_variable_handler(name):
          # Ensure that the CONFIG value is still defined in the core.run finally block
          if CONFIG["DEFINED_AT_IMPORT_TIME"] == None:
              raise ValueError("CONFIG['DEFINED_AT_IMPORT_TIME'] is None")

          return CONFIG[name]

      register_custom_variable_handling(".*", my_custom_variable_handler)
      """
      And I create a file at "{CUCU_RESULTS_DIR}/defined_in_import/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/defined_in_import/feature_that_prints.feature" with the following:
      """
      Feature: Feature file that prints my var

        Scenario: This scenario prints a bunch of variables
         Given I echo "\{DEFINED_AT_IMPORT_TIME\}"
      """
     Then I run the command "cucu run {CUCU_RESULTS_DIR}/defined_in_import --results={CUCU_RESULTS_DIR}/defined_in_import_results -g" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"

Feature: Tags
  As a developer I want the user to run the tags command

  @cli
  Scenario: User can run the tags command
    Given I run the command "cucu tags data/features/tagged_features" and save stdout to "STDOUT" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
      """
      [\s\S]*Tag.*Scenarios Affected.*
      [\s\S]*disabled.*1.*
      [\s\S]*feature1.*1.*
      [\s\S]*feature2.*1.*
      [\s\S]*feature3.*1.*
      [\s\S]*scenario1.*3
      """

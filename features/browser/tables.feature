Feature: Tables
  As a developer I want to make sure the test writer can verify tables present
  on the page

  Background: HTML page with tables
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/tables.html"

  Scenario: User can find an exact table
    Given I should see a table that is the following:
        | Name   | City          | Country       |
        | Alfred | Berlin        | Germany       |
        | Joe    | San Francisco | United States |
        | Maria  | Cancun        | Mexico        |

  Scenario: User can find a matching table
    Given I should see a table that matches the following:
        | Name   | City          | Country       |
        | Alfred | Berlin        | Germany       |
        | .*     | .*            | .*            |
        | Maria  | Cancun        | Mexico        |

  Scenario: User can find a table that contains some rows
    Given I should see a table that contains the following:
        | Name   | City          | Country       |
        | Maria  | Cancun        | Mexico        |

  Scenario: User can find a table that contains some matching rows
    Given I should see a table that contains rows matching the following:
        | Name   | City          | Country       |
        | .*     | .*            | .*            |
        | Maria  | Cancun        | Mexico        |

Feature: Tables
  As a developer I want to make sure the test writer can verify tables present
  on the page

  Background: HTML page with tables
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"

  Scenario: User verify there is an exact table
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should see a table that is the following:
        | Name   | City          | Country       |
        | Alfred | Berlin        | Germany       |
        | Joe    | San Francisco | United States |
        | Maria  | Cancun        | Mexico        |

  Scenario: User can verify is not an exact table
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should not see a table that is the following:
        | Name   | City          |
        | Alfred | Berlin        |

  Scenario: User verify there is a matching table
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should see a table that matches the following:
        | Name   | City          | Country       |
        | Alfred | Berlin        | Germany       |
        | .*     | .*            | .*            |
        | Maria  | Cancun        | Mexico        |

  Scenario: User verify there is not a matching table
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should not see a table that matches the following:
        | Name   | City          | Country       |
        | .*     | .*            | .*            |

  Scenario: User verify there is a table that contains some rows
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should see a table that contains the following:
        | Name   | City          | Country       |
        | Maria  | Cancun        | Mexico        |

  Scenario: User verify there is not a table that contains some rows
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should not see a table that contains the following:
        | Name   | City          | Country       |
        | Maria  | San Francisco | United States |

  Scenario: User verify there is a table that contains some matching rows
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should see a table that contains rows matching the following:
        | Name   | City          | Country       |
        | .*     | .*            | .*            |
        | Maria  | Cancun        | Mexico        |

  Scenario: User verify there is not a table that contains some matching rows
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should not see a table that contains rows matching the following:
        | Name | City          | Country       |
        | Foo  | .*            | .*            |

  Scenario: User can wait to verify an exact table
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html?delay_page_load_ms=5000"
     Then I wait to see a table that is the following:
        | Name   | City          | Country       |
        | Alfred | Berlin        | Germany       |
        | Joe    | San Francisco | United States |
        | Maria  | Cancun        | Mexico        |
      And I should see the previous step took more than "4" seconds

  Scenario: User can wait to verify there is a matching table
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html?delay_page_load_ms=5000"
     Then I wait to see a table that matches the following:
        | Name   | City          | Country       |
        | Alfred | Berlin        | Germany       |
        | .*     | .*            | .*            |
        | Maria  | Cancun        | Mexico        |
      And I should see the previous step took more than "4" seconds

  Scenario: User can wait to verify wait to verify there is a table that contains some rows
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html?delay_page_load_ms=5000"
     Then I wait to see a table that contains the following:
        | Name   | City          | Country       |
        | Maria  | Cancun        | Mexico        |
      And I should see the previous step took more than "4" seconds

  Scenario: User can wait to verify there is a table that contains some matching rows
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html?delay_page_load_ms=5000"
     Then I wait to see a table that contains rows matching the following:
        | Name   | City          | Country       |
        | .*     | .*            | .*            |
        | Maria  | Cancun        | Mexico        |
      And I should see the previous step took more than "4" seconds

  Scenario: User can verify a table with values containing html tags
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should see a table that is the following:
        | Name (last name optional) | Age (in years) |
        | Alfred                    | 31             |
        | Maria Lopez               | 33             |

  Scenario: User can verify a table with values that have newlines in them
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
     Then I should see a table that is the following:
        | User Title   | Yearly Salary |
        | Alfred White | 120,000       |
        | Maria Lopez  | 133,000       |

  Scenario: User can verify a table with variables in the cell names
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
      And I set the variable "USERNAME" to "Alfred White"
     Then I should see a table that is the following:
        | User Title   | Yearly Salary |
        | {USERNAME}   | 120,000       |
        | Maria Lopez  | 133,000       |

  Scenario: User can save any table cell value to a variable
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
      And I set the variable "USERNAME" to "Alfred White"
     When I save "1st" table, "1st" row, "1st" column value to a variable "TABLE_1_VALUE"
     Then I should see "{TABLE_1_VALUE}" is equal to "Name"
     When I save "2nd" table, "2nd" row, "1st" column value to a variable "TABLE_2_VALUE"
     Then I should see "{TABLE_2_VALUE}" is equal to "Alfred"
     When I wait to save "3rd" table, "2nd" row, "2nd" column value to a variable "TABLE_3_VALUE"
     Then I should see "{TABLE_3_VALUE}" is equal to "31"
     When I wait to save "4th" table, "3rd" row, "2nd" column value to a variable "TABLE_4_VALUE"
     Then I should see "{TABLE_4_VALUE}" is equal to "133,000"

  Scenario: User can click specific row in table
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
      And I should see a table that matches the following:
        | Color  | Font            | Style     |
        | Red    | Arial           | Bold      |
        | Blue   | Helvetica       | Underline |
        | Green  | Times New Roman | Italic    |
     When I wait to click the "2nd" row in the "5th" table
     Then I should see the text "Row 2 clicked"
     When I wait to click the "3rd" row in the "5th" table
     Then I should see the text "Row 3 clicked"
     When I wait to click the "4th" row in the "5th" table
     Then I should see the text "Row 4 clicked"

  Scenario: User can click specific cell in table
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
      And I should see a table that matches the following:
        | City  | Country | Continent |
        | Paris | France  | Europe    |
        | Cairo | Egypt   | Africa    |
        | Tokyo | Japan   | Asia      |
     When I wait to click the cell corresponding to the "2nd" row and "2nd" column in the "6th" table
     Then I should see the text "France clicked"
     When I wait to click the cell corresponding to the "3rd" row and "3rd" column in the "6th" table
     Then I should see the text "Africa clicked"
     When I wait to click the cell corresponding to the "4th" row and "1st" column in the "6th" table
     Then I should see the text "Tokyo clicked"

  Scenario: User can click a column within a row that contains specific text within the table
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
      And I should see a table that matches the following:
        | City  | Country | Continent |
        | Paris | France  | Europe    |
        | Cairo | Egypt   | Africa    |
        | Tokyo | Japan   | Asia      |
     When I wait to click the "2nd" column within a row that contains the text "Paris" in the "6th" table
     Then I should see the text "France clicked"
     When I wait to click the "1st" column within a row that contains the text "Africa" in the "6th" table
     Then I should see the text "Cairo clicked"
     When I wait to click the "3rd" column within a row that contains the text "Japan" in the "6th" table
     Then I should see the text "Asia clicked"

  Scenario: User can wait until a table contains a specified number of rows
    Given I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/tables.html"
      And I wait to click the button "Add row immediately"
      And I should see a table that matches the following:
        | Row Number |
        |      2     |
     Then I wait to see the following steps fail
      """
        I wait to see there are "3" rows in the "7th" table
      """
     When I wait to click the button "Add row after 20 seconds"
     Then I wait to see there are "3" rows in the "7th" table
      And I should see the previous step took more than "15" seconds
      And I should see a table that matches the following:
        | Row Number |
        |      2     |
        |      3     |

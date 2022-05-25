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

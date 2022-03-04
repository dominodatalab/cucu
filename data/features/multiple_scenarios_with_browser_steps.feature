Feature: Multiple scenarios with browser steps

  Scenario: Search for cat on www.google.com
    Given I search for "define: cat" on google search
     Then I should see the text "/kat/"

  Scenario: Search for dog on www.google.com
    Given I search for "define: dog" on google search
     Then I should see the text "/dôɡ/"

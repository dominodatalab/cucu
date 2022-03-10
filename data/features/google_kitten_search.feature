Feature: Google kitten search

  Scenario: Search for kittens on www.google.com
    Given I search for "define: kittens" on google search
     Then I should see the text "Kitten"

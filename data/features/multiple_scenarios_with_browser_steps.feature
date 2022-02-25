Feature: Multiple scenarios with browser steps

  Scenario: Search for cats on www.google.com
    Given I search for "define: cats" on google search
     Then I should see the text "Cat - Wikipedia"
  
  Scenario: Search for dogs on www.google.com
    Given I search for "define: dogs" on google search
     Then I should see the text "Dog - Wikipedia"

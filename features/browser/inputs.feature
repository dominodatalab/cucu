Feature: Inputs
  As a developer I want to make sure the test writer can interact with different
  input elements
  
  Background: HTML page with buttons
    Given I start a webserver on port "40000" at directory "data/www"
      And I open a browser at the url "http://{HOST_ADDRESS}:40000/inputs.html"

  Scenario: User can write into an <input type="date">
    Given I should see no value in the input "input type=date"
     When I write "01/01/2019" into the input "input type=date"
     Then I should see "2019-01-01" in the input "input type=date"

  @disabled
  Scenario: User can write into an <input type="datetime-local">
    Given I should see no value in the input "input type=datetime-local"
     When I write "01/01/2019 00:00:00" into the input "input type=datetime-local"
     Then I should see "2019-01-01 00:00:00" in the input "input type=datetime-local"

  Scenario: User can write into an <input type="email">
    Given I should see no value in the input "input type=email"
     When I write "foo@bar.com" into the input "input type=email"
     Then I should see "foo@bar.com" in the input "input type=email"

  @disabled
  Scenario: User can write into an <input type="month">
    Given I should see no value in the input "input type=month"
     When I write "August" into the input "input type=month"
     Then I should see "1980-08" in the input "input type=month"

  Scenario: User can write into an <input type="number">
    Given I should see no value in the input "input type=number"
     When I write "1234" into the input "input type=number"
     Then I should see "1234" in the input "input type=number"

  Scenario: User can write into an <input type="password">
    Given I should see no value in the input "input type=password"
     When I write "supersecret" into the input "input type=password"
     Then I should see "supersecret" in the input "input type=password"

  Scenario: User can write into an <input type="search">
    Given I should see no value in the input "input type=search"
     When I write "supersecret" into the input "input type=search"
     Then I should see "supersecret" in the input "input type=search"

  Scenario: User can write into an <input type="tel">
    Given I should see no value in the input "input type=tel"
     When I write "8675309" into the input "input type=tel"
     Then I should see "8675309" in the input "input type=tel"

  Scenario: User can write into an <input type="text">
    Given I should see no value in the input "input type=text"
     When I write "some text" into the input "input type=text"
     Then I should see "some text" in the input "input type=text"

  Scenario: User can write into an <input type="time">
    Given I should see no value in the input "input type=time"
     When I write "0810AM" into the input "input type=time"
     Then I should see "08:10" in the input "input type=time"

  Scenario: User can write into an <input type="url">
    Given I should see no value in the input "input type=url"
     When I write "https://www.google.com" into the input "input type=url"
     Then I should see "https://www.google.com" in the input "input type=url"

  Scenario: User can write into an <input type="week">
    Given I should see no value in the input "input type=week"
     When I write "022012" into the input "input type=week"
     Then I should see "2012-W02" in the input "input type=week"

  Scenario: User can write into an <input> with label for
    Given I should see no value in the input "input with label for"
     When I write "boop" into the input "input with label for"
     Then I should see "boop" in the input "input with label for"

Feature: Fuzzy rules
  As a developer I want to make sure the fuzzy rules match the expected elements
  in order.

  Scenario: User gets the expected matching before from fuzzy
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/fuzzy_rules.html"
     Then I should see no value in the input "value:"
     When I click the button "button with inner text"
     Then I should see "button with inner text" in the input "value:"
     When I click the button "button with aria-label"
     Then I should see "button with aria-label" in the input "value:"
     When I click the button "button with child that has aria-label"
     Then I should see "button with child that has aria-label" in the input "value:"
     When I click the button "button with title"
     Then I should see "button with title" in the input "value:"
     When I click the button "button with placeholder"
     Then I should see "button with placeholder" in the input "value:"
     When I click the button "button with previous nested sibling label"
     Then I should see "button with previous nested sibling label" in the input "value:"
     When I should see the dropdown "Pick a color"
     Then I wait up to "1" seconds to see the following steps fail
       """
       When I select the option "Apple" from the dropdown "Pick a color"
       """

  Scenario: Exact-case match outranks caseless variants
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/fuzzy_case_rules.html"
     Then I should see no value in the input "value:"
     When I click the button "project"
     Then I should see "exact case lowercase" in the input "value:"
     When I click the button "PrOjEcT"
     Then I should see "crazy case PrOjEcT" in the input "value:"
     When I click the button "Project"
     Then I should see "title case Project" in the input "value:"

  Scenario: Caseless match locates the element when only different-case exists
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/fuzzy_case_rules.html"
     Then I should see no value in the input "value:"
     When I click the button "settings"
     Then I should see "Settings clicked" in the input "value:"
     When I click the button "SETTINGS"
     Then I should see "Settings clicked" in the input "value:"

  Scenario: Caseless match via attribute still works
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/fuzzy_case_rules.html"
     Then I should see no value in the input "value:"
     When I click the button "save"
     Then I should see "Save via aria-label" in the input "value:"

  Scenario: Caseless widening does not match unrelated text
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/fuzzy_case_rules.html"
     Then I should see no value in the input "value:"
     Then I wait up to "1" seconds to see the following steps fail
       """
       When I click the button "nonexistent-button-text"
       """

  Scenario: DOM order breaks ties among caseless matches
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/fuzzy_case_rules.html"
     Then I should see no value in the input "value:"
     When I click the button "dashboard"
     Then I should see "Dashboard first in DOM" in the input "value:"

  # Regression: "project"/"dashboard" only ever match query "R" caselessly
  # (immediate + caselesssubstring = 350, since removed - they now score 0),
  # while the real target only genuinely matches via a case-sensitive
  # attribute substring ("Reports" contains "R") scoring 289 - below that old
  # 350 ceiling. Before the fix, the decoys would incorrectly outrank the
  # real target; the removed tier no longer lets that happen.
  Scenario: Short query resolves to a genuine substring match, not an unrelated caseless-substring decoy
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/fuzzy_short_query.html"
     Then I should see no value in the input "value:"
     When I click the button "R"
     Then I should see "Reports icon clicked" in the input "value:"

  # Regression: the collapse-header ancestor has no direct text node of its
  # own - its content is a nested title span plus a sibling badge span, so
  # its full textContent concatenates to "File Changes3". nameInNestedChild
  # must score it against the inner span's own immediate text
  # ("File Changes"), not the badge-concatenated full text, or it scores as
  # a weak substring match (155) instead of an exact one (505) and loses to
  # the unrelated decoy button below (which exact-matches via aria-label at
  # 439).
  Scenario: Clickable ancestor is scored on inner text, not concatenated badge text
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/nested_badge_button.html"
     Then I should see no value in the input "value:"
     When I click the button "File Changes"
     Then I should see "File Changes clicked" in the input "value:"

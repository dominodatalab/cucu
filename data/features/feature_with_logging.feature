Feature: Feature with logging

  Scenario: Logging at various levels
    Given I log "hello" at level "info"
      And I log "cruel" at level "debug"
      And I log "world" at level "warn"

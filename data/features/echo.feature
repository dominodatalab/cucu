Feature: Echo

  Scenario: Echo an environment variable
    Given I echo "current shell is '{SHELL}'"
      And I echo the following:
      """
      current user is '{USER}'
      """
      And I echo "current working directory is '{PWD}'"
      And I echo the following:
      """
      \{
        "user": "{USER}"
      \}
      """
      And I log "hello {USER}" at level "info"
      And I log the following at level "info"
      """
      good bye {USER}
      """

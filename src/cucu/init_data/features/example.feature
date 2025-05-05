Feature: Cucu init feature
  We want new projects to have a least one feature file with a scenario
  Note: This is a comment, you can continue writing more comments here.
  Avoid starting a line with keywords like Given, When, Then, And, Scenario, Background, etc.

  You can also have blank lines between comments.

  @example @another-tag
  # The @sid- is just an example of a tag to mark this test with an id.
  @sid-314159
  Scenario: Example scenario
    This is a sample scenario using a fake page
    Normally you'd have your website somewhere and not use a static files like this.
    Note: The login step is custom, you'll need to implement it in your project.
    Given I start a webserver at directory "data/www" and save the port to the variable "PORT"
      And I open a browser at the url "http://localhost:{PORT}/example.html"
     When I login in with the username "{MY_SECRET_USERNAME}" and password as var "MY_SECRET_PASSWORD"
     Then I should see the text "Welcome {MY_SECRET_USERNAME} !"

from cucu import run_steps, step


@step(
    'I login in with the username "{username}" and password as var "{password_var}"'
)
def step_with_substeps_that_log(ctx, username, password_var):
    """This is an example of a step that uses substeps.

    You probably want write a login step anyways"""
    run_steps(
        ctx,
        f"""
        When I write "{username}" into the input "username"
         And I write "{{{password_var}}}" into the input "password"
         And I click the button "Login"
        Then I wait to see the text "Welcome {username} !"
         """,
    )


# TODO:
# - add a step that takes a table and prints it
# - add a step that takes a multiline string and prints it
# - add a step that looks up a html element by css selector
# - add a step that waits with retries

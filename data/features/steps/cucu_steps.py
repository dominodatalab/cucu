from cucu import retry, run_steps, step


@step('I use a step with substeps that log')
def step_with_substeps_that_log(context):
    run_steps(context, """
    When I echo "hello"
     And I echo "cruel"
     And I echo "world"
    """)


@step('I use a step with substeps')
def step_with_substeps(context):
    run_steps(context, """
    When I do nothing
     And I do nothing
     And I do nothing
    """)


@step('I use a step with substeps that fail')
def step_with_substeps_that_fail(context):
    run_steps(context, """
    When I fail
    """)


@step('I use a step with substeps that waits to fail')
def step_with_substeps_that_waits_to_fail(context):
    run_steps(context, """
    When I wait to fail
    """)


@step('I do nothing')
def do_nothing(_):
    pass


@step('I fail')
def i_fail(_):
    raise RuntimeError('step fails on purpose')


@step('I wait to fail')
def i_wait_to_fail(_):
    def fail():
        raise RuntimeError('step fails on purpose after a while')

    retry(fail)


@step('I search for "{query}" on google search')
def search_for_on_google(context, query):
    run_steps(context, f"""
    When I open a browser at the url "https://www.google.com/search"
     And I wait to write "{query}" into the input "Search"
     And I click the button "Google Search"
    """)

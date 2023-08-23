from cucu import step


@step("This is a custom step")
def custom_step_test(ctx):
    print("This is a test for custom step")

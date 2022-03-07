import os

from behave import step


@step('I create a file at "{filepath}" with the following')
def create_file_with_the_following(context, filepath):
    dirname = os.path.dirname(filepath)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(filepath, 'wb') as output:
        output.write(bytes(context.text, 'utf8'))


@step('I append to the file at "{filepath}" the following')
def append_to_file_the_following(context, filepath):
    with open(filepath, 'ab') as output:
        output.write(bytes(context.text, 'utf8'))


@step('I should see the file at "{filepath}" has the following')
def should_see_file_with_the_following(context, filepath):
    with open(filepath, 'rb') as input:
        file_contents = input.read().decode('utf8')

        if file_contents != context.text:
            raise RuntimeError(f'expected:\n{context.text}\nbut got:\n{file_contents}\n')

import os
import re

from cucu import retry, step
from cucu.config import CONFIG


@step('I create a file at "{filepath}" with the following')
def create_file_with_the_following(ctx, filepath):
    dirname = os.path.dirname(filepath)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(filepath, "wb") as output:
        output.write(bytes(ctx.text, "utf8"))


@step('I create the directory at "{filepath}"')
def create_directory_at(ctx, filepath):
    os.makedirs(filepath)


@step('I delete the file at "{filepath}"')
def delete_file_at(ctx, filepath):
    os.remove(filepath)


@step('I delete the file at "{filepath}" if it exists')
def delete_file_at_if_it_exists(ctx, filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


@step(
    'I read the contents of the file at "{filepath}" and save to the variable "{variable}"'
)
def read_file_contents(ctx, filepath, variable):
    with open(filepath, "r") as _input:
        CONFIG[variable] = CONFIG.escape(_input.read())


@step('I append to the file at "{filepath}" the following')
def append_to_file_the_following(ctx, filepath):
    with open(filepath, "ab") as output:
        output.write(bytes(ctx.text, "utf8"))


def assert_file(ctx, filepath):
    if not (os.path.exists(filepath) and os.path.isfile(filepath)):
        raise RuntimeError(f"unable to see file at {filepath}")


@step('I should see a file at "{filepath}"')
def should_see_file(ctx, filepath):
    assert_file(ctx, filepath)


@step('I should not see a file at "{filepath}"')
def should_not_see_file(ctx, filepath):
    if os.path.exists(filepath) and os.path.isfile(filepath):
        raise RuntimeError(f"able to see file at {filepath}")


@step('I wait to see a file at "{filepath}"')
def wait_to_see_file(ctx, filepath):
    retry(assert_file)(ctx, filepath)


@step('I wait up to "{seconds}" seconds to see a file at "{filepath}"')
def wait_up_to_see_file(ctx, seconds, filepath):
    seconds = float(seconds)
    retry(assert_file, wait_up_to_s=seconds)(ctx, filepath)


@step('I should see the directory at "{filepath}"')
def should_see_directory(ctx, filepath):
    if not (os.path.exists(filepath) and os.path.isdir(filepath)):
        raise RuntimeError(f"unable to see directory at {filepath}")


@step('I should not see the directory at "{filepath}"')
def should_not_see_directory(ctx, filepath):
    if os.path.exists(filepath) and os.path.isdir(filepath):
        raise RuntimeError(f"able to see directory at {filepath}")


@step('I should see the file at "{filepath}" is equal to the following')
def should_see_file_is_equal_to_the_following(ctx, filepath):
    with open(filepath, "rb") as input:
        file_contents = input.read().decode("utf8")

        if file_contents != ctx.text:
            raise RuntimeError(
                f"\n{file_contents}\nis not equal to\n{ctx.text}\n"
            )


@step('I should see the file at "{filepath}" contains the following')
def should_see_file_contains_the_following(ctx, filepath):
    with open(filepath, "rb") as input:
        file_contents = input.read().decode("utf8")

        if ctx.text not in file_contents:
            raise RuntimeError(
                f"\n{file_contents}\ndoes not contain\n{ctx.text}\n"
            )


@step('I should see the file at "{filepath}" matches the following')
def should_see_file_matches_the_following(ctx, filepath):
    with open(filepath, "rb") as input:
        file_contents = input.read().decode("utf8")

        if not re.match(ctx.text, file_contents):
            raise RuntimeError(
                f"\n{file_contents}\ndoes not match\n{ctx.text}\n"
            )


@step('I should see the file at "{filepath}" is not equal to the following')
def should_see_file_is_not_equal_to_the_following(ctx, filepath):
    with open(filepath, "rb") as input:
        file_contents = input.read().decode("utf8")

        if file_contents != ctx.text:
            raise RuntimeError(f"\n{file_contents}\nis equal to\n{ctx.text}\n")


@step('I should see the file at "{filepath}" does not contain the following')
def should_see_file_does_not_contain_the_following(ctx, filepath):
    with open(filepath, "rb") as input:
        file_contents = input.read().decode("utf8")

        if ctx.text in file_contents:
            raise RuntimeError(f"\n{file_contents}\ncontains\n{ctx.text}\n")


@step('I should see the file at "{filepath}" does not match the following')
def should_see_file_does_not_match_the_following(ctx, filepath):
    with open(filepath, "rb") as input:
        file_contents = input.read().decode("utf8")

        if re.match(ctx.text, file_contents):
            raise RuntimeError(f"\n{file_contents}\nmatches\n{ctx.text}\n")

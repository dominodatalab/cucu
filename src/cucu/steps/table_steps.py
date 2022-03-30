import pkgutil
import re

from cucu import retry, step


def find_tables(ctx):
    """
    find all the tables currently present on the page

    parameters:
      ctx(object): behave context object used to share data between steps

    returns:
      an array of arrays containing the HTML tables currently displayed
    """
    tables_lib = pkgutil.get_data("cucu", "steps/tables.js")
    tables_lib = tables_lib.decode("utf8")
    ctx.browser.execute(tables_lib)
    return ctx.browser.execute("return findAllTables();")


def behave_table_to_array(table):
    """
    given a behave.model.Table object convert it to an array of rows

    parameters:
        table(behave.model.Table): the behave table to convert into an array

    returns:
        array of rows representing the behave table provided.
    """
    result = []

    for row in table.rows:
        values = []
        for value in row:
            values.append(value)
        result.append(values)

    return result


def assert_has_table(expected_table, tables):
    """
    assert that the expected_table can be found exactly in the list of tables
    provided.

    parameters:
        expected_table(array): an array of arrays that represent a table
        tables(array): an array of tables

    raises:
        a RuntimeError if the expected_table is not found in the list of tables
    """
    if expected_table not in tables:
        raise RuntimeError("unable to find the desired table")


def assert_matches_table(expected_table, tables):
    """
    assert that a table that matches the regex patterns in the expected_table
    can be found in the list of tables provided.

    parameters:
        expected_table(array): an array of arrays that represent a table
        tables(array): an array of tables

    raises:
        a RuntimeError if the expected_table is not found in the list of tables
    """

    for table in tables:
        table_matched = True

        if len(table) == len(expected_table):
            for (expected_row, row) in zip(expected_table, table):
                for (expected_value, value) in zip(expected_row, row):
                    if not re.match(expected_value, value):
                        table_matched = False

            if table_matched:
                return

    raise RuntimeError("unable to find the desired matching table")


def assert_contains_table(expected_table, tables):
    """
    assert that a table that containing the rows of the expected_table can be
    found in the list of tables provided.

    parameters:
        expected_table(array): an array of arrays that represent a table
        tables(array): an array of tables

    raises:
        a RuntimeError if the expected_table is not found in the list of tables
    """
    for table in tables:
        # if I find all of the rows of the expected_table within another table
        if all(row in table for row in expected_table):
            return

    raise RuntimeError("unable to find the desired table")


def assert_contains_rows_matching_table(expected_table, tables):
    """
    assert that a table containing the rows that match the regex patterns in
    the expected_table can be found in the list of tables provided.

    parameters:
        expected_table(array): an array of arrays that represent a table
        tables(array): an array of tables

    raises:
        a RuntimeError if the expected_table is not found in the list of tables
    """
    for table in tables:
        table_matched = True

        for expected_row in expected_table:
            for row in table:
                found_row = True
                for (expected_value, value) in zip(expected_row, row):
                    if not re.match(expected_value, value):
                        found_row = False
                if found_row:
                    break

            if not found_row:
                table_matched = False
                break

        if table_matched:
            return

    raise RuntimeError("unable to find the desired matching table")


for (thing, assert_func) in {
    "is": assert_has_table,
    "matches": assert_matches_table,
    "contains": assert_contains_table,
    "contains rows matching": assert_contains_rows_matching_table,
}.items():

    @step(f"I should see a table that {thing} the following")
    def should_see_the_table(ctx, assert_func=assert_func):
        table = behave_table_to_array(ctx.table)
        tables = find_tables(ctx)
        assert_func(table, tables)

    @step(f"I wait to see a table that {thing} the following")
    def wait_to_see_the_table(ctx, assert_func=assert_func):
        table = behave_table_to_array(ctx.table)
        tables = find_tables(ctx)
        retry(assert_func)(table, tables)

    @step(
        f'I wait up to "{{seconds}}" seconds to see a table that {thing} the following'
    )
    def wait_up_to_seconds_to_see_the_table(
        ctx, seconds, assert_func=assert_func
    ):
        table = behave_table_to_array(ctx.table)
        tables = find_tables(ctx)
        seconds = float(seconds)
        retry(assert_func, wait_up_to_s=seconds)(table, tables)

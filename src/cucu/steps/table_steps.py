import pkgutil
import re

from behave.model_describe import ModelPrinter
from cucu import retry, step
from io import StringIO
from tabulate import tabulate, TableFormat, Line, DataRow


def find_tables(ctx):
    """
    find all the tables currently present on the page

    parameters:
      ctx(object): behave context object used to share data between steps

    returns:
      an array of arrays containing the HTML tables currently displayed
    """
    ctx.check_browser_initialized()
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
    result = [table.headings]

    for row in table.rows:
        values = []
        for value in row:
            values.append(value)
        result.append(values)

    return result


def check_table_equals_table(table, expected_table):
    """
    check that table is equal to expected_table
    """
    return table == expected_table


def check_table_matches_table(table, expected_table):
    """
    check if table matches the regex patterns in expected table
    """

    if len(table) == len(expected_table):
        table_matched = True

        for (expected_row, row) in zip(expected_table, table):
            for (expected_value, value) in zip(expected_row, row):
                if not re.match(expected_value, value):
                    table_matched = False

        if table_matched:
            return True

    return False


def check_table_contains_table(table, expected_table):
    """
    check that table contains the rows in expected_table
    """
    return all(row in table for row in expected_table)


def check_table_contains_matching_rows_in_table(table, expected_table):
    """
    check that table contains the matching rows in expected_table
    """
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
        return True

    return False


GHERKIN_TABLEFORMAT = TableFormat(
    lineabove=None,
    linebelowheader=None,
    linebetweenrows=None,
    linebelow=None,
    headerrow=DataRow("|", "|", "|"),
    datarow=DataRow("|", "|", "|"),
    padding=1,
    with_header_hide=["lineabove"],
)


def report_unable_to_find_table(tables):
    stream = StringIO()
    for table in tables:
        stream.write(f"\n{tabulate(table, [], tablefmt=GHERKIN_TABLEFORMAT)}\n")

    stream.seek(0)
    raise RuntimeError(f"unable to find desired table, found: {stream.read()}")


def find_table(ctx, assert_func, nth=None):
    """
    validate we can find the table passed in the ctx object and assert it
    matches anyone of the tables on the current web page. If `nth` is set to
    something then we only check against the nth table of the available tables.

    paramters:
        ctx(object): behave context object
        assert_func(function): function used to assert two tables "match"
        nth(int): when set to an int specifies the exact table within the list
                  of available tables to match against.

    raises:
        RuntimeError when the desired table was not found
    """
    expected = behave_table_to_array(ctx.table)
    tables = find_tables(ctx)

    if nth is not None:
        if assert_func(tables[nth], expected):
            return

    else:
        for table in tables:
            if assert_func(table, expected):
                return

    report_unable_to_find_table(tables)


def do_not_find_table(ctx, assert_func, nth=None):
    """
    validate we can not find the table passed in the ctx object and assert it
    matches anyone of the tables on the current web page. If `nth` is set to
    something then we only check against the nth table of the available tables.

    paramters:
        ctx(object): behave context object
        assert_func(function): function used to assert two tables "match"
        nth(int): when set to an int specifies the exact table within the list
                  of available tables to match against.

    raises:
        RuntimeError when the desired table was not found
    """
    expected = behave_table_to_array(ctx.table)
    tables = find_tables(ctx)

    if nth is not None:
        if not assert_func(tables[nth], expected):
            return

    else:
        for table in tables:
            if not assert_func(table, expected):
                return

    report_unable_to_find_table(tables)


for (thing, check_func) in {
    "is": check_table_equals_table,
    "matches": check_table_matches_table,
    "contains": check_table_contains_table,
    "contains rows matching": check_table_contains_matching_rows_in_table,
}.items():

    @step(f"I should see a table that {thing} the following")
    def should_see_the_table(ctx, check_func=check_func):
        find_table(ctx, check_func)

    @step(f"I should not see a table that {thing} the following")
    def should_not_see_the_table(ctx, check_func=check_func):
        do_not_find_table(ctx, check_func)

    @step(f"I wait to see a table that {thing} the following")
    def wait_to_see_the_table(ctx, check_func=check_func):
        retry(find_table)(ctx, check_func)

    @step(f"I wait to not see a table that {thing} the following")
    def wait_to_not_see_the_table(ctx, check_func=check_func):
        retry(do_not_find_table)(ctx, check_func)

    @step(
        f'I wait up to "{{seconds}}" seconds to see a table that {thing} the following'
    )
    def wait_up_to_seconds_to_see_the_table(
        ctx, seconds, check_func=check_func
    ):
        seconds = float(seconds)
        retry(find_table, wait_up_to_s=seconds)(ctx, check_func)

    @step(
        f'I wait up to "{{seconds}}" seconds to not see a table that {thing} the following'
    )
    def wait_up_to_seconds_to_not_see_the_table(
        ctx, seconds, check_func=check_func
    ):
        seconds = float(seconds)
        retry(do_not_find_table, wait_up_to_s=seconds)(ctx, check_func)

    @step(f'I should see the "{{nth}}" table {thing} the following')
    def should_see_the_nth_table(ctx, nth, check_func=check_func):
        find_table(ctx, check_func, nth=nth)

    @step(f'I wait to see the "{{nth}}" table {thing} the following')
    def wait_to_see_the_nth_table(ctx, nth, check_func=check_func):
        retry(find_table)(ctx, check_func, nth=nth)

    @step(
        f'I wait up to "{{seconds}}" seconds to see the "{{nth}}" table {thing} the following'
    )
    def wait_up_to_seconds_to_see_the_nth_table(
        ctx, seconds, nth, check_func=check_func
    ):
        seconds = float(seconds)
        retry(find_table, wait_up_to_s=seconds)(ctx, check_func, nth=nth)

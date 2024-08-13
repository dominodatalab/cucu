import pkgutil
import re
from io import StringIO

from selenium.webdriver.common.by import By

from cucu import (
    config,
    format_gherkin_table,
    fuzzy,
    helpers,
    logger,
    retry,
    step,
)
from cucu.browser.frames import run_in_all_frames


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

    def search_for_tables():
        ctx.browser.execute(tables_lib)
        return ctx.browser.execute("return findAllTables();")

    return run_in_all_frames(ctx.browser, search_for_tables)


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

        for expected_row, row in zip(expected_table, table):
            for expected_value, value in zip(expected_row, row):
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
            for expected_value, value in zip(expected_row, row):
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


def report_unable_to_find_table(expected_table, found_tables):
    stream = StringIO()
    stream.write("\n")
    for index, table in enumerate(found_tables):
        print_index = helpers.nth_to_ordinal(index) or '"1st" '
        stream.write(
            f"{print_index}table:\n{format_gherkin_table(table, [], '  ')}\n"
        )

    stream.seek(0)
    raise RuntimeError(
        f"unable to find desired table\nexpected:\n{format_gherkin_table(expected_table, [], '  ')}\n\nfound:{stream.read()}"
    )


def report_found_undesired_table(unexpected_tables, found_tables):
    stream = StringIO()
    stream.write("\n")
    for index, table in enumerate(found_tables):
        print_index = helpers.nth_to_ordinal(index) or '"1st" '
        stream.write(
            f"{print_index}table:\n{format_gherkin_table(table, [], '  ')}\n"
        )

    stream.seek(0)
    error_message = ""
    for table in unexpected_tables:
        error_message += (
            f"found undesired table\n\nundesired table:\n{format_gherkin_table(table, [], '  ')}\n\n"
            f"all tables found:{stream.read()}\n"
        )
    raise RuntimeError(error_message)


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
    found_tables = find_tables(ctx)

    if nth is not None:
        if assert_func(found_tables[nth], expected):
            return

    else:
        for table in found_tables:
            if assert_func(table, expected):
                return

    report_unable_to_find_table(expected, found_tables)


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
    matching_tables = []

    if nth is not None:
        if assert_func(tables[nth], expected):
            matching_tables.append(tables[nth])

    else:
        for table in tables:
            if assert_func(table, expected):
                matching_tables.append(table)

    # If none of the tables match the pattern, then return
    if len(matching_tables) == 0:
        return

    report_found_undesired_table(matching_tables, tables)


for thing, check_func in {
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


def find_table_header(ctx, name, index=0):
    """
    find a table header with the provided name
    """
    ctx.check_browser_initialized()
    return fuzzy.find(ctx.browser, name, ["th"], index=index)


def click_table_header(ctx, header):
    """
    internal method used to simply click a table header element
    """
    ctx.check_browser_initialized()
    ctx.browser.click(header)


helpers.define_action_on_thing_with_name_steps(
    "table header",
    "click",
    find_table_header,
    click_table_header,
    with_nth=True,
)


def get_table_cell_value(ctx, table, row, column, variable_name):
    tables = find_tables(ctx)

    try:
        cell_value = tables[table][row][column]
    except IndexError:
        raise RuntimeError(
            f"Cannot find table:{table+1},row:{row+1},column:{column+1}. Please check your table data."
        )
    config.CONFIG[variable_name] = cell_value


@step(
    'I save "{table:nth}" table, "{row:nth}" row, "{column:nth}" column value to a variable "{variable_name}"'
)
def step_get_table_cell_value(ctx, table, row, column, variable_name):
    get_table_cell_value(ctx, table, row, column, variable_name)


@step(
    'I wait to save "{table:nth}" table, "{row:nth}" row, "{column:nth}" column value to a variable "{variable_name}"'
)
def wait_to_get_table_cell_value(ctx, table, row, column, variable_name):
    retry(get_table_cell_value)(ctx, table, row, column, variable_name)


def find_table_element(ctx, nth=1):
    """
    Return the nth table as a WebElement

    parameters:
      ctx(object): behave context object used to share data between steps
      nth(int): specifies the exact table within the list of available tables to match against.
                Defaults to 1st table.

    returns:
      A selenium WebElement associated with the table that was specified
    """
    ctx.check_browser_initialized()

    try:
        return ctx.browser.css_find_elements("table")[nth]
    except IndexError:
        raise RuntimeError(
            f"Cannot find table:{nth+1}. Please check your table data."
        )


def click_table_cell(ctx, row, column, table):
    """
    Clicks the cell corresponding to the given row and column

    parameters:
      ctx(object): behave context object used to share data between steps
      row(int): the row of the table to click
      column(int): the column of the table to click
      table(int): specifies the exact table within the list of available tables to match against.
    """
    table_element = find_table_element(ctx, table)

    try:
        row = table_element.find_elements(By.CSS_SELECTOR, "tbody tr")[row]
        cell = row.find_elements(By.CSS_SELECTOR, "td")[column]
    except IndexError:
        raise RuntimeError(
            f"Cannot find table:{table+1},row:{row+1},column:{column+1}. Please check your table data."
        )
    ctx.browser.click(cell)


@step('I wait to click the "{row:nth}" row in the "{table:nth}" table')
def wait_click_table_row(ctx, row, table):
    """
    Add 1 to the row number if the table has a header row.

    Note: Firefox is unable to click directly on a row <tr> if it has child columns <td>.
    In order to workaround this, the step just clicks the first column <td> of the row <tr>.
    Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1448825
    """
    retry(click_table_cell)(ctx, row, 1, table)


@step(
    'I wait to click the cell corresponding to the "{row:nth}" row and "{column:nth}" column in the "{table:nth}" table'
)
def wait_click_table_cell(ctx, row, column, table):
    """
    Add 1 to the row number if the table has a header row.
    """
    retry(click_table_cell)(ctx, row, column, table)


@step(
    'I wait to click the "{column:nth}" column within a row that contains the text "{match_text}" in the "{table:nth}" table'
)
def wait_click_table_cell_matching_text(ctx, column, match_text, table):
    def click_table_cell_matching_text(ctx, column, match_text, table):
        table_element = find_table_element(ctx, table)

        try:
            row = table_element.find_elements(
                By.XPATH, f'//td[.="{match_text}"]/parent::tr'
            )
            if len(row) > 1:
                logger.warn(
                    f'Found {len(row)} rows with matching text "{match_text}", using the first row.'
                )
            cell = row[0].find_elements(By.CSS_SELECTOR, "td")[column]
        except IndexError:
            raise RuntimeError(
                f"Cannot find table:{table+1},column:{column+1},text:{match_text}. Please check your table data."
            )

        ctx.browser.click(cell)

    retry(click_table_cell_matching_text)(ctx, column, match_text, table)


@step('I wait to see there are "{row_count}" rows in the "{table:nth}" table')
def wait_table_row_count(ctx, row_count, table):
    """
    Add 1 to the row number if the table has a header row.
    """

    def find_table_row_count(ctx, row_count, table):
        table_element = find_table_element(ctx, table)
        table_rows = len(table_element.find_elements(By.CSS_SELECTOR, "tr"))

        if int(row_count) == table_rows:
            return
        else:
            raise RuntimeError(
                f"Unable to find {row_count} rows in table {table+1}. Please check your table data."
            )

    retry(find_table_row_count)(ctx, row_count, table)

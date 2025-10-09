# only thing your project requires to load cucu steps
import sqlite3

from selenium.webdriver.common.by import By

from cucu import logger, step
from cucu.steps.table_steps import (
    behave_table_to_array,
    check_table_matches_table,
    report_unable_to_find_table,
)


@step('I should see the element with id "{id}" has a child')
def should_see_the_element_with_id_has_a_child(ctx, id):
    # this code forces the frame switching code to switch out of the wrong
    # frame when looking for elements that happen to be in the default
    # (top level) frame
    frames = ctx.browser.execute('return document.querySelectorAll("iframe");')
    if frames:
        ctx.browser.switch_to_frame(frames[-1])

    element = ctx.browser.css_find_elements(f"*[id={id}]")[0]
    element.find_elements(By.CSS_SELECTOR, "*")[0]


@step(
    'I should see the db "{rundb_path}" query "{query}" table matches the following'
)
def i_query_the_run_db_with_the_query(ctx, rundb_path, query):
    expected = behave_table_to_array(ctx.table)

    found = []
    with sqlite3.connect(rundb_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        found.append(
            [column[0] for column in cursor.description]
        )  # column names
        results = [list(x) for x in cursor.fetchall()]
        for row in results:
            for ix, data in enumerate(row):
                if data is None:
                    row[ix] = ""

        found.extend(results)

    logger.debug(f"Query {query} returned {found}")
    result = check_table_matches_table(table=found, expected_table=expected)
    if not result:
        report_unable_to_find_table(expected, [found])

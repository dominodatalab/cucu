from unittest import TestCase, mock
import operator
import pytest

from cucu.steps.table_steps import (
    check_table_contains_matching_rows_in_table,
    do_not_find_table,
    find_table_matching_rows_and_validate_row_count,
    find_nth_table_and_validate_row_count,
)


class TestDoNotFindTable(TestCase):
    def __init__(self, method_name="runTest"):
        super().__init__(method_name)
        self.seen_tables = [
            [["", "", "✕"]],
            [
                ["", "NAME", "SIZE", "MODIFIED", ""],
                ["", "", "", "", ""],
                ["", "3GB_file.txt", "3.2 GB", "Dec 14, 2023 8:46 PM", ""],
            ],
        ]

    def test_do_not_find_table_error(self):
        # Assert that if ANY table matches the undesired table pattern, a RuntimeError is raised
        undesired_table = [
            ["", "NAME", "SIZE", "MODIFIED", ""],
            ["", "3GB_file\\.txt", ".*", ".*", ""],
        ]
        expected_mock = mock.MagicMock(return_value=undesired_table)
        with mock.patch(
            "cucu.steps.table_steps.behave_table_to_array", expected_mock
        ):
            seen_mock = mock.MagicMock(return_value=self.seen_tables)
            with mock.patch("cucu.steps.table_steps.find_tables", seen_mock):
                dummy = mock.MagicMock()
                with self.assertRaises(RuntimeError):
                    do_not_find_table(
                        dummy, check_table_contains_matching_rows_in_table
                    )

    def test_do_not_find_table(self):
        # Assert that if NO table matches the undesired table pattern, no exception is raised
        undesired_table = [
            ["", "NAME", "SIZE", "MODIFIED", ""],
            ["", "999GB_file\\.txt", ".*", ".*", ""],
        ]
        expected_mock = mock.MagicMock(return_value=undesired_table)
        with mock.patch(
            "cucu.steps.table_steps.behave_table_to_array", expected_mock
        ):
            seen_mock = mock.MagicMock(return_value=self.seen_tables)
            with mock.patch("cucu.steps.table_steps.find_tables", seen_mock):
                dummy = mock.MagicMock()
                result = do_not_find_table(
                    dummy, check_table_contains_matching_rows_in_table
                )
                self.assertIsNone(result)


@pytest.mark.parametrize(
    "thing,check_func,expected_rows,actual_rows,should_raise",
    [
        ("more than", operator.gt, 2, 3, False),
        ("more than", operator.gt, 2, 2, True),
        ("equals", operator.eq, 2, 2, False),
        ("equals", operator.eq, 2, 1, True),
        ("at least", operator.ge, 2, 2, False),
        ("at least", operator.ge, 2, 1, True),
        ("at most", operator.le, 2, 2, False),
        ("at most", operator.le, 2, 3, True),
        ("less than", operator.lt, 2, 1, False),
        ("less than", operator.lt, 2, 2, True),
        ("not equal to", operator.ne, 2, 3, False),
        ("not equal to", operator.ne, 2, 2, True),
    ]
)
def test_find_table_matching_rows_and_validate_row_count(thing, check_func, expected_rows, actual_rows, should_raise):
    with mock.patch(
        "cucu.steps.table_steps.find_table",
        return_value=[[1]] * actual_rows
    ):
        dummy_ctx = mock.MagicMock()
        
        if should_raise:
            with pytest.raises(RuntimeError) as context:
                find_table_matching_rows_and_validate_row_count(
                    dummy_ctx, None, expected_rows, thing, check_func
                )
            assert f"Expected {thing} {expected_rows} rows" in str(context.value)
            assert f"but found {actual_rows} instead" in str(context.value)
        else:
            # Should not raise any exception
            result = find_table_matching_rows_and_validate_row_count(
                dummy_ctx, None, expected_rows, thing, check_func
            )
            assert result is None


@pytest.mark.parametrize(
    "thing,check_func,expected_rows,actual_rows,should_raise",
    [
        ("more than", operator.gt, 2, 3, False),
        ("more than", operator.gt, 2, 2, True),
        ("equals", operator.eq, 2, 2, False),
        ("equals", operator.eq, 2, 1, True),
        ("at least", operator.ge, 2, 2, False),
        ("at least", operator.ge, 2, 1, True),
        ("at most", operator.le, 2, 2, False),
        ("at most", operator.le, 2, 3, True),
        ("less than", operator.lt, 2, 1, False),
        ("less than", operator.lt, 2, 2, True),
        ("not equal to", operator.ne, 2, 3, False),
        ("not equal to", operator.ne, 2, 2, True),
    ]
)
def test_find_nth_table_and_validate_row_count(thing, check_func, expected_rows, actual_rows, should_raise):
    mock_table_element = mock.MagicMock()
    
    with mock.patch(
        "cucu.steps.table_steps.find_table_element",
        return_value=mock_table_element
    ), mock.patch(
        "cucu.steps.table_steps.count_rows_in_table_element",
        return_value=actual_rows
    ):
        dummy_ctx = mock.MagicMock()
        table_index = 0
        
        if should_raise:
            with pytest.raises(RuntimeError) as context:
                find_nth_table_and_validate_row_count(
                    dummy_ctx, table_index, thing, check_func, expected_rows
                )
            assert f"Expected {thing} {expected_rows} rows in table {table_index + 1}" in str(context.value)
            assert f"but found {actual_rows} instead" in str(context.value)
        else:
            # Should not raise any exception
            result = find_nth_table_and_validate_row_count(
                dummy_ctx, table_index, thing, check_func, expected_rows
            )
            assert result is None

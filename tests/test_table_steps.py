from unittest import TestCase, mock

from cucu.steps.table_steps import (
    check_table_contains_matching_rows_in_table,
    do_not_find_table,
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

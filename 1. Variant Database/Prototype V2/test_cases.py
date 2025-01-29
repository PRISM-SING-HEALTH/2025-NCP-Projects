import pandas as pd
import numpy as np
import yaml

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os

class TestLoadConfig(unittest.TestCase):
    def setUp(self):
        """
        Set up temporary files and test data.
        """
        self.valid_config = {
            'base_path': '/data/',
            'local_path': '/local/',
            'files': {
                'file1': 'file1.xlsx',
                'file2': 'file2.xlsx'
            }
        }

        self.missing_keys_config = {
            'base_path': '/data/',
            'files': {
                'file1': 'file1.xlsx'
            }
        }

        # Create temporary YAML files for testing
        self.valid_config_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        self.valid_config_file.write(yaml.dump(self.valid_config).encode())
        self.valid_config_file.close()

        self.missing_keys_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        self.missing_keys_file.write(yaml.dump(self.missing_keys_config).encode())
        self.missing_keys_file.close()

        self.invalid_yaml_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        self.invalid_yaml_file.write(b"{invalid_yaml: [missing, closing, brace")
        self.invalid_yaml_file.close()

        self.nonexistent_file = '/nonexistent/config.yaml'

    def tearDown(self):
        """
        Clean up temporary files after tests.
        """
        os.remove(self.valid_config_file.name)
        os.remove(self.missing_keys_file.name)
        os.remove(self.invalid_yaml_file.name)

    def test_valid_config(self):
        """
        Test that a valid configuration file is loaded successfully.
        """
        print("\nTest Case: Valid config file loaded.")
        config = load_config(self.valid_config_file.name)
        self.assertEqual(config, self.valid_config)

    def test_missing_keys(self):
        """
        Test that a configuration file with missing keys raises a ValueError.
        """
        print("\nTest Case: Missing keys.")
        with self.assertRaises(ValueError) as context:
            load_config(self.missing_keys_file.name)
        self.assertIn("Missing required configuration keys", str(context.exception))

    def test_invalid_yaml(self):
        """
        Test that an invalid YAML file raises a yaml.YAMLError.
        """
        print("\nTest Case: Invalid YAML file.")
        with self.assertRaises(yaml.YAMLError):
            load_config(self.invalid_yaml_file.name)

    def test_file_not_found(self):
        """
        Test that a non-existent file raises a FileNotFoundError.
        """
        print("\nTest Case: File not found.")
        with self.assertRaises(FileNotFoundError):
            load_config(self.nonexistent_file)

class TestStandardiseDataFrame(unittest.TestCase):
    def setUp(self):
        # Define a sample DataFrame and standard columns
        self.input_df = pd.DataFrame({
            "A": [1, 2, 3],
            "B": [4, 5, 6],
            "C": [7, 8, 9]
        })

        self.standard_columns = ["A", "B", "C", "D", "E"]  # Standardised columns to test against

    def test_standardise_dataframe_adds_missing_columns(self):
        """
        Test that missing columns are added with NaN values.
        """
        print("\nTest Case: Missing columns added with NaN values.")
        result_df = standardise_dataframe(self.input_df, self.standard_columns)

        # Check that the columns in the result match the standard columns
        self.assertListEqual(list(result_df.columns), self.standard_columns)

        # Check that the new columns contain NaN
        self.assertTrue(result_df["D"].isnull().all())
        self.assertTrue(result_df["E"].isnull().all())

    def test_standardise_dataframe_removes_extra_columns(self):
        """
        Test that extra columns in the input DataFrame are removed.
        """
        print("\nTest Case: Extra columns in input dataframe are removed.")
        result_df = standardise_dataframe(self.input_df, ["A", "B"])  # Subset of standard columns

        # Check that only the specified columns remain
        self.assertListEqual(list(result_df.columns), ["A", "B"])

    def test_standardise_dataframe_keeps_original_data(self):
        """
        Test that the original data in the columns is preserved.
        """
        print("\nTest Case: Original data in columns is preserved.")
        result_df = standardise_dataframe(self.input_df, self.standard_columns)

        # Check that data in original columns remains unchanged
        pd.testing.assert_series_equal(result_df["A"], self.input_df["A"])
        pd.testing.assert_series_equal(result_df["B"], self.input_df["B"])
        pd.testing.assert_series_equal(result_df["C"], self.input_df["C"])

    def test_standardise_dataframe_empty_dataframe(self):
        """
        Test behavior with an empty input DataFrame.
        """
        print("\nTest Case: Empty input dataframe.")
        empty_df = pd.DataFrame()
        result_df = standardise_dataframe(empty_df, self.standard_columns)

        # Check that all standard columns are present and filled with NaN
        self.assertListEqual(list(result_df.columns), self.standard_columns)
        self.assertTrue(result_df.isnull().all().all())

    def test_standardise_dataframe_no_columns(self):
        """
        Test behavior when no columns are specified.
        """
        print("\nTest Case: No column specified.")
        result_df = standardise_dataframe(self.input_df, [])

        # Check that the resulting DataFrame has no columns
        self.assertTrue(result_df.empty)
        self.assertListEqual(list(result_df.columns), [])

class TestQueryFunction(unittest.TestCase):
    def setUp(self):
        # Sample DataFrame for testing
        self.df = pd.DataFrame({
            'CategoryA': ['Apple', 'Banana', 'Cherry', 'Apple Pie'],
            'CategoryB': ['Dog', 'Cat', 'Horse', 'Fish']
        })

    @patch('builtins.input', side_effect=['CategoryA', 'Apple'])
    def test_valid_query_case_insensitive(self, mock_input):
        """
        Test valid query with case-insensitive comparison.
        """
        print("\nTest Case: Valid query with case-insensitive comparison")
        result = query(self.df)
        expected = self.df[self.df['CategoryA'].str.contains('Apple', case=False, na=False)]
        pd.testing.assert_frame_equal(result, expected)

    @patch('builtins.input', side_effect=['CategoryB', 'cat'])
    def test_valid_query_substring_search(self, mock_input):
        """
        Test valid query with substring matching.
        """
        print("\nTest Case: Valid query with substring matching")
        result = query(self.df)
        expected = self.df[self.df['CategoryB'].str.contains('cat', case=False, na=False)]
        pd.testing.assert_frame_equal(result, expected)

    @patch('builtins.input', side_effect=['InvalidCategory', 'Apple'])
    def test_invalid_category(self, mock_input):
        """
        Test querying an invalid category.
        """
        print("\nTest Case: Invalid category")
        result = query(self.df)
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=['CategoryA', 'NonexistentItem'])
    def test_no_results_found(self, mock_input):
        """
        Test querying an item that doesn't exist in the DataFrame.
        """
        print("\nTest Case: No results found.")
        result = query(self.df)
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=['CategoryA', ''])
    def test_empty_item(self, mock_input):
        """
        Test querying with an empty item.
        """
        print("\nTest Case: Empty item.")
        result = query(self.df)
        self.assertIsNone(result)

class TestExportToExcel(unittest.TestCase):
    def setUp(self):
        # Sample DataFrame for testing
        self.sample_df = pd.DataFrame({
            "A": [1, 2, None],
            "B": ["Test", None, "Data"]
        })
        self.output_path = "test_output.xlsx"

    @patch("pandas.DataFrame.to_excel")
    def test_export_to_excel_success(self, mock_to_excel):
        """
        Test successful export of DataFrame to an Excel file.
        """
        print("\nTest Case: Export dataframe to excel file.")
        # Call the function
        export_to_excel(self.sample_df, self.output_path)

        # Assert that `to_excel` was called with correct arguments
        mock_to_excel.assert_called_once_with(self.output_path, index=False)

    @patch("pandas.DataFrame.to_excel", side_effect=PermissionError("Permission denied"))
    def test_export_to_excel_permission_error(self, mock_to_excel):
        """
        Test export when a PermissionError occurs.
        """
        print("\nTest Case: Export with PermissionError.")
        with self.assertRaises(PermissionError):
            export_to_excel(self.sample_df, self.output_path)

    def tearDown(self):
        # Clean up the test output file if it was accidentally created
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False) # Run tests without exiting

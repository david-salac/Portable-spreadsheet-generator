import unittest
import json

import tempfile
import os
import copy

import numpy as np

from portable_spreadsheet.spreadsheet import Spreadsheet


class TestSerialization(unittest.TestCase):
    """Regression test for serializers."""

    def setUp(self) -> None:
        self.warnings = []
        self.nr_row = 5
        self.nr_col = 4
        self.rows_labels = [f"R_{r_i}" for r_i in range(self.nr_row)]
        self.columns_labels = [f"NL_C_{c_i}" for c_i in range(self.nr_col)]
        self.rows_help_text = [f"HT_R_{r_i}" for r_i in range(self.nr_row)]
        self.columns_help_text = [f"HT_C_{c_i}" for c_i in range(self.nr_col)]
        self.native_rows = [f"NL_R_{r_i}" for r_i in range(self.nr_row)]
        self.native_cols = [f"NL_C_{c_i}" for c_i in range(self.nr_col)]
        self.sheet = Spreadsheet.create_new_sheet(
            self.nr_row, self.nr_col, {
                'native': (
                    self.native_rows,
                    self.native_cols
                )
            },
            rows_labels=self.rows_labels,
            columns_labels=self.columns_labels,
            rows_help_text=self.rows_help_text,
            columns_help_text=self.columns_help_text,
            excel_append_row_labels=True,
            excel_append_column_labels=True,
            warning_logger=lambda message: self.warnings.append(message)
        )
        self.sheet_shape = (self.nr_row, self.nr_col)
        # Add some random values:
        self.inserted_rand_values: np.ndarray = np.array(
            [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12],
             [13, 14, 15, 16], [17, 18, 19, 20]]
        )
        self.sheet.iloc[:, :] = self.inserted_rand_values
        # Add some descriptions:
        for row_idx in range(self.nr_row):
            for col_idx in range(self.nr_col):
                self.sheet.iloc[row_idx, col_idx].description = \
                    f"DescFor{row_idx},{col_idx}"
        # Temporary directory for file exports
        self.working_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        """Remove temporary directory content."""
        for file in [
            f for f in os.listdir(self.working_dir)
            if os.path.isfile(os.path.join(self.working_dir, f))
        ]:
            os.remove(os.path.join(self.working_dir, file))

    def test_to_excel(self):
        """Test if the Excel file is created."""
        file_name = "export.xlsx"
        excel_path = os.path.join(self.working_dir, file_name)
        self.sheet.to_excel(excel_path)
        self.assertTrue(os.path.exists(excel_path))

    def test_to_dictionary(self):
        """Test export to dictionary"""
        expected = {'table': {'data': {'rows': {'R_0': {'columns': {'NL_C_0': {'excel': '1', 'python_numpy': '1', 'native': '1', 'value': 1, 'description': 'DescFor0,0', 'column_description': 'HT_C_0'}, 'NL_C_1': {'excel': '2', 'python_numpy': '2', 'native': '2', 'value': 2, 'description': 'DescFor0,1', 'column_description': 'HT_C_1'}, 'NL_C_2': {'excel': '3', 'python_numpy': '3', 'native': '3', 'value': 3, 'description': 'DescFor0,2', 'column_description': 'HT_C_2'}, 'NL_C_3': {'excel': '4', 'python_numpy': '4', 'native': '4', 'value': 4, 'description': 'DescFor0,3', 'column_description': 'HT_C_3'}}, 'row_description': 'HT_R_0'}, 'R_1': {'columns': {'NL_C_0': {'excel': '5', 'python_numpy': '5', 'native': '5', 'value': 5, 'description': 'DescFor1,0', 'column_description': 'HT_C_0'}, 'NL_C_1': {'excel': '6', 'python_numpy': '6', 'native': '6', 'value': 6, 'description': 'DescFor1,1', 'column_description': 'HT_C_1'}, 'NL_C_2': {'excel': '7', 'python_numpy': '7', 'native': '7', 'value': 7, 'description': 'DescFor1,2', 'column_description': 'HT_C_2'}, 'NL_C_3': {'excel': '8', 'python_numpy': '8', 'native': '8', 'value': 8, 'description': 'DescFor1,3', 'column_description': 'HT_C_3'}}, 'row_description': 'HT_R_1'}, 'R_2': {'columns': {'NL_C_0': {'excel': '9', 'python_numpy': '9', 'native': '9', 'value': 9, 'description': 'DescFor2,0', 'column_description': 'HT_C_0'}, 'NL_C_1': {'excel': '10', 'python_numpy': '10', 'native': '10', 'value': 10, 'description': 'DescFor2,1', 'column_description': 'HT_C_1'}, 'NL_C_2': {'excel': '11', 'python_numpy': '11', 'native': '11', 'value': 11, 'description': 'DescFor2,2', 'column_description': 'HT_C_2'}, 'NL_C_3': {'excel': '12', 'python_numpy': '12', 'native': '12', 'value': 12, 'description': 'DescFor2,3', 'column_description': 'HT_C_3'}}, 'row_description': 'HT_R_2'}, 'R_3': {'columns': {'NL_C_0': {'excel': '13', 'python_numpy': '13', 'native': '13', 'value': 13, 'description': 'DescFor3,0', 'column_description': 'HT_C_0'}, 'NL_C_1': {'excel': '14', 'python_numpy': '14', 'native': '14', 'value': 14, 'description': 'DescFor3,1', 'column_description': 'HT_C_1'}, 'NL_C_2': {'excel': '15', 'python_numpy': '15', 'native': '15', 'value': 15, 'description': 'DescFor3,2', 'column_description': 'HT_C_2'}, 'NL_C_3': {'excel': '16', 'python_numpy': '16', 'native': '16', 'value': 16, 'description': 'DescFor3,3', 'column_description': 'HT_C_3'}}, 'row_description': 'HT_R_3'}, 'R_4': {'columns': {'NL_C_0': {'excel': '17', 'python_numpy': '17', 'native': '17', 'value': 17, 'description': 'DescFor4,0', 'column_description': 'HT_C_0'}, 'NL_C_1': {'excel': '18', 'python_numpy': '18', 'native': '18', 'value': 18, 'description': 'DescFor4,1', 'column_description': 'HT_C_1'}, 'NL_C_2': {'excel': '19', 'python_numpy': '19', 'native': '19', 'value': 19, 'description': 'DescFor4,2', 'column_description': 'HT_C_2'}, 'NL_C_3': {'excel': '20', 'python_numpy': '20', 'native': '20', 'value': 20, 'description': 'DescFor4,3', 'column_description': 'HT_C_3'}}, 'row_description': 'HT_R_4'}}}, 'variables': {}, 'row-labels': ['R_0', 'R_1', 'R_2', 'R_3', 'R_4'], 'column-labels': ['NL_C_0', 'NL_C_1', 'NL_C_2', 'NL_C_3']}}  # noqa
        self.assertDictEqual(expected, self.sheet.to_dictionary())

    def test_to_csv(self):
        """Test export to CSV"""
        # Expected value with labels
        expected_no_skip = """Sheet,NL_C_0,NL_C_1,NL_C_2,NL_C_3
R_0,1,2,3,4
R_1,5,6,7,8
R_2,9,10,11,12
R_3,13,14,15,16
R_4,17,18,19,20"""
        # Expected value without labels
        expected_skip = """1,2,3,4
5,6,7,8
9,10,11,12
13,14,15,16
17,18,19,20"""
        self.assertEqual(self.sheet.to_csv(), expected_no_skip)
        self.assertEqual(self.sheet.to_csv(skip_labels=True),
                         expected_skip)

    def test_to_markdown(self):
        """MD (Markdown) language export"""
        expected_no_skip = """| *Sheet* | *NL_C_0* | *NL_C_1* | *NL_C_2* | *NL_C_3* |
|----|----|----|----|----|
| *R_0* | 1 | 2 | 3 | 4 |
| *R_1* | 5 | 6 | 7 | 8 |
| *R_2* | 9 | 10 | 11 | 12 |
| *R_3* | 13 | 14 | 15 | 16 |
| *R_4* | 17 | 18 | 19 | 20 |
"""

        expected_skip = """||||||
|----|----|----|----|
| 1 | 2 | 3 | 4 |
| 5 | 6 | 7 | 8 |
| 9 | 10 | 11 | 12 |
| 13 | 14 | 15 | 16 |
| 17 | 18 | 19 | 20 |
"""
        self.assertEqual(self.sheet.to_markdown(), expected_no_skip)
        self.assertEqual(self.sheet.to_markdown(skip_labels=True),
                         expected_skip)

    def test_to_html_table(self):
        """Test the export to the HTML table"""
        expected_no_skip = '<table><tr><th>Sheet</th><th><a href="javascript:;"  title="HT_C_0">NL_C_0</a></th><th><a href="javascript:;"  title="HT_C_1">NL_C_1</a></th><th><a href="javascript:;"  title="HT_C_2">NL_C_2</a></th><th><a href="javascript:;"  title="HT_C_3">NL_C_3</a></th></tr><tr><td><a href="javascript:;"  title="HT_R_0">R_0</a></td><td><a href="javascript:;"  title="DescFor0,0">1</a></td><td><a href="javascript:;"  title="DescFor0,1">2</a></td><td><a href="javascript:;"  title="DescFor0,2">3</a></td><td><a href="javascript:;"  title="DescFor0,3">4</a></td></tr><tr><td><a href="javascript:;"  title="HT_R_1">R_1</a></td><td><a href="javascript:;"  title="DescFor1,0">5</a></td><td><a href="javascript:;"  title="DescFor1,1">6</a></td><td><a href="javascript:;"  title="DescFor1,2">7</a></td><td><a href="javascript:;"  title="DescFor1,3">8</a></td></tr><tr><td><a href="javascript:;"  title="HT_R_2">R_2</a></td><td><a href="javascript:;"  title="DescFor2,0">9</a></td><td><a href="javascript:;"  title="DescFor2,1">10</a></td><td><a href="javascript:;"  title="DescFor2,2">11</a></td><td><a href="javascript:;"  title="DescFor2,3">12</a></td></tr><tr><td><a href="javascript:;"  title="HT_R_3">R_3</a></td><td><a href="javascript:;"  title="DescFor3,0">13</a></td><td><a href="javascript:;"  title="DescFor3,1">14</a></td><td><a href="javascript:;"  title="DescFor3,2">15</a></td><td><a href="javascript:;"  title="DescFor3,3">16</a></td></tr><tr><td><a href="javascript:;"  title="HT_R_4">R_4</a></td><td><a href="javascript:;"  title="DescFor4,0">17</a></td><td><a href="javascript:;"  title="DescFor4,1">18</a></td><td><a href="javascript:;"  title="DescFor4,2">19</a></td><td><a href="javascript:;"  title="DescFor4,3">20</a></td></tr></table>'  # noqa
        expected_skip = '<table><tr><td><a href="javascript:;"  title="DescFor0,0">1</a></td><td><a href="javascript:;"  title="DescFor0,1">2</a></td><td><a href="javascript:;"  title="DescFor0,2">3</a></td><td><a href="javascript:;"  title="DescFor0,3">4</a></td></tr><tr><td><a href="javascript:;"  title="DescFor1,0">5</a></td><td><a href="javascript:;"  title="DescFor1,1">6</a></td><td><a href="javascript:;"  title="DescFor1,2">7</a></td><td><a href="javascript:;"  title="DescFor1,3">8</a></td></tr><tr><td><a href="javascript:;"  title="DescFor2,0">9</a></td><td><a href="javascript:;"  title="DescFor2,1">10</a></td><td><a href="javascript:;"  title="DescFor2,2">11</a></td><td><a href="javascript:;"  title="DescFor2,3">12</a></td></tr><tr><td><a href="javascript:;"  title="DescFor3,0">13</a></td><td><a href="javascript:;"  title="DescFor3,1">14</a></td><td><a href="javascript:;"  title="DescFor3,2">15</a></td><td><a href="javascript:;"  title="DescFor3,3">16</a></td></tr><tr><td><a href="javascript:;"  title="DescFor4,0">17</a></td><td><a href="javascript:;"  title="DescFor4,1">18</a></td><td><a href="javascript:;"  title="DescFor4,2">19</a></td><td><a href="javascript:;"  title="DescFor4,3">20</a></td></tr></table>'  # noqa
        self.assertEqual(self.sheet.to_html_table(), expected_no_skip)
        self.assertEqual(self.sheet.to_html_table(skip_labels=True),
                         expected_skip)

    def test_to_json(self):
        """Test export to JSON"""
        expected: str = '{"table": {"data": {"rows": {"R_0": {"columns": {"NL_C_0": {"excel": "1", "python_numpy": "1", "native": "1", "value": 1, "description": "DescFor0,0", "column_description": "HT_C_0"}, "NL_C_1": {"excel": "2", "python_numpy": "2", "native": "2", "value": 2, "description": "DescFor0,1", "column_description": "HT_C_1"}, "NL_C_2": {"excel": "3", "python_numpy": "3", "native": "3", "value": 3, "description": "DescFor0,2", "column_description": "HT_C_2"}, "NL_C_3": {"excel": "4", "python_numpy": "4", "native": "4", "value": 4, "description": "DescFor0,3", "column_description": "HT_C_3"}}, "row_description": "HT_R_0"}, "R_1": {"columns": {"NL_C_0": {"excel": "5", "python_numpy": "5", "native": "5", "value": 5, "description": "DescFor1,0", "column_description": "HT_C_0"}, "NL_C_1": {"excel": "6", "python_numpy": "6", "native": "6", "value": 6, "description": "DescFor1,1", "column_description": "HT_C_1"}, "NL_C_2": {"excel": "7", "python_numpy": "7", "native": "7", "value": 7, "description": "DescFor1,2", "column_description": "HT_C_2"}, "NL_C_3": {"excel": "8", "python_numpy": "8", "native": "8", "value": 8, "description": "DescFor1,3", "column_description": "HT_C_3"}}, "row_description": "HT_R_1"}, "R_2": {"columns": {"NL_C_0": {"excel": "9", "python_numpy": "9", "native": "9", "value": 9, "description": "DescFor2,0", "column_description": "HT_C_0"}, "NL_C_1": {"excel": "10", "python_numpy": "10", "native": "10", "value": 10, "description": "DescFor2,1", "column_description": "HT_C_1"}, "NL_C_2": {"excel": "11", "python_numpy": "11", "native": "11", "value": 11, "description": "DescFor2,2", "column_description": "HT_C_2"}, "NL_C_3": {"excel": "12", "python_numpy": "12", "native": "12", "value": 12, "description": "DescFor2,3", "column_description": "HT_C_3"}}, "row_description": "HT_R_2"}, "R_3": {"columns": {"NL_C_0": {"excel": "13", "python_numpy": "13", "native": "13", "value": 13, "description": "DescFor3,0", "column_description": "HT_C_0"}, "NL_C_1": {"excel": "14", "python_numpy": "14", "native": "14", "value": 14, "description": "DescFor3,1", "column_description": "HT_C_1"}, "NL_C_2": {"excel": "15", "python_numpy": "15", "native": "15", "value": 15, "description": "DescFor3,2", "column_description": "HT_C_2"}, "NL_C_3": {"excel": "16", "python_numpy": "16", "native": "16", "value": 16, "description": "DescFor3,3", "column_description": "HT_C_3"}}, "row_description": "HT_R_3"}, "R_4": {"columns": {"NL_C_0": {"excel": "17", "python_numpy": "17", "native": "17", "value": 17, "description": "DescFor4,0", "column_description": "HT_C_0"}, "NL_C_1": {"excel": "18", "python_numpy": "18", "native": "18", "value": 18, "description": "DescFor4,1", "column_description": "HT_C_1"}, "NL_C_2": {"excel": "19", "python_numpy": "19", "native": "19", "value": 19, "description": "DescFor4,2", "column_description": "HT_C_2"}, "NL_C_3": {"excel": "20", "python_numpy": "20", "native": "20", "value": 20, "description": "DescFor4,3", "column_description": "HT_C_3"}}, "row_description": "HT_R_4"}}}, "variables": {}, "row-labels": ["R_0", "R_1", "R_2", "R_3", "R_4"], "column-labels": ["NL_C_0", "NL_C_1", "NL_C_2", "NL_C_3"]}}'  # noqa
        expected_parsed_dict: dict = json.loads(expected)
        computed_parsed_dict: dict = json.loads(self.sheet.to_json())
        self.assertDictEqual(expected_parsed_dict, computed_parsed_dict)


class TestSerializationToArrays(unittest.TestCase):
    """Test to_numpy serializer."""

    def setUp(self) -> None:
        self.warnings = []
        self.nr_row = 20
        self.nr_col = 30
        self.rows_labels = [f"R_{r_i}" for r_i in range(self.nr_row)]
        self.columns_labels = [f"NL_C_{c_i}" for c_i in range(self.nr_col)]
        self.rows_help_text = [f"HT_R_{r_i}" for r_i in range(self.nr_row)]
        self.columns_help_text = [f"HT_C_{c_i}" for c_i in range(self.nr_col)]
        self.native_rows = [f"NL_R_{r_i}" for r_i in range(self.nr_row)]
        self.native_cols = [f"NL_C_{c_i}" for c_i in range(self.nr_col)]
        self.sheet = Spreadsheet.create_new_sheet(
            self.nr_row, self.nr_col, {
                'native': (
                    self.native_rows,
                    self.native_cols
                )
            },
            rows_labels=self.rows_labels,
            columns_labels=self.columns_labels,
            rows_help_text=self.rows_help_text,
            columns_help_text=self.columns_help_text,
            excel_append_row_labels=True,
            excel_append_column_labels=True,
            warning_logger=lambda message: self.warnings.append(message)
        )
        self.sheet_shape = (self.nr_row, self.nr_col)
        # Add some random values:
        self.inserted_rand_values: np.ndarray = \
            np.random.random(self.sheet_shape) * 1_000
        self.sheet.iloc[:, :] = self.inserted_rand_values

    def test_to_numpy(self):
        """Test exporting to NumPy"""
        self.assertTrue(np.allclose(self.sheet.to_numpy(),
                                    self.inserted_rand_values))

    def test_to_2d_list(self):
        """Test the serialization to 2D list"""
        # Check values
        computed_2d_list = self.sheet.to_2d_list(skip_labels=True)
        self.assertTrue(isinstance(computed_2d_list, list))
        self.assertTrue(
            np.allclose(np.array(computed_2d_list), self.inserted_rand_values)
            )
        # Check labels:
        corner = "yMq7W0bk"
        computed_2d_list = self.sheet.to_2d_list(skip_labels=False,
                                                 top_right_corner_text=corner)
        self.assertTrue(isinstance(computed_2d_list, list))
        self.assertTrue(computed_2d_list[0][0], corner)
        # Check row labels
        for row_idx, row_label in enumerate(
                self.sheet.cell_indices.rows_labels):
            self.assertEqual(computed_2d_list[row_idx + 1][0], row_label)
        # Check column labels
        for col_idx, col_label in enumerate(
                self.sheet.cell_indices.columns_labels):
            self.assertEqual(computed_2d_list[0][col_idx + 1], col_label)
        # Check values inside:
        computed = [arr[1:] for arr in computed_2d_list[1:]]
        self.assertTrue(
            np.allclose(np.array(computed), self.inserted_rand_values)
        )
        # Check the language export
        sheet = copy.deepcopy(self.sheet)
        sheet.iloc[0, 0] = sheet.iloc[0, 1] * sheet.iloc[1, 0]
        computed_2d_list = sheet.to_2d_list(skip_labels=True,
                                            language='excel')
        # Regression test
        self.assertEqual(sheet.iloc[0, 0].parse['excel'], '=C2*B3')
        # Test all the values inside
        for row_idx in range(sheet.shape[0]):
            for col_idx in range(sheet.shape[1]):
                computed = computed_2d_list[row_idx][col_idx]
                expected = sheet.iloc[row_idx, col_idx].parse['excel']
                self.assertEqual(expected, computed)

    def test_to_string_of_values(self):
        """Test the serialization to 2D list"""
        computed_2d_list = self.sheet.to_string_of_values()
        self.assertTrue(isinstance(computed_2d_list, str))
        evaluated_list = eval(computed_2d_list)
        self.assertTrue(
            np.allclose(np.array(evaluated_list), self.inserted_rand_values)
            )

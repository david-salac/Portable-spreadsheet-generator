import unittest
import tempfile
import pathlib
import json
import shutil

from portable_spreadsheet.work_book import WorkBook, \
    ExcelParameters, DictionaryParameters, ListParameters
from portable_spreadsheet.sheet import Sheet


class TestGrammarUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.names = ['ABC', 'EFG']
        self.sheet_a = Sheet.create_new_sheet(5, 5, name=self.names[0])
        self.sheet_b = Sheet.create_new_sheet(5, 5, name=self.names[1])
        self.workbook = WorkBook(self.sheet_a, self.sheet_b)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_excel_create_variable_sheet(self):
        """Test if the variable sheet is on the right place"""
        var_sheet_name = "variables"
        with self.assertRaises(ValueError):
            # If there is no variable
            self.workbook.excel_create_variable_sheet(
                sheet_name="variables",
                position=1,
            )

        self.sheet_a.var['abc'] = "hello"
        self.workbook.excel_create_variable_sheet(
            sheet_name="variables",
            position=1,
        )
        self.assertListEqual([self.names[0], var_sheet_name, self.names[1]],
                             [sheet.name for sheet in self.workbook.sheets])

    def test_to_excel(self):
        """Test exporting to Excel"""
        path = pathlib.Path(tempfile.mkdtemp(), "file.xlsx")
        self.workbook.to_excel(path, export_parameters=[ExcelParameters()] * 3)
        self.assertTrue(path.exists())

    def test_to_dictionary(self):
        """Test exporting to dictionary"""
        res = self.workbook.to_dictionary(
            export_parameters=[DictionaryParameters()] * 3
        )
        self.assertDictEqual(res, {'ABC': {'table': {'data': {'rows': {'0': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '1': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '2': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '3': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '4': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}}}, 'variables': {}, 'rows': [{'name': '0'}, {'name': '1'}, {'name': '2'}, {'name': '3'}, {'name': '4'}], 'columns': [{'name': '0'}, {'name': '1'}, {'name': '2'}, {'name': '3'}, {'name': '4'}]}}, 'EFG': {'table': {'data': {'rows': {'0': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '1': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '2': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '3': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '4': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}}}, 'variables': {}, 'rows': [{'name': '0'}, {'name': '1'}, {'name': '2'}, {'name': '3'}, {'name': '4'}], 'columns': [{'name': '0'}, {'name': '1'}, {'name': '2'}, {'name': '3'}, {'name': '4'}]}}})  # noqa: E501

    def test_to_json(self):
        """Test exporting to JSON"""
        res = json.loads(
            self.workbook.to_json(
                export_parameters=[DictionaryParameters()] * 3
            )
        )
        self.assertDictEqual(res, {'ABC': {'table': {'data': {'rows': {'0': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '1': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '2': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '3': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '4': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}}}, 'variables': {}, 'rows': [{'name': '0'}, {'name': '1'}, {'name': '2'}, {'name': '3'}, {'name': '4'}], 'columns': [{'name': '0'}, {'name': '1'}, {'name': '2'}, {'name': '3'}, {'name': '4'}]}}, 'EFG': {'table': {'data': {'rows': {'0': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '1': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '2': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '3': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}, '4': {'columns': {'0': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '1': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '2': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '3': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}, '4': {'excel': '', 'python_numpy': '', 'value': None, 'description': None}}}}}, 'variables': {}, 'rows': [{'name': '0'}, {'name': '1'}, {'name': '2'}, {'name': '3'}, {'name': '4'}], 'columns': [{'name': '0'}, {'name': '1'}, {'name': '2'}, {'name': '3'}, {'name': '4'}]}}})  # noqa: E501

    def test_generate_json_schema(self):
        """Test JSON schema generator"""
        self.assertIsInstance(WorkBook.generate_json_schema(), dict)

    def test_to_string_of_values(self):
        """Test exporting to str"""
        self.workbook['ABC'].iloc[0, 0] = 7
        self.assertEqual(self.workbook.to_string_of_values(),
                         """[[[7, None, None, None, None],
[None, None, None, None, None],
[None, None, None, None, None],
[None, None, None, None, None],
[None, None, None, None, None]],[[None, None, None, None, None],
[None, None, None, None, None],
[None, None, None, None, None],
[None, None, None, None, None],
[None, None, None, None, None]],]"""
                         )

    def test_to_list(self):
        """Test exporting to list"""
        self.assertListEqual(self.workbook.to_list(export_parameters=[ListParameters()] * 3), [[['ABC', '0', '1', '2', '3', '4'], ['0', None, None, None, None, None], ['1', None, None, None, None, None], ['2', None, None, None, None, None], ['3', None, None, None, None, None], ['4', None, None, None, None, None]], [['EFG', '0', '1', '2', '3', '4'], ['0', None, None, None, None, None], ['1', None, None, None, None, None], ['2', None, None, None, None, None], ['3', None, None, None, None, None], ['4', None, None, None, None, None]]])  # noqa: E501

    def test_getitem(self):
        """Test wb[item] functionality"""
        self.assertEqual(self.workbook['ABC'].name, 'ABC')

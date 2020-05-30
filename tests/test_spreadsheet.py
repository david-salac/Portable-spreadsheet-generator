import unittest

import copy

import numpy as np

from portable_spreadsheet.spreadsheet import Spreadsheet
from portable_spreadsheet.cell import Cell
from portable_spreadsheet.cell_type import CellType
from portable_spreadsheet.cell_slice import CellSlice
from portable_spreadsheet.cell_indices import CellIndices
from portable_spreadsheet.cell_indices_templates import excel_generator


class TestSpreadsheetBasicFunctionality(unittest.TestCase):
    """Test the basic spreadsheet basic functionality."""
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
            excel_append_labels=True,
            warning_logger=lambda message: self.warnings.append(message)
        )
        self.sheet_shape = (self.nr_row, self.nr_col)

    def test_index_property(self):
        """Test index property"""
        computed = self.sheet.index
        expected = self.rows_labels
        self.assertListEqual(expected, computed)
        # Slice
        computed = self.sheet.iloc[3:, :].index
        expected = self.rows_labels[3:]
        self.assertListEqual(expected, computed)

    def test_columns_property(self):
        """Test columns property"""
        computed = self.sheet.columns
        expected = self.columns_labels
        self.assertListEqual(expected, computed)
        # Slice
        computed = self.sheet.iloc[:, 3:].columns
        expected = self.columns_labels[3:]
        self.assertListEqual(expected, computed)

    def test_create_new_sheet(self):
        """Test the instance sheet"""
        self.assertTrue(isinstance(self.sheet, Spreadsheet))

    def test_expand_sheet(self):
        """Test the expanding of the sheet size"""
        # Try to expand without all parameters
        with self.assertRaises(ValueError):
            self.sheet.cell_indices.expand_size(5, 3)

        old_sheet: Spreadsheet = copy.deepcopy(self.sheet)
        expand_row = 3
        expand_col = 5
        new_native_rows = [f'eR_{r_i}' for r_i in range(expand_row)]
        new_native_cols = [f'eC_{c_i}' for c_i in range(expand_col)]
        new_rows_labels = [f'LeR_{r_i}' for r_i in range(expand_row)]
        new_columns_labels = [f'LeC_{c_i}' for c_i in range(expand_col)]
        new_rows_help_text = [f'HeR_{r_i}' for r_i in range(expand_row)]
        new_columns_help_text = [f'HeC_{c_i}' for c_i in range(expand_col)]

        new_cell_idx = self.sheet.cell_indices.expand_size(
            expand_row, expand_col,
            {
                'native': (
                    new_native_rows,
                    new_native_cols
                )
            },
            new_rows_labels=new_rows_labels,
            new_columns_labels=new_columns_labels,
            new_rows_help_text=new_rows_help_text,
            new_columns_help_text=new_columns_help_text
        )
        old_sheet.expand_using_cell_indices(new_cell_idx)
        # Test the expanded sheet
        cell_indices: CellIndices = old_sheet.cell_indices
        self.assertTupleEqual(
            new_cell_idx.shape,
            old_sheet.shape,
            (self.nr_row + expand_row, self.nr_col + expand_col)
        )
        # Check rows in each language
        self.assertListEqual(cell_indices.rows['native'],
                             self.native_rows + new_native_rows)
        self.assertListEqual(
            cell_indices.rows['python_numpy'],
            [str(i) for i in range(0, self.nr_row + expand_row + 1)]
        )
        self.assertListEqual(
            cell_indices.rows['excel'],
            [str(i) for i in range(2, self.nr_row + expand_row + 1 + 1)]
        )
        # Check columns in each language
        self.assertListEqual(cell_indices.columns['native'],
                             self.native_cols + new_native_cols)
        self.assertListEqual(
            cell_indices.columns['python_numpy'],
            [str(i) for i in range(0, self.nr_col + expand_col + 1)]
        )
        self.assertListEqual(
            cell_indices.columns['excel'],
            excel_generator(1, self.nr_col + expand_col, 1)[1]
        )
        # Check variables of cell index
        self.assertListEqual(cell_indices.rows_labels,
                             self.rows_labels + new_rows_labels)
        self.assertListEqual(cell_indices.columns_labels,
                             self.columns_labels + new_columns_labels)
        self.assertListEqual(cell_indices.rows_help_text,
                             self.rows_help_text + new_rows_help_text)
        self.assertListEqual(cell_indices.columns_help_text,
                             self.columns_help_text + new_columns_help_text)

    def test_cell_indices(self):
        """Test the indices inside sheet"""
        cell_indices: CellIndices = self.sheet.cell_indices
        self.assertTupleEqual(cell_indices.shape, self.sheet_shape)
        # Check rows in each language
        self.assertListEqual(cell_indices.rows['native'], self.native_rows)
        self.assertListEqual(cell_indices.rows['python_numpy'],
                             [str(i) for i in range(0, self.nr_row + 1)])
        self.assertListEqual(cell_indices.rows['excel'],
                             [str(i) for i in range(2, self.nr_row + 1 + 1)])
        # Check columns in each language
        self.assertListEqual(cell_indices.columns['native'],
                             self.native_cols)
        self.assertListEqual(cell_indices.columns['python_numpy'],
                             [str(i) for i in range(0, self.nr_col + 1)])
        self.assertListEqual(cell_indices.columns['excel'],
                             excel_generator(1, self.nr_col, 1)[1])
        self.assertListEqual(excel_generator(1, 5, 1)[1],
                             ["B", "C", "D", "E", "F"])
        # Check variables of cell index
        self.assertListEqual(cell_indices.rows_labels, self.rows_labels)
        self.assertListEqual(cell_indices.columns_labels, self.columns_labels)
        self.assertListEqual(cell_indices.rows_help_text, self.rows_help_text)
        self.assertListEqual(cell_indices.columns_help_text,
                             self.columns_help_text)

    def test_shape_property(self):
        """Check the shape of the sheet property"""
        self.assertTupleEqual(self.sheet.shape, self.sheet_shape)

    def test_warning(self):
        """Test the warning logs."""
        self.sheet.iloc[:, :].to_dictionary()
        self.assertEqual(len(self.warnings), 1)


class TestSpreadsheetSelection(unittest.TestCase):
    """Test the selecting (slicing) from the spreadsheet."""
    def setUp(self) -> None:
        self.n_row = 13
        self.n_col = 27
        self.row_labels = [f"R_{r_i}" for r_i in range(self.n_row)]
        self.col_labels = [f"C_{c_i}" for c_i in range(self.n_col)]
        self.sheet = Spreadsheet.create_new_sheet(
            self.n_row, self.n_col,
            rows_labels=self.row_labels,
            columns_labels=self.col_labels
        )

    def assertAllClose2D(self, operand_1, operand_2, delta=0.000001) -> None:
        """Compare two 2D numpy-like arrays (with shape property)

        Args:
            operand_1: Expected value
            operand_2: Compared value
            delta: Delta for IEEE-Double comparisons
        """
        self.assertTupleEqual(operand_1.shape, operand_2.shape)
        for row_idx in range(operand_1.shape[0]):
            for col_idx in range(operand_1.shape[1]):
                if (np.isnan(operand_1[row_idx, col_idx])
                        and np.isnan(operand_2[row_idx, col_idx])):
                    continue
                self.assertAlmostEqual(operand_1[row_idx, col_idx],
                                       operand_2[row_idx, col_idx],
                                       delta=delta)

    def test_single_values(self):
        """Test the selecting and writing to the single value"""
        sheet = copy.deepcopy(self.sheet)
        np_sheet: np.ndarray = np.full((self.n_row, self.n_col), np.nan)
        # Getting values out of range
        with self.assertRaises(IndexError):
            self.sheet.iloc[50, 1]
        with self.assertRaises(IndexError):
            self.sheet.iloc[1, 55]

        # Setting values out of range
        with self.assertRaises(IndexError):
            self.sheet.iloc[50, 1] = 7
        with self.assertRaises(IndexError):
            self.sheet.iloc[1, 55] = 7

        # Getting values out of by label
        with self.assertRaises(ValueError):
            self.sheet.loc["XYZ", "C_1"]
        with self.assertRaises(ValueError):
            self.sheet.loc["R_1", "XZY"]

        # Setting values out of range by label
        with self.assertRaises(ValueError):
            self.sheet.loc["XYZ", "C_1"] = 7
        with self.assertRaises(ValueError):
            self.sheet.loc["R_1", "XZY"] = 7

        # Set the single value
        i_idx = (11, 20)
        sheet.iloc[i_idx] = 89.912
        np_sheet[i_idx] = 89.912
        self.assertAllClose2D(sheet.to_numpy(), np_sheet)
        # Test getter
        self.assertAlmostEqual(sheet.iloc[i_idx].value, np_sheet[i_idx])
        # Test the word created in cell
        a_cell: Cell = sheet.iloc[i_idx]
        self.assertEqual(a_cell.word.words['python_numpy'],
                         f'values[{i_idx[0]},{i_idx[1]}]')
        self.assertTrue(a_cell.anchored)
        self.assertEqual(a_cell.cell_type, CellType.value_only)
        self.assertTupleEqual(a_cell.coordinates, i_idx)

        # Setting by the label:
        sheet.loc['R_11', "C_20"] = 7.3
        np_sheet[i_idx] = 7.3
        self.assertAllClose2D(sheet.to_numpy(), np_sheet)
        # Test getter
        self.assertAlmostEqual(sheet.iloc[i_idx].value, np_sheet[i_idx])
        # Test the word created in cell
        a_cell: Cell = sheet.iloc[i_idx]
        self.assertEqual(a_cell.word.words['python_numpy'],
                         f'values[{i_idx[0]},{i_idx[1]}]')
        self.assertTrue(a_cell.anchored)
        self.assertEqual(a_cell.cell_type, CellType.value_only)
        self.assertTupleEqual(a_cell.coordinates, i_idx)

        # Test negative indices
        sheet.iloc[-7, -11] = 35.123
        np_sheet[-7, -11] = 35.123
        self.assertAllClose2D(sheet.to_numpy(), np_sheet)
        # Test getter
        self.assertAlmostEqual(sheet.iloc[-7, -11].value, np_sheet[-7, -11])

    def test_slice(self):
        """Test the selecting and writing to the slice"""
        sheet = copy.deepcopy(self.sheet)
        np_sheet: np.ndarray = np.full((self.n_row, self.n_col), np.nan)
        # Getting values out of range
        with self.assertRaises(IndexError):
            self.sheet.iloc[:500, 1]
        with self.assertRaises(IndexError):
            self.sheet.iloc[1, :500]

        # Setting values out of range
        with self.assertRaises(IndexError):
            self.sheet.iloc[500:, 1] = 7
        with self.assertRaises(IndexError):
            self.sheet.iloc[1, 500:] = 7

        # Getting values out of range by label
        with self.assertRaises(ValueError):
            self.sheet.loc[:"R_600", "C_1"]
        with self.assertRaises(ValueError):
            self.sheet.loc["R_1", :"C_30000"]

        # Setting values out of range by label
        with self.assertRaises(ValueError):
            self.sheet.loc[:"R_600", "C_1"] = 7
        with self.assertRaises(ValueError):
            self.sheet.loc["R_1", :"C_30000"] = 7

        # Set the slice of values
        i_idx = (slice(0, 11), slice(0, 20))
        sheet.iloc[i_idx] = 89.912
        np_sheet[i_idx] = 89.912
        self.assertAllClose2D(sheet.to_numpy(), np_sheet)
        # Test getter
        self.assertAllClose2D(sheet.iloc[i_idx].to_numpy(), np_sheet[i_idx])
        # Test slice method
        cell_slice: CellSlice = sheet.iloc[i_idx]
        u_max = cell_slice.max()
        self.assertDictEqual(u_max.word.words,
                             {'python_numpy': 'np.max(values[0:11,0:20])',
                              'excel': 'MAX(B2:U12)'})
        self.assertFalse(u_max.anchored)
        self.assertEqual(u_max.cell_type, CellType.computational)
        self.assertTupleEqual(u_max.coordinates, (None, None))
        # Test slice setter
        cell_slice <<= 9.9
        np_sheet[i_idx] = 9.9
        self.assertAllClose2D(sheet.iloc[i_idx].to_numpy(), np_sheet[i_idx])

        # Set the slice of values using labels
        label_idx = (slice("R_0", "R_11"), slice("C_0", "C_20"))
        sheet.loc[label_idx] = 3.14159
        np_sheet[i_idx] = 3.14159
        # Test getter
        self.assertAllClose2D(sheet.loc[label_idx].to_numpy(), np_sheet[i_idx])

        # Test slice with negative values:
        # Set the slice of values
        i_idx = (slice(0, -3), slice(0, -8))
        sheet.iloc[i_idx] = 14.5458
        np_sheet[i_idx] = 14.5458
        self.assertAllClose2D(sheet.to_numpy(), np_sheet)
        # Test getter
        self.assertAllClose2D(sheet.iloc[i_idx].to_numpy(), np_sheet[i_idx])


class TestNewLogic(unittest.TestCase):
    """Bigger regression testing of new constructing."""
    def setUp(self) -> None:
        """Set-up basic values and disable logging of NumPy."""
        # Numpy warnings:
        self.np_old_settings = np.seterr(all='ignore')

        self.shape = (10, 15)
        self.sheet: Spreadsheet = Spreadsheet.create_new_sheet(*self.shape)
        self.values = 1000 * np.random.random(self.shape)
        self.values[0, 0] = 2
        self.sheet.iloc[:, :] = self.values

    def tearDown(self) -> None:
        """Enable logging of NumPy back."""
        np.seterr(**self.np_old_settings)

    def test_binary_operations(self):
        """Test binary operations"""
        cell_composed = (
                self.sheet.iloc[3, 2] +
                self.sheet.iloc[1, 4] *
                self.sheet.fn.brackets(
                    self.sheet.iloc[6, 7] / self.sheet.iloc[5, 3]
                ) -
                self.sheet.iloc[4, 8] **
                self.sheet.iloc[0, 0] +
                self.sheet.iloc[8, 9] %
                self.sheet.iloc[2, 5] +
                self.sheet.fn.const(13)
        )

        # Array values is used by evaluation function
        values = self.values  # noqa
        computed = cell_composed.value
        expected_python_word = 'values[3,2]+values[1,4]*(values[6,7]/' \
                               'values[5,3])-values[4,8]**values[0,0]+' \
                               'values[8,9]%values[2,5]+13'
        self.assertEqual(expected_python_word,
                         cell_composed.parse['python_numpy'])
        expected = eval(cell_composed.parse['python_numpy'])
        self.assertAlmostEqual(computed, expected)

    def test_unary_operations(self):
        """Test unary operations"""
        cell_composed = self.sheet.fn.exp(self.sheet.fn.const(9)) + \
            self.sheet.fn.floor(
                self.sheet.iloc[3, 2] +
                self.sheet.iloc[1, 4] *
                self.sheet.fn.brackets(
                    self.sheet.iloc[6, 7] / self.sheet.iloc[5, 3]
                ) **
                self.sheet.fn.ln(self.sheet.iloc[0, 0])
            ) + \
            self.sheet.fn.ceil(self.sheet.iloc[2, 3]) - \
            self.sheet.fn.floor(self.sheet.iloc[4, 8]) * \
            self.sheet.fn.round(self.sheet.iloc[7, 9]) + \
            self.sheet.fn.abs(self.sheet.iloc[6, 3]) - \
            self.sheet.fn.sqrt(self.sheet.iloc[7, 4]) - \
            self.sheet.fn.sign(self.sheet.iloc[6, 2])

        # Array values is used by evaluation function
        values = self.values  # noqa
        computed = cell_composed.value
        expected_python_word = 'np.exp(9)+np.floor(values[3,2]+values[1,4]*' \
                               '(values[6,7]/values[5,3])**' \
                               'np.log(values[0,0]))+np.ceil(values[2,3])' \
                               '-np.floor(values[4,8])*' \
                               'np.round(values[7,9])+np.abs(values[6,3])-' \
                               'np.sqrt(values[7,4])-np.sign(values[6,2])'
        self.assertEqual(expected_python_word,
                         cell_composed.parse['python_numpy'])
        expected = eval(cell_composed.parse['python_numpy'])
        self.assertAlmostEqual(computed, expected)

    def test_condition(self):
        """Test conditional statement"""
        cell_cond = self.sheet.fn.conditional(
            self.sheet.fn.brackets(
                self.sheet.iloc[1, 0] + self.sheet.iloc[3, 5] *
                self.sheet.iloc[7, 5]
            ) == self.sheet.fn.brackets(
                self.sheet.iloc[2, 1] / self.sheet.iloc[7, 1] *
                self.sheet.iloc[0, 5]
            ),
            self.sheet.iloc[1, 5] + self.sheet.iloc[7, 3],
            self.sheet.fn.ln(self.sheet.iloc[0, 0]) *
            self.sheet.fn.exp(self.sheet.iloc[0, 0]) + self.sheet.iloc[8, 4]
        )

        # Array values is used by evaluation function
        values = self.values  # noqa
        computed = cell_cond.value
        expected_python_word = '((values[1,5]+values[7,3]) if ' \
                               '((values[1,0]+values[3,5]*values[7,5])==' \
                               '(values[2,1]/values[7,1]*values[0,5])) else ' \
                               '(np.log(values[0,0])*np.exp(values[0,0])+' \
                               'values[8,4]))'
        self.assertEqual(expected_python_word,
                         cell_cond.parse['python_numpy'])
        expected = eval(cell_cond.parse['python_numpy'])
        self.assertAlmostEqual(computed, expected)

    def test_offset(self):
        """Test offset statement"""
        cell_offset = self.sheet.fn.offset(
            self.sheet.iloc[3, 4],
            self.sheet.iloc[0, 0] + self.sheet.fn.const(1),
            self.sheet.fn.const(2) + self.sheet.iloc[0, 0]
        )

        # Array values is used by evaluation function
        values = self.values  # noqa
        computed = cell_offset.value
        expected_python_word = 'values[int(3+values[0,0]+1),' \
                               'int(4+2+values[0,0])]'
        self.assertEqual(expected_python_word,
                         cell_offset.parse['python_numpy'])
        expected = eval(cell_offset.parse['python_numpy'])
        self.assertAlmostEqual(computed, expected)

    def test_concatenate(self):
        """Test string concatenation"""
        cell_concatenate = (self.sheet.iloc[3, 4] <<
                            self.sheet.iloc[0, 0] <<
                            self.sheet.fn.const(19) <<
                            self.sheet.fn.const("hello"))

        # Array values is used by evaluation function
        values = self.values  # noqa
        computed = cell_concatenate.value
        expected_python_word = 'str(str(str(values[3,4])+str(values[0,0]' \
                               '))+str("19"))+str("hello")'
        self.assertEqual(expected_python_word,
                         cell_concatenate.parse['python_numpy'])
        expected = eval(cell_concatenate.parse['python_numpy'])
        self.assertEqual(computed, expected)

    def test_aggregation(self):
        """Test aggregation functions"""
        cell_aggregate = (
            self.sheet.iloc[3, 4:5].sum() +
            self.sheet.iloc[3:4, 6].average() +
            self.sheet.iloc[4:5, 5:6].product() +
            self.sheet.iloc[2:6, 3:8].stdev() +
            self.sheet.iloc[:, 1].min() +
            self.sheet.iloc[3, :].max() +
            self.sheet.iloc[:, :].median() +
            self.sheet.iloc[1, :].count() +
            self.sheet.iloc[1, 3:].count() +
            self.sheet.iloc[1:4, 3:].count()
        )
        # Array values is used by evaluation function
        values = self.values  # noqa
        computed = cell_aggregate.value
        expected_python_word = 'np.sum(values[3:4,4:5])+np.mean(values[3:4,' \
                               '6:7])+np.prod(values[4:5,5:6])+np.std(' \
                               'values[2:6,3:8])+np.min(values[0:10,1:2])' \
                               '+np.max(values[3:4,0:15])+np.median(' \
                               'values[0:10,0:15])+((lambda var=values[' \
                               '1:2,0:15]: var.shape[0] * var.shape[1])())' \
                               '+((lambda var=values[1:2,3:15]: ' \
                               'var.shape[0] * var.shape[1])())+' \
                               '((lambda var=values[1:4,3:15]: ' \
                               'var.shape[0] * var.shape[1])())'
        self.assertEqual(expected_python_word,
                         cell_aggregate.parse['python_numpy'])
        expected = eval(cell_aggregate.parse['python_numpy'])
        self.assertEqual(computed, expected)

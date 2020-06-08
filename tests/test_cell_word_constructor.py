import unittest

from typing import Callable, Collection

import numpy_financial as npf
import numpy as np

from portable_spreadsheet.cell import Cell
from portable_spreadsheet.cell_indices import CellIndices
from portable_spreadsheet.cell_type import CellType


class TestCellBasicFunctionality(unittest.TestCase):
    """Integration test for basic Cell functionality and WordConstructor
    functionality.

    Notice:
        if variable start with prefix 'a_' it means that cell is anchored
        (located in grid), if with prefix 'u_' it means that it is NOT
        anchored, with prefix 't' it does not matter (just a testing variable).
    """
    def setUp(self) -> None:
        self.cell_indices: CellIndices = CellIndices(5, 7)

    def test_initialisation(self):
        """Test the constructor of class Cell"""
        with self.assertRaises(ValueError):
            Cell(3, None, cell_indices=self.cell_indices)

        with self.assertRaises(AttributeError):
            Cell(3, 3, cell_indices=None)

        # Create some reasonable cell
        t_cell = Cell(3, 4, 7, cell_indices=self.cell_indices)
        self.assertEqual(t_cell.row, 3)
        self.assertEqual(t_cell.column, 4)
        self.assertEqual(t_cell.value, 7)
        self.assertEqual(t_cell.cell_type, CellType.value_only)
        self.assertFalse(t_cell.is_variable)
        self.assertIsNone(t_cell.variable_name)
        self.assertEqual(len(t_cell._excel_format), 0)
        self.assertIsNone(t_cell._description)
        # Check the initialisation words
        words = t_cell.constructing_words
        self.assertEqual(words.words['excel'], '7')
        self.assertEqual(words.words['python_numpy'], '7')
        self.assertTrue(t_cell.anchored)

    def test_word_property(self):
        """Test the property 'word'"""
        # Anchored cell
        a_cell = Cell(3, 4, 7, cell_indices=self.cell_indices)
        # There is an offset 1 row/column for labels!
        self.assertEqual(a_cell.word.words['excel'], 'F5')
        self.assertEqual(a_cell.word.words['python_numpy'], 'values[3,4]')
        self.assertTrue(a_cell.anchored)

        # Un-anchored cell
        u_cell = Cell(value=7, cell_indices=self.cell_indices)
        self.assertEqual(u_cell.word.words['excel'], '7')
        self.assertEqual(u_cell.word.words['python_numpy'], '7')
        self.assertFalse(u_cell.anchored)

    def test_coordinates_property(self):
        """Test coordinates"""
        # Anchored cell
        a_cell = Cell(3, 4, 7, cell_indices=self.cell_indices)
        self.assertTupleEqual(a_cell.coordinates, (3, 4))

        # Un-anchored cell
        u_cell = Cell(value=7, cell_indices=self.cell_indices)
        self.assertTupleEqual(u_cell.coordinates, (None, None))
        # Test setter
        u_cell.coordinates = (3, 2)
        self.assertTupleEqual(u_cell.coordinates, (3, 2))

    def test_value_property(self):
        """Test the value property"""
        t_cell = Cell(3, 4, 7, cell_indices=self.cell_indices)
        self.assertEqual(t_cell.value, 7)

    def test_parse_property(self):
        """Test the parsing (basically tests the method parse from the
            WordConstructor class
        """
        # Anchored & Value cells
        a_cell = Cell(3, 4, 7, cell_indices=self.cell_indices)
        a_parsed = a_cell.parse
        self.assertEqual(a_parsed['excel'], '7')
        self.assertEqual(a_parsed['python_numpy'], '7')
        # empty cell
        e_cell = Cell(3, 4, None, cell_indices=self.cell_indices)
        e_parsed = e_cell.parse
        self.assertEqual(e_parsed['excel'], '')
        self.assertEqual(e_parsed['python_numpy'], '')
        # Computational cells
        # have to do some simple computation
        operand_1 = Cell(3, 4, 7, cell_indices=self.cell_indices)
        operand_2 = Cell(2, 4, 6, cell_indices=self.cell_indices)
        sum_1_2 = operand_1 + operand_2
        s_parsed = sum_1_2.parse
        self.assertEqual(s_parsed['excel'], '=F5+F4')
        self.assertEqual(s_parsed['python_numpy'], 'values[3,4]+values[2,4]')

    def test_excel_format(self):
        """Test if excel format getter/setter works"""
        t_cell = Cell(3, 4, 7, cell_indices=self.cell_indices)
        with self.assertRaises(ValueError):
            t_cell.excel_format = 7
        t_cell.excel_format = {'bold': True}
        self.assertDictEqual(t_cell.excel_format, {'bold': True})
        self.assertDictEqual(t_cell._excel_format, {'bold': True})

    def test_description(self):
        """Test if the description works"""
        t_cell = Cell(3, 4, 7, cell_indices=self.cell_indices)
        with self.assertRaises(ValueError):
            t_cell.description = 7
        t_cell.description = "Super description"
        self.assertEqual(t_cell.description, "Super description")
        self.assertEqual(t_cell._description, "Super description")

    def test_constructing_words(self):
        """Test the constructing words property."""
        t_cell = Cell(3, 4, 7, cell_indices=self.cell_indices)
        self.assertEqual(t_cell.constructing_words, t_cell._constructing_words)

    def test_conditional(self):
        """Regression test for the conditional."""
        a_cell_cond_1 = Cell(1, 3, 8, cell_indices=self.cell_indices)
        u_cell_cond_2 = Cell(value=7, cell_indices=self.cell_indices)
        a_cell_conseq = Cell(2, 3, 11, cell_indices=self.cell_indices)
        u_cell_altern = Cell(value=5, cell_indices=self.cell_indices)

        u_res = Cell.conditional(a_cell_cond_1 == u_cell_cond_2,  # <- IF
                                 a_cell_conseq,  # <- THEN
                                 u_cell_altern)  # <- ELSE
        # Test generated words
        res_word = u_res.parse
        word_expected = {
            'python_numpy': '((values[2,3]) if (values[1,3]==7) else (5))',
            'excel': '=IF(E3=7,E4,5)'
        }
        self.assertDictEqual(word_expected, res_word)
        # Test generated values
        value_computed = u_res.value
        value_expected = u_cell_altern.value
        self.assertEqual(value_expected, value_computed)

    def test_offset(self):
        """Regression test for the offset."""
        a_cell_ref = Cell(1, 3, 8, cell_indices=self.cell_indices)
        u_cell_row = Cell(value=7, cell_indices=self.cell_indices)
        a_cell_col = Cell(2, 3, 11, cell_indices=self.cell_indices)
        u_cell_tar = Cell(5, 5, 5, cell_indices=self.cell_indices)

        u_res = Cell.offset(a_cell_ref, u_cell_row, a_cell_col,
                            target=u_cell_tar)
        # Test generated words
        res_word = u_res.parse
        word_expected = {'excel': '=OFFSET(E3,7,E4)',
                         'python_numpy': 'values[1+7,3+values[2,3]]'}
        self.assertDictEqual(word_expected, res_word)
        # Test generated values
        value_computed = u_res.value
        value_expected = u_cell_tar.value
        self.assertEqual(value_expected, value_computed)


class TestCellBinaryOperations(unittest.TestCase):
    """Test binary operations.

    Notice:
        if variable start with prefix 'a_' it means that cell is anchored
        (located in grid), if with prefix 'u_' it means that it is NOT
        anchored, with prefix 't' it does not matter (just a testing variable).
    """
    def setUp(self) -> None:
        self.cell_indices: CellIndices = CellIndices(5, 7)
        self.a_operand_1 = Cell(3, 4, 7, cell_indices=self.cell_indices)
        self.a_operand_2 = Cell(2, 4, 4, cell_indices=self.cell_indices)
        self.coord_operand_1_python = "values[3,4]"
        self.coord_operand_2_python = "values[2,4]"
        self.coord_operand_1_excel = "F5"
        self.coord_operand_2_excel = "F4"

        self.u_operand_1 = Cell(value=7, cell_indices=self.cell_indices)
        self.u_operand_2 = Cell(value=8, cell_indices=self.cell_indices)
        self.value_u_1 = "7"
        self.value_u_2 = "8"

    def _check_binary_operation(
            self,
            operation_method: Callable[[Cell, Cell], Cell],
            real_operation_fn: Callable[[float, float], float],
            excel_separator: str,
            python_numpy_separator: str, *,
            excel_prefix: str = "",
            excel_suffix: str = "",
            excel_reference_prefix: str = "=",
            python_reference_prefix: str = "",
    ) -> None:
        """Run the binary operation, compare numeric result, compare words.

        Args:
            operation_method (Callable[[Cell, Cell], Cell]): Pointer to the
                method inside the Cell class.
            real_operation_fn (Callable[[float, float], float]): Pointer to the
                Python method that compute the same.
            excel_separator (str): Separator of the operation in
                Excel language.
            python_numpy_separator (str): Separator of the operation in
                Python_NumPY language.
            excel_prefix (str): Prefix for the operation in Excel language.
            excel_suffix (str): Suffix for the operation in Excel language.
            excel_reference_prefix (str): Prefix of the word that reference
                to some computation in Excel.
            python_reference_prefix (str): Prefix of the word that reference
                to some computation in Python.
        """
        # A) Anchored
        a_res_cell = operation_method(self.a_operand_1, self.a_operand_2)
        # Compare words
        a_res_parsed = a_res_cell.parse
        self.assertEqual(a_res_parsed['excel'],
                         (excel_reference_prefix + excel_prefix +
                          self.coord_operand_1_excel + excel_separator +
                          self.coord_operand_2_excel + excel_suffix)
                         )
        self.assertEqual(a_res_parsed['python_numpy'],
                         (python_reference_prefix +
                          self.coord_operand_1_python +
                          python_numpy_separator +
                          self.coord_operand_2_python)
                         )
        # Compare results of anchored
        self.assertAlmostEqual(a_res_cell.value,
                               real_operation_fn(self.a_operand_1.value,
                                                 self.a_operand_2.value))
        # B) Un-anchored
        u_res_cell = operation_method(self.u_operand_1, self.u_operand_2)
        # Compare words
        u_res_parsed = u_res_cell.parse
        self.assertEqual(u_res_parsed['excel'],
                         (excel_reference_prefix + excel_prefix +
                          self.value_u_1 +
                          excel_separator +
                          self.value_u_2 + excel_suffix)
                         )
        self.assertEqual(u_res_parsed['python_numpy'],
                         (python_reference_prefix +
                          self.value_u_1 +
                          python_numpy_separator +
                          self.value_u_2)
                         )
        # Compare results of un-anchored
        self.assertAlmostEqual(u_res_cell.value,
                               real_operation_fn(self.u_operand_1.value,
                                                 self.u_operand_2.value))

    def test_add(self):
        """Test adding"""
        # Method test
        self._check_binary_operation(Cell.add,
                                     lambda x, y: x + y,
                                     "+",
                                     "+")
        # Operator test
        self._check_binary_operation(Cell.__add__,
                                     lambda x, y: x + y,
                                     "+",
                                     "+")

    def test_subtract(self):
        """Test subtracting"""
        # Method test
        self._check_binary_operation(Cell.subtract,
                                     lambda x, y: x - y,
                                     "-",
                                     "-")
        # Operator test
        self._check_binary_operation(Cell.__sub__,
                                     lambda x, y: x - y,
                                     "-",
                                     "-")

    def test_multiply(self):
        """Test multiplying"""
        # Method test
        self._check_binary_operation(Cell.multiply,
                                     lambda x, y: x * y,
                                     "*",
                                     "*")
        # Operator test
        self._check_binary_operation(Cell.__mul__,
                                     lambda x, y: x * y,
                                     "*",
                                     "*")

    def test_divide(self):
        """Test dividing"""
        # Method test
        self._check_binary_operation(Cell.divide,
                                     lambda x, y: x / y,
                                     "/",
                                     "/")
        # Operator test
        self._check_binary_operation(Cell.__truediv__,
                                     lambda x, y: x / y,
                                     "/",
                                     "/")

    def test_modulo(self):
        """Test modulo"""
        # Method test
        self._check_binary_operation(Cell.modulo,
                                     lambda x, y: x % y,
                                     ",",
                                     "%",
                                     excel_prefix="MOD(",
                                     excel_suffix=")")
        # Operator test
        self._check_binary_operation(Cell.__mod__,
                                     lambda x, y: x % y,
                                     ",",
                                     "%",
                                     excel_prefix="MOD(",
                                     excel_suffix=")")

    def test_power(self):
        """Test power"""
        # Method test
        self._check_binary_operation(Cell.power,
                                     lambda x, y: x ** y,
                                     "^",
                                     "**")
        # Operator test
        self._check_binary_operation(Cell.__pow__,
                                     lambda x, y: x ** y,
                                     "^",
                                     "**")

    def test_equalTo(self):
        """Test equal to"""
        # Method test
        self._check_binary_operation(Cell.equalTo,
                                     lambda x, y: x == y,
                                     "=",
                                     "==")
        # Operator test
        self._check_binary_operation(Cell.__eq__,
                                     lambda x, y: x == y,
                                     "=",
                                     "==")

    def test_notEqualTo(self):
        """Test not equal to"""
        # Method test
        self._check_binary_operation(Cell.notEqualTo,
                                     lambda x, y: x != y,
                                     "<>",
                                     "!=")
        # Operator test
        self._check_binary_operation(Cell.__ne__,
                                     lambda x, y: x != y,
                                     "<>",
                                     "!=")

    def test_greaterThan(self):
        """Test greater than"""
        # Method test
        self._check_binary_operation(Cell.greaterThan,
                                     lambda x, y: x > y,
                                     ">",
                                     ">")
        # Operator test
        self._check_binary_operation(Cell.__gt__,
                                     lambda x, y: x > y,
                                     ">",
                                     ">")

    def test_greaterThanOrEqualTo(self):
        """Test greater than or equal to"""
        # Method test
        self._check_binary_operation(Cell.greaterThanOrEqualTo,
                                     lambda x, y: x >= y,
                                     ">=",
                                     ">=")
        # Operator test
        self._check_binary_operation(Cell.__ge__,
                                     lambda x, y: x >= y,
                                     ">=",
                                     ">=")

    def test_lessThan(self):
        """Test less than"""
        # Method test
        self._check_binary_operation(Cell.lessThan,
                                     lambda x, y: x < y,
                                     "<",
                                     "<")
        # Operator test
        self._check_binary_operation(Cell.__lt__,
                                     lambda x, y: x < y,
                                     "<",
                                     "<")

    def test_lessThanOrEqualTo(self):
        """Test less than or equal to"""
        # Method test
        self._check_binary_operation(Cell.lessThanOrEqualTo,
                                     lambda x, y: x <= y,
                                     "<=",
                                     "<=")
        # Operator test
        self._check_binary_operation(Cell.__le__,
                                     lambda x, y: x <= y,
                                     "<=",
                                     "<=")

    def test_LogicalConjunction(self):
        """Test logical conjunction"""
        # Method test
        self._check_binary_operation(Cell.logicalConjunction,
                                     lambda x, y: x and y,
                                     ", ",
                                     " and ",
                                     excel_prefix="AND(",
                                     excel_suffix=")")
        # Operator test
        self._check_binary_operation(Cell.__and__,
                                     lambda x, y: x and y,
                                     ", ",
                                     " and ",
                                     excel_prefix="AND(",
                                     excel_suffix=")")

    def test_LogicalDisjunction(self):
        """Test logical disjunction"""
        # Method test
        self._check_binary_operation(Cell.logicalDisjunction,
                                     lambda x, y: x or y,
                                     ", ",
                                     " or ",
                                     excel_prefix="OR(",
                                     excel_suffix=")")
        # Operator test
        self._check_binary_operation(Cell.__or__,
                                     lambda x, y: x or y,
                                     ", ",
                                     " or ",
                                     excel_prefix="OR(",
                                     excel_suffix=")")

    def test_chain_of_operation(self):
        """Test multiple operations in a sequence"""
        result = self.a_operand_1 + self.a_operand_2 * self.u_operand_1
        self.assertDictEqual({'python_numpy': 'values[3,4]+values[2,4]*7',
                              'excel': '=F5+F4*7'},
                             result.parse)
        self.assertAlmostEqual(result.value, 35)

    def test_raw_statement(self):
        """Test raw statement"""
        result = Cell.raw(self.a_operand_1, {
            'python_numpy': "Hello from Python",
            'excel': "Excel welcomes"
        })
        self.assertDictEqual({
            'python_numpy': "Hello from Python",
            'excel': "=Excel welcomes"  # Always computational
        }, result.parse)
        self.assertAlmostEqual(self.a_operand_1.value, 7)

    def test_concatenate(self):
        """Test string concatenation."""
        # Define grammar rules
        excel_reference_prefix = "="
        excel_prefix = "CONCATENATE("
        excel_separator = ","
        excel_suffix = ")"
        python_reference_prefix = ""
        python_numpy_separator = "+"
        # A) Anchored
        a_res_cell = self.a_operand_1.concatenate(self.a_operand_2)
        # Compare words
        a_res_parsed = a_res_cell.parse
        self.assertEqual((excel_reference_prefix + excel_prefix +
                          self.coord_operand_1_excel + excel_separator +
                          self.coord_operand_2_excel + excel_suffix),
                         a_res_parsed['excel'])
        self.assertEqual((python_reference_prefix +
                          self.coord_operand_1_python +
                          python_numpy_separator +
                          self.coord_operand_2_python),
                         a_res_parsed['python_numpy']
                         )
        # Compare results of anchored
        self.assertAlmostEqual(a_res_cell.value,
                               str(self.a_operand_1.value) +
                               str(self.a_operand_2.value))

        # B) Un-anchored, numerical
        u_res_cell = self.u_operand_1.concatenate(self.u_operand_2)
        # Compare words
        u_res_parsed = u_res_cell.parse
        self.assertEqual(u_res_parsed['excel'],
                         (excel_reference_prefix +
                          excel_prefix +
                          self.value_u_1 +
                          excel_separator +
                          self.value_u_2 +
                          excel_suffix)
                         )
        self.assertEqual(u_res_parsed['python_numpy'],
                         ('"' + python_reference_prefix +
                          self.value_u_1 + '"' +
                          python_numpy_separator +
                          '"' + self.value_u_2 + '"')
                         )
        # Compare results of un-anchored
        self.assertAlmostEqual(u_res_cell.value,
                               str(self.u_operand_1.value) +
                               str(self.u_operand_2.value))

        # C) Un-anchored, strings
        str_value = "6ppW1lPT"
        u_operand_1 = Cell(value=str_value, cell_indices=self.cell_indices)
        u_res_cell = u_operand_1.concatenate(self.u_operand_2)
        # Compare words
        u_res_parsed = u_res_cell.parse
        self.assertEqual(u_res_parsed['excel'],
                         (excel_reference_prefix +
                          excel_prefix +
                          '"' + str_value + '"' +
                          excel_separator +
                          self.value_u_2 +
                          excel_suffix)
                         )
        self.assertEqual(u_res_parsed['python_numpy'],
                         (python_reference_prefix +
                          str_value +
                          python_numpy_separator +
                          '"' + self.value_u_2 + '"')
                         )
        # Compare results of un-anchored
        self.assertAlmostEqual(u_res_cell.value,
                               u_operand_1.value +
                               str(self.u_operand_2.value))


class TestCellAggregationFunctionality(unittest.TestCase):
    """Test aggregation functions.

    Notice:
        if variable start with prefix 'a_' it means that cell is anchored
        (located in grid), if with prefix 'u_' it means that it is NOT
        anchored, with prefix 't' it does not matter (just a testing variable).
    """
    def setUp(self) -> None:
        self.cell_indices: CellIndices = CellIndices(5, 7)
        self.a_cell_start = Cell(1, 2, 7, cell_indices=self.cell_indices)
        self.a_cell_end = Cell(3, 5, 4, cell_indices=self.cell_indices)
        # Words for slices (aggregation operation):
        self.slice_python = "values[1:4,2:6]"
        self.slice_excel = "D3:G5"  # shifted because of offset to labels
        # Create the set (collection of values)
        self.slice_cardinality = 12
        self.cell_set = [Cell(i, j, np.random.random() * 10,
                              cell_indices=self.cell_indices)
                         for i in range(1, 3 + 1)
                         for j in range(2, 5 + 1)
                         ]
        self.cell_set[0]._value = -100
        self.cell_values = [self.cell_set[i].value
                            for i in range(self.slice_cardinality)]

    def _check_aggregate_function(
            self,
            operation_method: Callable[[Cell, Cell, Collection[Cell]], Cell],
            real_operation_fn: Callable[[float, float], float],
            excel_prefix: str,
            excel_suffix: str,
            python_prefix: str,
            python_suffix: str, *,
            excel_reference_prefix: str = "=",
            python_reference_prefix: str = "",
    ) -> None:
        """Run the aggregate function, compare numeric result, compare words.

        Args:
            operation_method (Callable[[Cell, Cell], Cell], Collection[Cell]):
                Pointer to the method inside the Cell class.
            real_operation_fn (Callable[[float, float], float]): Pointer to the
                Python method that compute the same.
            excel_prefix (str): Prefix for the operation in Excel language.
            excel_suffix (str): Suffix for the operation in Excel language.
            python_prefix (str): Prefix for the operation in Python_NumPy
                language.
            python_suffix (str): Suffix for the operation in Python_NumPy
                language.
            excel_reference_prefix (str): Prefix of the word that reference
                to some computation in Excel.
            python_reference_prefix (str): Prefix of the word that reference
                to some computation in Python.
        """
        u_result = operation_method(self.a_cell_start, self.a_cell_end,
                                    self.cell_set)
        # Check the values
        u_value_computed = u_result.value
        value_expected = real_operation_fn(self.cell_values)
        self.assertAlmostEqual(u_value_computed, value_expected)

        # Compare words
        u_res_parsed = u_result.parse
        self.assertEqual(u_res_parsed['excel'],
                         (excel_reference_prefix + excel_prefix +
                          self.slice_excel + excel_suffix)
                         )
        self.assertEqual(u_res_parsed['python_numpy'],
                         (python_reference_prefix + python_prefix +
                          self.slice_python + python_suffix)
                         )

    def test_sum(self):
        """Test the sum"""
        self._check_aggregate_function(Cell.sum, np.sum, "SUM(", ")",
                                       "np.sum(", ")")

    def test_product(self):
        """Test the product"""
        self._check_aggregate_function(Cell.product, np.prod, "PRODUCT(", ")",
                                       "np.prod(", ")")

    def test_mean(self):
        """Test the mean"""
        self._check_aggregate_function(Cell.mean, np.mean, "AVERAGE(", ")",
                                       "np.mean(", ")")

    def test_min(self):
        """Test the min"""
        self._check_aggregate_function(Cell.min, np.min, "MIN(", ")",
                                       "np.min(", ")")

    def test_max(self):
        """Test the max"""
        self._check_aggregate_function(Cell.max, np.max, "MAX(", ")",
                                       "np.max(", ")")

    def test_stdev(self):
        """Test the standard deviation"""
        self._check_aggregate_function(Cell.stdev, np.std, "STDEV(", ")",
                                       "np.std(", ")")

    def test_median(self):
        """Test the median"""
        self._check_aggregate_function(Cell.median, np.median, "MEDIAN(", ")",
                                       "np.median(", ")")

    def test_count(self):
        """Test the count"""
        self._check_aggregate_function(Cell.count,
                                       lambda _: self.slice_cardinality,
                                       "COUNT(", ")",
                                       "((lambda var=",
                                       ": var.shape[0] * var.shape[1])())")

    def test_irr(self):
        """Test the Internal Rate of Return (IRR)"""
        self._check_aggregate_function(Cell.irr, npf.irr, "IRR(", ")",
                                       "npf.irr(", ")")

    def test_match_negative_before_positive(self):
        """Test of finding the position of the last negative number in the
            series that is located just before the first non-negative number.
        """
        self._check_aggregate_function(Cell.match_negative_before_positive,
                                       lambda x: (np.argmin(np.array(x) < 0)),
                                       "MATCH(0,", ")",
                                       "np.argmin(", "<0)")


class TestCellUnaryFunctionality(unittest.TestCase):
    """Test unary operators (functions with just one parameter).

    Notice:
        if variable start with prefix 'a_' it means that cell is anchored
        (located in grid), if with prefix 'u_' it means that it is NOT
        anchored, with prefix 't' it does not matter (just a testing variable).
    """
    def setUp(self) -> None:
        self.cell_indices: CellIndices = CellIndices(5, 7)
        self.a_operand = Cell(3, 4, 7, cell_indices=self.cell_indices)
        self.coord_operand_python = "values[3,4]"
        self.coord_operand_excel = "F5"

        self.u_operand = Cell(value=7, cell_indices=self.cell_indices)
        self.value_u = "7"

    def test_reference(self):
        """Test the referencing to some cell"""
        with self.assertRaises(ValueError):
            Cell.reference(self.u_operand)
        u_reference = Cell.reference(self.a_operand)
        u_ref_word = u_reference.parse
        self.assertEqual(u_ref_word['excel'], "=" + self.coord_operand_excel)
        self.assertEqual(u_ref_word['python_numpy'], self.coord_operand_python)

    def test_variable(self):
        """Test the variables parsing"""
        with self.assertRaises(ValueError):
            Cell.variable(self.a_operand)

        variable_name = "test_var"
        var_value = 99
        # Un-anchored variable
        u_var_cell = Cell(None, None, 99, cell_indices=self.cell_indices,
                          is_variable=True, variable_name=variable_name,
                          cell_type=CellType.computational)
        self.assertEqual(u_var_cell.value, var_value)
        # Reference to variable
        u_ref_cell = Cell.variable(u_var_cell)
        u_ref_cell_word = u_ref_cell.parse
        self.assertEqual(u_ref_cell_word['python_numpy'], str(variable_name))
        self.assertEqual(u_ref_cell_word['excel'], '=' + str(variable_name))

    def _check_unary_operation(
            self,
            operation_method: Callable[[Cell], Cell],
            real_operation_fn: Callable[[float], float],
            excel_prefix: str = "",
            excel_suffix: str = "",
            python_prefix: str = "",
            python_suffix: str = "",
            *,
            excel_reference_prefix: str = "=",
            python_reference_prefix: str = "",
    ) -> None:
        """Run the unary operation, compare numeric result, compare words.

        Args:
            operation_method (Callable[[Cell, Cell], Cell]): Pointer to the
                method inside the Cell class.
            real_operation_fn (Callable[[float, float], float]): Pointer to the
                Python method that compute the same.
            excel_prefix (str): Prefix for the operation in Excel language.
            excel_suffix (str): Suffix for the operation in Excel language.
            python_prefix (str): Prefix for the operation in Python_NumPy
                language.
            python_suffix (str): Suffix for the operation in Python_NumPy
                language.
            excel_reference_prefix (str): Prefix of the word that reference
                to some computation in Excel.
            python_reference_prefix (str): Prefix of the word that reference
                to some computation in Python.
        """
        # A) Anchored
        a_res_cell = operation_method(self.a_operand)
        # Compare words
        a_res_parsed = a_res_cell.parse
        self.assertEqual(a_res_parsed['excel'],
                         (excel_reference_prefix + excel_prefix +
                          self.coord_operand_excel + excel_suffix)
                         )
        self.assertEqual(a_res_parsed['python_numpy'],
                         (python_reference_prefix + python_prefix +
                          self.coord_operand_python + python_suffix)
                         )
        # Compare results of anchored
        self.assertAlmostEqual(a_res_cell.value,
                               real_operation_fn(self.a_operand.value))
        # B) Un-anchored
        u_res_cell = operation_method(self.u_operand)
        # Compare words
        u_res_parsed = u_res_cell.parse
        self.assertEqual(u_res_parsed['excel'],
                         (excel_reference_prefix + excel_prefix +
                          self.value_u + excel_suffix)
                         )
        self.assertEqual(u_res_parsed['python_numpy'],
                         (python_reference_prefix + python_prefix +
                          self.value_u + python_suffix)
                         )
        # Compare results of un-anchored
        self.assertAlmostEqual(u_res_cell.value,
                               real_operation_fn(self.u_operand.value))

    def test_brackets(self):
        """Test the brackets parsing"""
        self._check_unary_operation(Cell.brackets,
                                    lambda x: x,
                                    "(", ")", "(", ")")

    def test_logarithm(self):
        """Test the logarithm parsing"""
        self._check_unary_operation(Cell.logarithm,
                                    np.log,
                                    "LN(", ")", "np.log(", ")")

    def test_exponential(self):
        """Test the exponential parsing"""
        self._check_unary_operation(Cell.exponential,
                                    np.exp,
                                    "EXP(", ")", "np.exp(", ")")

    def test_ceil(self):
        """Test the ceil parsing"""
        self._check_unary_operation(Cell.ceil,
                                    np.ceil,
                                    "CEILING(", ")", "np.ceil(", ")")

    def test_floor(self):
        """Test the floor parsing"""
        self._check_unary_operation(Cell.floor,
                                    np.floor,
                                    "FLOOR(", ")", "np.floor(", ")")

    def test_round(self):
        """Test the round parsing"""
        self._check_unary_operation(Cell.round,
                                    np.round,
                                    "ROUND(", ")", "np.round(", ")")

    def test_abs(self):
        """Test the abs parsing"""
        self._check_unary_operation(Cell.abs,
                                    np.abs,
                                    "ABS(", ")", "np.abs(", ")")

    def test_sqrt(self):
        """Test the square root parsing"""
        self._check_unary_operation(Cell.sqrt,
                                    np.sqrt,
                                    "SQRT(", ")", "np.sqrt(", ")")

    def test_logicalNegation(self):
        """Test the logical negation parsing"""
        self._check_unary_operation(Cell.logicalNegation,
                                    lambda x: not x,
                                    "NOT(", ")", "not (", ")")

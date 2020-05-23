import unittest

from typing import Callable

from portable_spreadsheet.cell import Cell
from portable_spreadsheet.cell_indices import CellIndices
from portable_spreadsheet.cell_type import CellType


class TestCellBasicFunctionality(unittest.TestCase):
    """Integration test for basic Cell functionality and WordConstructor
    functionality."""
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

        # Unanchored cell
        u_cell = Cell(value=7, cell_indices=self.cell_indices)
        self.assertEqual(u_cell.word.words['excel'], '7')
        self.assertEqual(u_cell.word.words['python_numpy'], '7')
        self.assertFalse(u_cell.anchored)

    def test_coordinates_property(self):
        """Test coordinates"""
        # Anchored cell
        a_cell = Cell(3, 4, 7, cell_indices=self.cell_indices)
        self.assertTupleEqual(a_cell.coordinates, (3, 4))

        # Unanchored cell
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


class TestCellBinaryOperations(unittest.TestCase):
    """Test binary operations"""
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
            excel_prefix: str = "=",
            excel_suffix: str = "",
    ):
        """Run the binary operation, compare numeric result, compare words."""
        # A) Anchored
        a_res_cell = operation_method(self.a_operand_1, self.a_operand_2)
        # Compare words
        a_res_parsed = a_res_cell.parse
        self.assertEqual(a_res_parsed['excel'],
                         (excel_prefix + self.coord_operand_1_excel +
                          excel_separator +
                          self.coord_operand_2_excel + excel_suffix)
                         )
        self.assertEqual(a_res_parsed['python_numpy'],
                         (self.coord_operand_1_python +
                          python_numpy_separator +
                          self.coord_operand_2_python)
                         )
        # Compare results of anchored
        self.assertEqual(a_res_cell.value,
                         real_operation_fn(self.a_operand_1.value,
                                           self.a_operand_2.value))
        # B) Un-anchored
        u_res_cell = operation_method(self.u_operand_1, self.u_operand_2)
        # Compare words
        u_res_parsed = u_res_cell.parse
        self.assertEqual(u_res_parsed['excel'],
                         (excel_prefix + self.value_u_1 +
                          excel_separator +
                          self.value_u_2 + excel_suffix)
                         )
        self.assertEqual(u_res_parsed['python_numpy'],
                         (self.value_u_1 +
                          python_numpy_separator +
                          self.value_u_2)
                         )
        # Compare results of un-anchored
        self.assertEqual(u_res_cell.value,
                         real_operation_fn(self.u_operand_1.value,
                                           self.u_operand_2.value))

    def test_add(self):
        """Test adding"""
        self._check_binary_operation(Cell.add,
                                     lambda x, y: x + y,
                                     "+",
                                     "+")

    def test_subtract(self):
        """Test subtracting"""
        self._check_binary_operation(Cell.subtract,
                                     lambda x, y: x - y,
                                     "-",
                                     "-")

    def test_multiply(self):
        """Test multiplying"""
        self._check_binary_operation(Cell.multiply,
                                     lambda x, y: x * y,
                                     "*",
                                     "*")

    def test_divide(self):
        """Test dividing"""
        self._check_binary_operation(Cell.divide,
                                     lambda x, y: x / y,
                                     "/",
                                     "/")

    def test_modulo(self):
        """Test modulo"""
        self._check_binary_operation(Cell.modulo,
                                     lambda x, y: x % y,
                                     ",",
                                     "%",
                                     excel_prefix="=MOD(",
                                     excel_suffix=")")

    def test_power(self):
        """Test power"""
        self._check_binary_operation(Cell.power,
                                     lambda x, y: x ** y,
                                     "^",
                                     "**")

    def test_equalTo(self):
        """Test equal to"""
        self._check_binary_operation(Cell.equalTo,
                                     lambda x, y: x == y,
                                     "=",
                                     "==")

    def test_notEqualTo(self):
        """Test not equal to"""
        self._check_binary_operation(Cell.notEqualTo,
                                     lambda x, y: x != y,
                                     "<>",
                                     "!=")

    def test_greaterThan(self):
        """Test greater than"""
        self._check_binary_operation(Cell.greaterThan,
                                     lambda x, y: x > y,
                                     ">",
                                     ">")

    def test_greaterThanOrEqualTo(self):
        """Test greater than or equal to"""
        self._check_binary_operation(Cell.greaterThanOrEqualTo,
                                     lambda x, y: x >= y,
                                     ">=",
                                     ">=")

    def test_lessThan(self):
        """Test less than"""
        self._check_binary_operation(Cell.lessThan,
                                     lambda x, y: x < y,
                                     "<",
                                     "<")

    def test_lessThanOrEqualTo(self):
        """Test less than or equal to"""
        self._check_binary_operation(Cell.lessThanOrEqualTo,
                                     lambda x, y: x <= y,
                                     "<=",
                                     "<=")

    def test_LogicalConjunction(self):
        """Test logical conjunction"""
        self._check_binary_operation(Cell.logicalConjunction,
                                     lambda x, y: x and y,
                                     ", ",
                                     " and ",
                                     excel_prefix="=AND(",
                                     excel_suffix=")")

    def test_LogicalDisjunction(self):
        """Test logical disjunction"""
        self._check_binary_operation(Cell.logicalDisjunction,
                                     lambda x, y: x or y,
                                     ", ",
                                     " or ",
                                     excel_prefix="=OR(",
                                     excel_suffix=")")

    def test_chain_of_operation(self):
        """Test multiple operations in a sequence"""
        result = self.a_operand_1 + self.a_operand_2 * self.u_operand_1
        self.assertDictEqual({'python_numpy': 'values[3,4]+values[2,4]*7',
                              'excel': '=F5+F4*7'},
                             result.parse)
        self.assertEqual(result.value, 35)


class TestCellAggregationFunctionality(unittest.TestCase):
    """Test aggregation functions"""
    def setUp(self) -> None:
        self.cell_indices: CellIndices = CellIndices(5, 7)
        self.a_operand_start = Cell(1, 2, 7, cell_indices=self.cell_indices)
        self.a_operand_end = Cell(3, 5, 4, cell_indices=self.cell_indices)
        self.slice_python = "values[1:4,2:6]"
        self.slice_excel = "C2:F4"
        self.cell_set = [Cell(1, 2, 7, cell_indices=self.cell_indices)
                         for _ in range(12)]

    # TODO

    def test_sum(self):
        """Test the sum"""
        pass

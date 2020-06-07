from typing import Dict, Optional, Iterable, Tuple, Callable

import numpy as np
import numpy_financial as npf

from .word_constructor import WordConstructor
from .cell_type import CellType
from .cell_indices import CellIndices
from .nary_tree import NaryTree


class Cell(object):
    """Represent the single cell in the spreadsheet.

    Attributes:
        row (Optional[int]): Position of the cell (row index).
        column (Optional[int]): Position of the cell (column index).
        cell_type (CellType): If the cell is Value or Computational. Value type
            means that it only stores constant value, computation means that
            it does some computations
        _value (Optional[float]): The actual value of the cell.
        _cell_indices (CellIndices): The indices of the columns and rows for
            each used language.
        _constructing_words (WordConstructor): The words defining the cell in
            each language.
        is_variable (bool): If True, cell is considered to be a varaible.
        variable_name (Optional[str]): The name of variable.
        _excel_format (dict): Dictionary defining the Excel format style
            for the cell.
        _description (Optional[str]): Optional description of the cell.
        _operations_tree (NaryTree): n-ary tree describing relations of the
            cell with other cells. Created, perforce, for implementing deleting
            cells and rows/columns.
    """
    def __init__(self,
                 row: Optional[int] = None,
                 column: Optional[int] = None, /,  # noqa E999
                 value: Optional[float] = None, *,
                 cell_indices: CellIndices,
                 # Private arguments
                 cell_type: CellType = CellType.value_only,
                 words: Optional[WordConstructor] = None,
                 is_variable: bool = False,
                 variable_name: Optional[str] = None,
                 operations_tree: Optional[NaryTree] = None
                 ):
        """Create single cell.

        Args:
            row (Optional[int]): Position of the cell (row index).
            column (Optional[int]): Position of the cell (column index).
            cell_indices (CellIndices): The indices of the columns and rows for
                each used language.
            cell_type (CellType): If the cell is Value or Computational. Value
                type means that it only stores constant value, computation
                means that it does some computations. Do not use this argument
                directly.
            words (Optional[WordConstructor]): The words defining the cell
                in each language. Do not use this argument directly.
            is_variable (bool): If True, cell is considered to be a variable.
            variable_name (Optional[str]): The name of variable.
            operations_tree (NaryTree): n-ary tree describing relations of the
                cell with other cells. Created, perforce, for implementing
                deleting cells and rows/columns.
        """
        if row is not None and column is None \
                or row is None and column is not None:
            raise ValueError("The values of 'row' and 'column' parameters have"
                             " to be either both not None or both None.")
        self.row: Optional[int] = row
        self.column: Optional[int] = column
        self._value: Optional[float] = value
        self.cell_type: CellType = cell_type
        self._cell_indices: CellIndices = cell_indices  # pass only reference
        self.is_variable: bool = is_variable
        self.variable_name: Optional[str] = variable_name
        self._excel_format: dict = {}
        self._description: Optional[str] = None

        if operations_tree is None:
            self._operations_tree: NaryTree = NaryTree(row, column)
        else:
            self._operations_tree: NaryTree = operations_tree

        if words is not None:
            self._constructing_words: WordConstructor = words
        else:
            self._constructing_words: WordConstructor = \
                WordConstructor.init_from_new_cell(self)

    # === CLASS METHODS and PROPERTIES: ===
    @property
    def cell_indices(self) -> CellIndices:
        """Get the sheet indices.

        Returns:
            CellIndices: Indices of the sheet
        """
        return self._cell_indices

    @cell_indices.setter
    def cell_indices(self, cell_indices: CellIndices) -> CellIndices:
        """Set the sheet indices.

        Args:
            cell_indices (CellIndices): Indices of the sheet
        """
        # Update cell indices on the Cell level
        self._cell_indices: CellIndices = cell_indices
        # Update cell indices in the word constructor
        self._constructing_words.cell_indices = cell_indices

    @property
    def word(self) -> WordConstructor:
        """Return correct word. If the cell is anchored, returns just the
            coordinates. If the cell is not anchored: 1) If it is computational
            returns the building string, 2) If it is Value returns the value

        Returns:
              WordConstructor: Right word.
        """
        if self.anchored:
            return WordConstructor.reference(self)
        else:
            if self.cell_type == CellType.computational:
                return self._constructing_words
            elif self.cell_type == CellType.value_only:
                return WordConstructor.constant(self)

    @property
    def anchored(self) -> bool:
        """Return True if the cell is the part of the grid. Return False
            if it is temporarily created for the computation.

        Returns:
            bool: True/False value telling if the cell is anchored to grid.
        """
        return self.row is not None

    @property
    def coordinates(self) -> Tuple[int, int]:
        """Returns the coordinates of the cell.

        Returns:
            Tuple[int, int]: 1) row index, 2) column index
        """
        return self.row, self.column

    @coordinates.setter
    def coordinates(self, coordinates: Tuple[int, int]) -> None:
        """Set the coordinates of the grid.

        Args:
            coordinates (Tuple[int, int]): New coordinates index (row, column)
        """
        # Update coordinates of the Cell
        self.row = coordinates[0]
        self.column = coordinates[1]
        # Update coordinates of the tree
        self._operations_tree.coordinates = coordinates

    @property
    def value(self) -> float:
        """Return the actual numeric value of the cell.

        Returns:
            float: the numeric value of the cell.
        """
        return self._value

    def __str__(self) -> str:
        """Override the method __str__ to allow human-readable string
            generations of inside.

        Returns:
            str: String representation of inner value.
        """
        ret_dict = self.parse
        ret_dict['value'] = self.value
        return str(ret_dict)

    @property
    def constructing_words(self) -> WordConstructor:
        """Get the constructing words.

        Returns:
            WordConstructor: the constructing word of the cell.
        """
        return self._constructing_words

    @property
    def parse(self) -> Dict[str, str]:
        """Return the dictionary with keys: language, values: constructing
            word. This function is called when the cell should be inserted to
            a spreadsheet.

        Returns:
            Dict[str, str]: Words for each language
        """
        return self._constructing_words.parse(self)

    @property
    def excel_format(self) -> dict:
        """Return style/format of the cell for Excel.

        Returns:
            dict: Excel format dictionary
        """
        return self._excel_format

    @excel_format.setter
    def excel_format(self, new_format: dict):
        """Set the Excel cell format/style.

        Read the documentation: https://xlsxwriter.readthedocs.io/format.html

        Args:
            new_format (dict): New format definition.
        """
        if not isinstance(new_format, dict):
            raise ValueError("New format has to be a dictionary!")
        self._excel_format = new_format

    @property
    def description(self) -> Optional[str]:
        """Return description of the cell or None.

        Returns:
            str: description of the cell or None.
        """
        return self._description

    @description.setter
    def description(self, new_description: Optional[str]):
        """Set the cell description.

        Args:
            new_description (Optional[str]): description of the cell.
        """
        # Use only None value or string value
        if (new_description is not None
                and not isinstance(new_description, str)):
            raise ValueError("Cell description has to be a string value!")
        self._description = new_description

    def re_evaluate(self, sheet, /) -> None:  # noqa: E225
        """Re-evaluate (recompute) the value of the cell from the word.

        Args:
            sheet (Spreadsheet): Spreadsheet object.
        TODO:
            use different logic
        """
        values = sheet.iloc  # noqa
        words = self.parse
        print(words)
        self.value = eval(words['python_numpy'])

    def update_after_cell_delete(self, *,
                                 row_index: int,
                                 column_index: int) -> Tuple[Tuple[int, int]]:
        """Perform deleting of the cell on given row/column position.

        Args:
            row_index (int): Index of the cell's row to be deleted.
            column_index (int): Index of the cell's column to be deleted.

        Returns:
            Tuple[Tuple[int, int]]: Indices of the cells that must be updated.
        """
        return self._operations_tree.delete(row_index, column_index)

    @property
    def operations_tree(self) -> NaryTree:
        """Return the cell tree describing relations between operations.

        Returns:
            NaryTree: cell tree describing relations between operations.
        """
        return self._operations_tree
    # =====================================

    # === BINARY OPERATORS: ===
    def _binary_operation(self,
                          other: 'Cell',
                          python_operation: Callable[[object], object],
                          word_constructor_method: Callable[['Cell', 'Cell'],
                                                            WordConstructor]
                          ) -> 'Cell':
        """Generic binary operation.

        Args:
            other (Cell): Another operand besides of cell for the binary
                operation.
            python_operation (Callable[[object], object]): Function in Python
                that does required operation (typically some lambda expression)
            word_constructor_method (Callable[['Cell', 'Cell'],
                WordConstructor]): Method in WordConstructor class that creates
                words for given operation.

        Returns:
            Cell: Computational type of Cell class with result.
        """
        return Cell(value=python_operation(self.value, other.value),
                    words=word_constructor_method(self, other),
                    cell_indices=other.cell_indices,
                    cell_type=CellType.computational,
                    operations_tree=NaryTree.construct(self, other)
                    )

    def add(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Add two values.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self + other
        """
        return self._binary_operation(other,
                                      lambda a, b: a + b,
                                      WordConstructor.add)

    def subtract(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Subtract two values.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self - other
        """
        return self._binary_operation(other,
                                      lambda a, b: a - b,
                                      WordConstructor.subtract)

    def multiply(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Multiply two values.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self * other
        """
        return self._binary_operation(other,
                                      lambda a, b: a * b,
                                      WordConstructor.multiply)

    def divide(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Divide two values.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self / other
        """
        return self._binary_operation(other,
                                      lambda a, b: a / b,
                                      WordConstructor.divide)

    def modulo(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Modulo of two values.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self / other
        """
        return self._binary_operation(other,
                                      lambda a, b: a % b,
                                      WordConstructor.modulo)

    def power(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Self power to other.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self ** other
        """
        return self._binary_operation(other,
                                      lambda a, b: a ** b,
                                      WordConstructor.power)

    def equalTo(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Boolean equal operator.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self equal to other
        """
        return self._binary_operation(other,
                                      lambda a, b: a == b,
                                      WordConstructor.equalTo)

    def notEqualTo(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Boolean not equal operator.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self not equal to other
        """
        return self._binary_operation(other,
                                      lambda a, b: a != b,
                                      WordConstructor.notEqualTo)

    def greaterThan(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Boolean greater than operator.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self greater than other
        """
        return self._binary_operation(other,
                                      lambda a, b: a > b,
                                      WordConstructor.greaterThan)

    def greaterThanOrEqualTo(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Boolean greater than or equal to operator.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self greater than or equal to other
        """
        return self._binary_operation(other,
                                      lambda a, b: a >= b,
                                      WordConstructor.greaterThanOrEqualTo)

    def lessThan(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Boolean less than operator.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self less than other
        """
        return self._binary_operation(other,
                                      lambda a, b: a < b,
                                      WordConstructor.lessThan)

    def lessThanOrEqualTo(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Boolean less than or equal to operator.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self less than or equal to other
        """
        return self._binary_operation(other,
                                      lambda a, b: a <= b,
                                      WordConstructor.lessThanOrEqualTo)

    def logicalConjunction(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Logical conjunction operator.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self and other
        """
        return self._binary_operation(other,
                                      lambda a, b: a and b,
                                      WordConstructor.logicalConjunction)

    def logicalDisjunction(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Logical disjunction operator.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self or other
        """
        return self._binary_operation(other,
                                      lambda a, b: a or b,
                                      WordConstructor.logicalDisjunction)

    def concatenate(self, other: 'Cell', /) -> 'Cell':  # noqa: E225
        """Concatenate two values as strings.

        Args:
            other (Cell): Another operand.

        Returns:
            Cell: self concatenate with other
        """
        return self._binary_operation(other,
                                      lambda a, b: str(a) + str(b),
                                      WordConstructor.concatenate)
    # =========================

    # ==== OPERATOR OVERLOADING ====
    def __mul__(self, other):
        """Overload the operator '*'."""
        return self.multiply(other)

    def __sub__(self, other):
        """Overload the operator '-'."""
        return self.subtract(other)

    def __add__(self, other):
        """Overload the operator '+'."""
        return self.add(other)

    def __truediv__(self, other):
        """Overload the operator '/'."""
        return self.divide(other)

    def __pow__(self, power, modulo=None):
        """Overload the operator '**'."""
        return self.power(power)

    def __mod__(self, other):
        """Overload the operator '%'."""
        return self.modulo(other)

    def __eq__(self, other):
        """Overload the operator '=='."""
        return self.equalTo(other)

    def __ne__(self, other):
        """Overload the operator '!='."""
        return self.notEqualTo(other)

    def __gt__(self, other):
        """Overload the operator '>'."""
        return self.greaterThan(other)

    def __ge__(self, other):
        """Overload the operator '>='."""
        return self.greaterThanOrEqualTo(other)

    def __lt__(self, other):
        """Overload the operator '<'."""
        return self.lessThan(other)

    def __le__(self, other):
        """Overload the operator '<='."""
        return self.lessThanOrEqualTo(other)

    def __and__(self, other):
        """Overload the operator 'and'."""
        return self.logicalConjunction(other)

    def __or__(self, other):
        """Overload the operator 'or'."""
        return self.logicalDisjunction(other)

    def __invert__(self):
        """Overload the operator '~'."""
        return self.logicalNegation(self)

    def __lshift__(self, other):
        """Overload the operator '<<' to string concatenation."""
        return self.concatenate(other)
    # ==============================

    # === AGGREGATE OPERATORS ===
    @staticmethod
    def sum(cell_start: 'Cell', cell_end: 'Cell',
            subset: Iterable['Cell']) -> 'Cell':
        """Compute the sum of the slice.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.

        Returns:
            Cell: the cell with aggregated and computed results.
        """
        return Cell._aggregate_fun(cell_start, cell_end, subset,
                                   'sum', np.sum)

    @staticmethod
    def product(cell_start: 'Cell', cell_end: 'Cell',
                subset: Iterable['Cell']) -> 'Cell':
        """Compute the product of the slice.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.

        Returns:
            Cell: the cell with aggregated and computed results.
        """
        return Cell._aggregate_fun(cell_start, cell_end, subset,
                                   'product', np.prod)

    @staticmethod
    def mean(cell_start: 'Cell', cell_end: 'Cell',
             subset: Iterable['Cell']) -> 'Cell':
        """Compute the mean-average of the slice.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.

        Returns:
            Cell: the cell with aggregated and computed results.
        """
        return Cell._aggregate_fun(cell_start, cell_end, subset,
                                   'mean', np.mean)

    @staticmethod
    def min(cell_start: 'Cell', cell_end: 'Cell',
            subset: Iterable['Cell']) -> 'Cell':
        """Compute the minimum of the slice.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.

        Returns:
            Cell: the cell with aggregated and computed results.
        """
        return Cell._aggregate_fun(cell_start, cell_end, subset,
                                   'minimum', np.min)

    @staticmethod
    def max(cell_start: 'Cell', cell_end: 'Cell',
            subset: Iterable['Cell']) -> 'Cell':
        """Compute the maximum of the slice.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.

        Returns:
            Cell: the cell with aggregated and computed results.
        """
        return Cell._aggregate_fun(cell_start, cell_end, subset,
                                   'maximum', np.max)

    @staticmethod
    def stdev(cell_start: 'Cell', cell_end: 'Cell',
              subset: Iterable['Cell']) -> 'Cell':
        """Compute the standard deviation of the slice.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.

        Returns:
            Cell: the cell with aggregated and computed results.
        """
        return Cell._aggregate_fun(cell_start, cell_end, subset,
                                   'stdev', np.std)

    @staticmethod
    def median(cell_start: 'Cell', cell_end: 'Cell',
               subset: Iterable['Cell']) -> 'Cell':
        """Compute the median of the slice.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.

        Returns:
            Cell: the cell with aggregated and computed results.
        """
        return Cell._aggregate_fun(cell_start, cell_end, subset,
                                   'median', np.median)

    @staticmethod
    def count(cell_start: 'Cell', cell_end: 'Cell',
              subset: Iterable['Cell']) -> 'Cell':
        """Compute the number of items the slice.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.

        Returns:
            Cell: the cell with aggregated and computed results.
        """
        return Cell._aggregate_fun(cell_start, cell_end, subset,
                                   'count', len)

    @staticmethod
    def irr(cell_start: 'Cell', cell_end: 'Cell',
            subset: Iterable['Cell']) -> 'Cell':
        """Compute the Internal Rate of Return (IRR) of items in slice.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.

        Returns:
            Cell: return the Internal Rate of Return (IRR) of slice.
        """
        return Cell._aggregate_fun(cell_start, cell_end, subset,
                                   'irr', npf.irr)

    @staticmethod
    def _aggregate_fun(
            cell_start: 'Cell',
            cell_end: 'Cell',
            subset: Iterable['Cell'],
            grammar_method: str,
            method_np: Callable[[Iterable[float]], float]
    ) -> 'Cell':
        """General aggregation function covering all methods.

        Args:
            cell_start (Cell): Starting cell of the slice (left top).
            cell_end: (Cell'): Ending cell of the slice (bottom right).
            subset (Iterable['Cell']): List of all cells in the subset.
            grammar_method (str): What method is used (like 'minimum', ...)
            method_np (Callable[[Iterable[float]], float]): What numpy method
                is used for computation.

        Returns:
            Cell: the cell with aggregated and computed results.

        Raises:
            ValueError: If the starting or ending cells are not anchored.
        """
        if not(cell_start.anchored and cell_end.anchored):
            raise ValueError("All cells in the slice has to be anchored!")

        return Cell(value=method_np([c.value for c in subset]),
                    words=WordConstructor.aggregation(
                        cell_start, cell_end, grammar_method
                    ),
                    cell_indices=cell_start.cell_indices,
                    cell_type=CellType.computational,
                    operations_tree=NaryTree.construct(*subset)
                    )
    # ===========================

    # === UNARY OPERATORS: ===
    @staticmethod
    def _unary_operation(other: 'Cell',
                         python_operation: Callable[[object], object],
                         word_constructor_method: Callable[['Cell'],
                                                           WordConstructor]
                         ) -> 'Cell':
        """General unary operation

        Args:
            other (Cell): Cell for the unary operation.
            python_operation (Callable[[object], object]): Function
                that computes result in pure Python (typically lambda).
            word_constructor_method (Callable[['Cell'], WordConstructor]):
                Method of the WordConstructor class that construct the word.

        Returns:
            Cell: Result after applying the unary operation.
        """
        return Cell(value=python_operation(other.value),
                    words=word_constructor_method(other),
                    cell_indices=other.cell_indices,
                    cell_type=CellType.computational,
                    operations_tree=NaryTree.construct(other)
                    )

    @staticmethod
    def reference(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Create a reference to some anchored cell.

        Args:
            other (Cell): The cell to what reference is constructed.

        Returns:
            Cell: Cell containing only the reference to another cell.
        """
        if not other.anchored:
            raise ValueError("The referenced cell has to be anchored.")

        return Cell._unary_operation(other,
                                     lambda x: x,
                                     WordConstructor.reference)

    @staticmethod
    def variable(other: 'Cell', /) -> 'Cell':  # noqa E225
        """The cell as a variable.

        Args:
            other (Cell): Cell that is interpreted as a variable.

        Returns:
            Cell: variable.
        """
        if not other.is_variable:
            raise ValueError("Only the variable type cell is accepted!")

        return Cell._unary_operation(other,
                                     lambda x: x,
                                     WordConstructor.variable)

    @staticmethod
    def brackets(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Add brackets to expression.

        Args:
            other (Cell): The expression that should be in brackets.

        Returns:
            Cell: Expression in brackets
        """
        return Cell._unary_operation(other,
                                     lambda x: x,
                                     WordConstructor.brackets)

    @staticmethod
    def logarithm(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Logarithm of the value in the cell.

        Args:
            other (Cell): Argument of the logarithm function.

        Returns:
            Cell: logarithm of the value
        """
        return Cell._unary_operation(other,
                                     lambda x: np.log(x),
                                     WordConstructor.logarithm)

    @staticmethod
    def exponential(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Exponential of the value in the cell.

        Args:
            other (Cell): Argument of the exponential function.

        Returns:
            Cell: exponential of the value
        """
        return Cell._unary_operation(other,
                                     lambda x: np.exp(x),
                                     WordConstructor.exponential)

    @staticmethod
    def ceil(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Ceiling function of the value in the cell.

        Args:
            other (Cell): Argument of the ceiling function.

        Returns:
            Cell: ceiling function value of the input
        """
        return Cell._unary_operation(other,
                                     lambda x: np.ceil(x),
                                     WordConstructor.ceil)

    @staticmethod
    def floor(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Floor function of the value in the cell.

        Args:
            other (Cell): Argument of the floor function.

        Returns:
            Cell: floor function value of the input
        """
        return Cell._unary_operation(other,
                                     lambda x: np.floor(x),
                                     WordConstructor.floor)

    @staticmethod
    def round(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Round the value in the cell.

        Args:
            other (Cell): Argument of the rounding function.

        Returns:
            Cell: round of the input numeric value
        """
        return Cell._unary_operation(other,
                                     lambda x: np.round(x),
                                     WordConstructor.round)

    @staticmethod
    def abs(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Absolute value of the value in the cell.

        Args:
            other (Cell): Argument of the absolute value function.

        Returns:
            Cell: absolute value of the input numeric value
        """
        return Cell._unary_operation(other,
                                     lambda x: np.abs(x),
                                     WordConstructor.abs)

    @staticmethod
    def sqrt(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Square root of the value in the cell.

        Args:
            other (Cell): Argument of the square root function.

        Returns:
            Cell: square root of the input numeric value
        """
        return Cell._unary_operation(other,
                                     lambda x: np.sqrt(x),
                                     WordConstructor.sqrt)

    @staticmethod
    def signum(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Signum function of the value in the cell.

        Args:
            other (Cell): Argument of the signum function.

        Returns:
            Cell: signum of the input numeric value
        """
        return Cell._unary_operation(other,
                                     lambda x: np.sign(x),
                                     WordConstructor.signum)

    @staticmethod
    def logicalNegation(other: 'Cell', /) -> 'Cell':  # noqa E225
        """Logical negation of the value in the cell.

        Args:
            other (Cell): Argument of the logical negation.

        Returns:
            Cell: logical negation the input value
        """
        return Cell._unary_operation(other,
                                     lambda x: not (x),
                                     WordConstructor.logicalNegation)
    # ========================

    # === Conditional (if-then-else statement) ===
    @staticmethod
    def conditional(condition: 'Cell',
                    consequent: 'Cell',
                    alternative: 'Cell', /) -> 'Cell':  # noqa E225
        """Conditional statement (standard if-then-else statement).

        Evaluate the value of the condition, if it is true, take the value
            of the consequent, if not take the value of the alternative.

        Args:
            condition (Cell): Cell defining the condition (boolean value)
            consequent (Cell): What is pass if the condition is true (the
                part right after the if)
            alternative (Cell): What is pass if the condition is false (the
                part right after the else)

        Returns:
            Cell: The if-then-else conditional statement and correctly
                chosen value.
        """
        return Cell(value=(consequent.value
                           if condition.value else alternative.value),
                    words=WordConstructor.conditional(
                        condition, consequent, alternative
                    ),
                    cell_indices=condition.cell_indices,
                    cell_type=CellType.computational,
                    operations_tree=NaryTree.construct(consequent,
                                                       condition, alternative)
                    )
    # ============================================

    # === OFFSET ===
    @staticmethod
    def offset(reference: 'Cell',
               row_skip: 'Cell',
               column_skip: 'Cell', /, *, # noqa E225
               target: 'Cell') -> 'Cell':
        """Return the cell with value computed as offset from reference cell
            plus row_skip rows and column_skip columns.

        Args:
            reference (Cell): Reference cell from that the position is
                computed.
            row_skip (Cell): How many rows (down) should be skipped.
            column_skip (Cell): How many columns (left) should be skipped.
            target (Cell): Target cell (place where user really skips).

        Returns:
            Cell: Cell with offset operation and value from the cell on the
                referential position.

        Raises:
            ValueError: If any of reference or target cells are not anchored.
        """
        # Test if both reference and target cells are anchored
        if not(reference.anchored and target.anchored):
            raise ValueError("Both reference cell and target cell must be"
                             " anchored!")
        return Cell(value=target.value,
                    words=WordConstructor.offset(
                        reference, row_skip, column_skip
                    ),
                    cell_indices=reference.cell_indices,
                    cell_type=CellType.computational,
                    operations_tree=NaryTree.construct(reference, row_skip,
                                                       column_skip, target)
                    )
    # ==============

    # ==== RAW STATEMENT ====
    @staticmethod
    def raw(other: 'Cell', words: Dict[str, str], /) -> 'Cell':  # noqa: E225
        """Add the raw statement and use the value of input cell.

        Args:
            other (Cell): Input cell that defines value and type of output.
            words (Dict[str, str]): Word for each language (language is a key,
                word is a value)

        Returns:
            Cell: Expression with defined word
        """
        return Cell(value=other.value,
                    words=WordConstructor.raw(other, words),
                    cell_indices=other.cell_indices,
                    cell_type=CellType.computational,
                    operations_tree=NaryTree.construct(other)
                    )
    # =======================

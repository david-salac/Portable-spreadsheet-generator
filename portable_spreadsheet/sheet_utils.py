from typing import Dict, Union, Optional, TYPE_CHECKING
import re
from numbers import Number

from .cell import Cell
from .cell_type import CellType

if TYPE_CHECKING:
    from .cell_slice import CellSlice
    from .sheet import Sheet

# ========== File with the functionality for internal purposes only ===========


class _Location(object):
    """Private class that enables indexing and slicing of values using
        obj.loc[col, row] or obj.iloc[col_idx, row_idx] logic.

    Attributes:
        spreadsheet (Sheet): Reference to spreadsheet instance.
        by_integer (bool): If True, indices are computed using integer value,
            if False, labels (aliases, typically string) are used.
    """

    def __init__(self,
                 spreadsheet,
                 by_integer: bool):
        """Initialise location

        Args:
            spreadsheet (Sheet): Reference to spreadsheet instance.
            by_integer (bool): If True, indices are computed using integer
            value, if False, labels (aliases, typically string) are used.
        """
        self.spreadsheet = spreadsheet
        self.by_integer: str = by_integer

    def __setitem__(self, index, val):
        """Set item selected as index or as a slice.

        Args:
            index: standard tuple of indices or tuple of slices.
            val: the value to be set.
        """
        has_slice = isinstance(index[0], slice) or isinstance(index[1], slice)
        if not has_slice:
            if self.by_integer:
                self.spreadsheet._set_item(val, index, None)
            else:
                self.spreadsheet._set_item(val, None, index)
        else:
            if self.by_integer:
                return self.spreadsheet._set_slice(val, index, None)
            else:
                return self.spreadsheet._set_slice(val, None, index)

    def __getitem__(self, index):
        """Get the item from the slice or single value.

        Args:
            index: standard tuple of indices or tuple of slices.
        """
        has_slice = isinstance(index[0], slice) or isinstance(index[1], slice)
        if not has_slice:
            if self.by_integer:
                return self.spreadsheet._get_item(index, None)
            else:
                return self.spreadsheet._get_item(None, index)
        else:
            if self.by_integer:
                return self.spreadsheet._get_slice(index, None)
            else:
                return self.spreadsheet._get_slice(None, index)

    def get_slice(self,
                  index_row: Union[slice, int],
                  index_column: Union[slice, int],
                  *,
                  include_right: bool = False) -> 'CellSlice':
        """Get the slice directly using method.

        Args:
            index_row (slice): Position of the row inside spreadsheet.
            index_column (slice): Position of the column inside spreadsheet.
            include_right (bool): If True, right most value (end parameter
                value) is included.

        Returns:
            CellSlice: slice of the cells
        """
        if self.by_integer:
            return self.spreadsheet._get_slice((index_row, index_column), None,
                                               include_right=include_right)
        else:
            return self.spreadsheet._get_slice(None, (index_row, index_column),
                                               include_right=include_right)

    def set_slice(self,
                  index_row: Union[slice, int],
                  index_column: Union[slice, int],
                  value,
                  *,
                  include_right: bool = False) -> None:
        """Get the slice directly using method.

        Args:
            index_row (slice): Position of the row inside spreadsheet.
            index_column (slice): Position of the column inside spreadsheet.
            include_right (bool): If True, right most value (end parameter
                value) is included.
            value: The new value to be set.
        """
        if self.by_integer:
            return self.spreadsheet._set_slice(value,
                                               (index_row, index_column),
                                               None,
                                               include_right=include_right)
        else:
            return self.spreadsheet._set_slice(value,
                                               None,
                                               (index_row, index_column),
                                               include_right=include_right)


class _Functionality(object):
    """Class encapsulating some shortcuts for functionality.

    Attributes:
        spreadsheet (Sheet): Reference to spreadsheet instance.
    """

    def __init__(self, spreadsheet):
        """
        Args:
            spreadsheet (Sheet): Reference to spreadsheet instance.
        """
        self.spreadsheet = spreadsheet

    def const(self, value: Number) -> Cell:
        """Create the constant for computation (un-anchored cell).

        Args:
            value (Number): Some constant value.

        Returns:
            Cell: un-anchored cell with constant value.
        """
        return Cell(value=value,
                    cell_indices=self.spreadsheet.cell_indices)

    @staticmethod
    def raw(value: Cell, words: Dict[str, str]) -> Cell:
        """Add the raw statement and use the value of input cell.

        Args:
            value (Cell): Input cell that defines value and type of output.
            words (Dict[str, str]): Word for each language (language is a key,
                word is a value)

        Warnings:
            Do not use this feature unless you really have to.

        Returns:
            Cell: Expression with defined word
        """
        return Cell.raw(value, words)

    @staticmethod
    def brackets(body: Cell) -> Cell:
        """Shortcut for adding bracket around body.

        Args:
            body (Cell): The body of the expression.

        Returns:
            Cell: Expression with brackets
        """
        return Cell.brackets(body)

    @staticmethod
    def cross_reference(target: Cell, sheet: 'Sheet') -> Cell:
        """Cross reference to other sheet in the workbook.

        Args:
            target (Cell): Target cell in a different sheet.
            sheet (Sheet): Sheet of the target cell.

        Return:
            Cell: reference to the different location.
        """
        return Cell.cross_reference(target, sheet)

    @staticmethod
    def ln(value: Cell) -> Cell:
        """Natural logarithm of the value.

        Args:
            value (Cell): The input value for computation.

        Returns:
            Cell: Natural logarithm of the input value.
        """
        return Cell.logarithm(value)

    @staticmethod
    def exp(value: Cell) -> Cell:
        """Exponential function of the value (e^value).

        Args:
            value (Cell): The input value for computation.

        Returns:
            Cell: Exponential function of the input value.
        """
        return Cell.exponential(value)

    @staticmethod
    def floor(value: Cell) -> Cell:
        """Floor function of the value.

        Args:
            value (Cell): The input value for computation.

        Returns:
            Cell: Floor function of the input value.
        """
        return Cell.floor(value)

    @staticmethod
    def ceil(value: Cell) -> Cell:
        """Ceiling function of the value.

        Args:
            value (Cell): The input value for computation.

        Returns:
            Cell: Ceiling function of the input value.
        """
        return Cell.ceil(value)

    @staticmethod
    def round(value: Cell) -> Cell:
        """Round the numeric value.

        Args:
            value (Cell): The input value for computation.

        Returns:
            Cell: Round of the input value.
        """
        return Cell.round(value)

    @staticmethod
    def abs(value: Cell) -> Cell:
        """Absolute value of the input.

        Args:
            value (Cell): The input value for computation.

        Returns:
            Cell: Absolute value of the input value.
        """
        return Cell.abs(value)

    @staticmethod
    def sqrt(value: Cell) -> Cell:
        """Square root of the input.

        Args:
            value (Cell): The input value for computation.

        Returns:
            Cell: Square root of the input value.
        """
        return Cell.sqrt(value)

    @staticmethod
    def sign(value: Cell) -> Cell:
        """Signum function of the input.

        Args:
            value (Cell): The input value for computation.

        Returns:
            Cell: Signum function value of the input value.
        """
        return Cell.signum(value)

    @staticmethod
    def neg(value: Cell) -> Cell:
        """Logical negation of the input.

        Args:
            value (Cell): The input value for computation.

        Returns:
            Cell: logical negation of the input value.
        """
        return Cell.logicalNegation(value)

    @staticmethod
    def conditional(condition: Cell,
                    consequent: Cell,
                    alternative: Cell, /) -> Cell:  # noqa: E225
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
        return Cell.conditional(condition, consequent, alternative)

    def offset(self,
               reference: Cell,
               row_skip: Cell,
               column_skip: Cell, /) -> Cell:  # noqa: E225
        """Return the cell with value computed as offset from reference
            cell plus row_skip rows and column_skip columns.

        Args:
            reference (Cell): Reference cell from that the position is
                computed.
            row_skip (Cell): How many rows (down) should be skipped.
            column_skip (Cell): How many columns (left) should be skipped.

        Returns:
            Cell: Cell with offset operation and value from the cell on the
                referential position.

        Raises:
            ValueError: If the reference cell is not anchored.
        """
        # Test if the reference cell is anchored
        if not reference.anchored:
            raise ValueError("Reference cell must be anchored!")
        # Find the target cell
        target = self.spreadsheet.iloc[
            reference.row + row_skip.value,
            reference.column + column_skip.value
        ]
        return Cell.offset(reference, row_skip, column_skip, target=target)


class _SheetVariable(object):
    """Encapsulate the sheet variables.

    Attributes:
        _variables (Dict[str, Cell]): Mapping from variable name to definition.
        description (Dict[str, str]): Description of concrete variable.
        spreadsheet (Sheet): Reference to spreadsheet instance.
    """
    def __init__(self, spreadsheet: 'Sheet'):
        """Initialize instance
        Args:
            spreadsheet (Sheet): Reference to spreadsheet instance.
        """
        self.spreadsheet: 'Sheet' = spreadsheet
        self._variables: Dict[str, Cell] = dict()
        self.description: Dict[str, str] = dict()

    @property
    def empty(self) -> bool:
        """Return True if the variable set is empty, False otherwise.

        Returns:
            bool: Return True if the variable set is empty, False otherwise.
        """
        return len(self._variables) == 0

    def __len__(self) -> int:
        """Overload length operator"""
        return len(self._variables)

    def __getitem__(self, item):
        """Overloads [item] operator getter"""
        return self.get_variable(item)

    def __setitem__(self, key, value):
        """Overloads [item] operator setter"""
        self.set_variable(key, value)

    def get_variable(self, name: str, /) -> Cell:  # noqa: E225
        """Get variable value as a Cell by its name.

        Args:
            name (str): Name of the variable

        Returns:
            Cell: variable
        """
        if name in self._variables:
            return self._variables[name]
        else:
            raise IndexError(f"Variable with name {name} does not exist in "
                             f"the system!")

    def set_variable(self,
                     name: str,
                     value: Union[str, Number, Cell],
                     description: Optional[str] = None) -> None:
        """Check the name consistency and set the variable.

        If the variable with given name is already in the dictionary, it is
            rewritten with a new value.

        Args:
            name (str): Unique name for the variable. Has to be lower case
                alphanumeric value maximally with underscore symbols.
            value (Union[str, Number]): A value to be set.
            description (Optional[str]): Description of the variable

        Raises:
            ValueError: If the structure of the name does not match the
                required pattern (lowercase alphanumeric and underscores only).

        Warning:
            The function str(VAL) is called on the value (it has to be stored
                as a string) when the result is exported to Excel!
        """
        # Check the consistency of name for variable
        if not isinstance(name, str):
            raise ValueError("Name has to be a string!")
        if ' ' in name:
            raise ValueError("Space is not allowed in the name of variable!")
        elif name.lower() != name:
            raise ValueError("Name of the variable has to be lowercase!")
        if re.match(r'^[a-z0-9_]+$', name):
            pass
        else:
            raise ValueError("Name of variable has to be alphanumeric value "
                             "with underscores!")

        self.description[name] = description
        if isinstance(value, Cell):
            self._variables[name] = value
            self._variables[name].is_variable = True
        else:
            self._variables[name] = Cell.variable(
                    Cell(None, None,  # No position
                         variable_name=name,
                         value=value,
                         is_variable=True,
                         cell_type=CellType.computational,
                         cell_indices=self.spreadsheet.cell_indices
                         )
                )

    def get_variables_dict(self, include_cell: bool = True) -> dict:
        """Serialize variables to dictionary.
        Args:
            include_cell (bool): If true, value 'cell' -> Cell is included.
        Returns:
            dict: serialization of variables to dictionary.
        """
        res = {}
        for _name, _var in self._variables.items():
            res[_name] = {
                'value': _var.value,
                'description': self.description[_name],
                'excel_format': _var.excel_format
            }
            if include_cell:
                res[_name]['cell'] = _var
        return res

    @property
    def variables_dict(self) -> dict:
        """Serialize variables to dictionary.
        Returns:
            dict: serialization of variables to dictionary.
        """
        return self.get_variables_dict(False)

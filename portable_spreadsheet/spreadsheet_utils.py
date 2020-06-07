from typing import Dict, Union, Optional, Tuple
import re
import copy
from numbers import Number

from .cell import Cell
from .cell_type import CellType

# ========== File with the functionality for internal purposes only ===========


class _Location(object):
    """Private class that enables indexing and slicing of values using
        obj.loc[col, row] or obj.iloc[col_idx, row_idx] logic.

    Attributes:
        spreadsheet (Spreadsheet): Reference to spreadsheet instance.
        by_integer (bool): If True, indices are computed using integer value,
            if False, labels (aliases, typically string) are used.
    """

    def __init__(self,
                 spreadsheet,
                 by_integer: bool):
        """Initialise location

        Args:
            spreadsheet (Spreadsheet): Reference to spreadsheet instance.
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
            index_p = self._parse_indices(index, has_slice)
            return self.spreadsheet._set_item(val, index_p)
        else:
            index_p = self._parse_indices(index, has_slice)
            return self.spreadsheet._set_slice(val, index_p)

    def __getitem__(self, index):
        """Get the item from the slice or single value.

        Args:
            index: standard tuple of indices or tuple of slices.
        """
        has_slice = isinstance(index[0], slice) or isinstance(index[1], slice)
        if not has_slice:
            index_p = self._parse_indices(index, has_slice)
            return self.spreadsheet._get_item(index_p)
        else:
            index_p = self._parse_indices(index, has_slice)
            return self.spreadsheet._get_slice(index_p)

    def __delitem__(self, index):
        """Safely delete a single cell or the slice of cells inside the
            spreadsheet.

        Args:
            index: standard tuple of indices or tuple of slices.
        """
        has_slice = isinstance(index[0], slice) or isinstance(index[1], slice)
        if not has_slice:
            index_p = self._parse_indices(index, has_slice)
            return self.spreadsheet._delete_single_cell(index_p)
        else:
            index_p = self._parse_indices(index, has_slice)
            return self.spreadsheet._delete_cell_slice(index_p)

    def _parse_indices(
            self, index: tuple, has_slice: bool
    ) -> Union[Tuple[int, int, int, int, int, int], Tuple[int, int]]:
        """Parse the indices of the sheet (for both positional/integer indexing
            and labels indexing).

        Args:
            index (tuple): Index of cell/cells expressed using integer or
                label as indices
            has_slice (bool): If true, return slices

        Returns:

            Union[Tuple[int, int, int, int, int, int], Tuple[int, int]]:
                Position of the slice or cell by rows/columns,
                tuples contains (start, end, step) OR just (row, column).
        """
        if len(index) != 2:
            raise IndexError("Index has to be either slice or position of "
                             "cell/cells but always has dimension TWO.")

        if not self.by_integer:
            if isinstance(index[0], slice):
                # If the first index is slice
                _x_start = 0
                if index[0].start:
                    _x_start = self.spreadsheet.cell_indices.rows_labels.index(
                        index[0].start)
                _x_end = self.spreadsheet.shape[0]
                if index[0].stop:
                    _x_end = self.spreadsheet.cell_indices.rows_labels.index(
                        index[0].stop)
                _x_step = 1
                if index[0].step:
                    _x_step = int(index[0].step)
            else:
                # If the first index is scalar
                _x_start = self.spreadsheet.cell_indices.rows_labels.index(
                    index[0])
                _x_end = _x_start + 1
                _x_step = 1

            if isinstance(index[1], slice):
                # If the second index is slice
                _y_start = 0
                if index[1].start:
                    _y_start = \
                        self.spreadsheet.cell_indices.columns_labels.index(
                            index[1].start)
                _y_end = self.spreadsheet.shape[1]
                if index[1].stop:
                    _y_end = \
                        self.spreadsheet.cell_indices.columns_labels.index(
                            index[1].stop)
                _y_step = 1
                if index[1].step:
                    _y_step = int(index[1].step)
            else:
                # If the first index is scalar
                _y_start = self.spreadsheet.cell_indices.columns_labels.index(
                    index[1])
                _y_end = _y_start + 1
                _y_step = 1

        if self.by_integer:
            if isinstance(index[0], slice):
                # If the first index is slice
                _x_start = 0
                if index[0].start:
                    _x_start = int(index[0].start)
                    # Negative index starts from end
                    if _x_start < 0:
                        _x_start = self.spreadsheet.shape[0] + _x_start
                _x_end = self.spreadsheet.shape[0]
                if index[0].stop:
                    _x_end = int(index[0].stop)
                    # Negative index starts from end
                    if _x_end < 0:
                        _x_end = self.spreadsheet.shape[0] + _x_end
                _x_step = 1
                if index[0].step:
                    _x_step = int(index[0].step)
            else:
                # If the first index is scalar
                _x_start = index[0]
                # Negative index starts from end
                if _x_start < 0:
                    _x_start = self.spreadsheet.shape[0] + _x_start
                _x_end = _x_start + 1
                _x_step = 1

            if isinstance(index[1], slice):
                # If the second index is slice
                _y_start = 0
                if index[1].start:
                    _y_start = int(index[1].start)
                    # Negative index starts from end
                    if _y_start < 0:
                        _y_start = self.spreadsheet.shape[1] + _y_start
                _y_end = self.spreadsheet.shape[1]
                if index[1].stop:
                    _y_end = int(index[1].stop)
                    # Negative index starts from end
                    if _y_end < 0:
                        _y_end = self.spreadsheet.shape[1] + _y_end
                _y_step = 1
                if index[1].step:
                    _y_step = int(index[1].step)
            else:
                # If the first index is scalar
                _y_start = index[1]
                # Negative index starts from end
                if _y_start < 0:
                    _y_start = self.spreadsheet.shape[1] + _y_start
                _y_end = _y_start + 1
                _y_step = 1

        # Sanity check for selected indices
        # All indices has to be integers
        diff_sum = (abs(_x_start - int(_x_start)) +
                    abs(_x_step - int(_x_step)) +
                    abs(_x_end - int(_x_end)) +
                    abs(_y_start - int(_y_start)) +
                    abs(_y_step - int(_y_step)) +
                    abs(_y_end - int(_y_end)))
        if _x_start < 0 or \
                _y_start < 0 or \
                _x_step < 0 or \
                _y_step < 0 or \
                _x_end > self.spreadsheet.shape[0] or \
                _y_end > self.spreadsheet.shape[1] or \
                _x_start > _x_end or \
                _y_start > _y_end or \
                _x_step > _x_end or \
                _y_step > _y_end or \
                diff_sum > 0.00001:
            raise IndexError("Index is out of bound!")

        # Return slices
        if has_slice:
            return int(_x_start), int(_x_end), int(_x_step), int(_y_start), \
                   int(_y_end), int(_y_step)
        # Return cell index
        return int(_x_start), int(_y_start)


class _Functionality(object):
    """Class encapsulating some shortcuts for functionality.

    Attributes:
        spreadsheet (Spreadsheet): Reference to spreadsheet instance.
    """

    def __init__(self, spreadsheet):
        """
        Args:
            spreadsheet (Spreadsheet): Reference to spreadsheet instance.
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
                    alternative: Cell, /) -> Cell:  # noqa E225
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
               column_skip: Cell, /) -> Cell:  # noqa E225
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


class _SheetVariables(object):
    """Encapsulate the sheet variables.

    Attributes:
        _variables (Dict[str, object]): Dictionary with variables, key is the
            name of the variable and value is the actual value assigned to the
            variable.
        spreadsheet (Spreadsheet): Reference to spreadsheet instance.
    """
    def __init__(self, spreadsheet):
        """
        Args:
            spreadsheet (Spreadsheet): Reference to spreadsheet instance.
        """
        self._variables: Dict[str, Dict[str, object]] = {}
        self.spreadsheet = spreadsheet

    def set_variable(self,
                     name: str,
                     value: Union[str, Number],
                     description: Optional[str] = None,
                     exclude_description_update: bool = False) -> None:
        """Check the name consistency and set the variable.

        If the variable with given name is already in the dictionary, it is
            rewritten with a new value.

        Args:
            name (str): Unique name for the variable. Has to be lower case
                alphanumeric value maximally with underscore symbols.
            value (Union[str, Number]): A value to be set.
            description (Optional[str]): Description of the variable
            exclude_description_update (bool): If true, description is not
                updated

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
                             "maximally with underscores!")

        # Use the existing description if required
        if name in self._variables.keys():
            if exclude_description_update:
                description = self._variables[name]["description"]

        # Add the value to the dictionary:
        self._variables[name] = {
            "value": value,
            "description": description
        }

    @property
    def variables_dict(self) -> Dict[str, Dict[str, object]]:
        """Return the variables as a read-only dictionary with keys as a name
            of variable and value as actual value of the variable.

        Returns:
            Dict[str, Dict[str, object]]: Read-only dictionary with names of
                variables (keys) and their values and description (value).
                Example: 'key' -> {'value': VALUE, "description": DESCRIPTION}
        """
        return copy.deepcopy(self._variables)

    def variable_exist(self, name: str) -> bool:
        """Returns true if the variable exist in the dictionary.

        Args:
            name (str): Unique name for the variable. Has to be lower case
                alphanumeric value maximally with underscore symbols.
        Return:
            bool: True if variable exists in the system, False otherwise.
        """
        return str(name) in self._variables.keys()

    def get_variable(self, name: str, /) -> Cell:  # noqa E225
        """Get variable value as a new Cell by its name.

        Args:
            name (str): Name of the variable
        """
        if self.variable_exist(name):
            return Cell.variable(
                Cell(None,
                     None,
                     variable_name=name,
                     value=self._variables[name]['value'],
                     is_variable=True,
                     cell_type=CellType.computational,
                     cell_indices=self.spreadsheet.cell_indices
                     )
            )
        else:
            raise ValueError(f"Variable with name {name} does not exist in "
                             f"the system!")

    def __getitem__(self, item):
        """Overloads [item] operator getter"""
        return self.get_variable(item)

    def __setitem__(self, key, value):
        """Overloads [item] operator setter"""
        self.set_variable(key, value, exclude_description_update=True)

    @property
    def empty(self) -> bool:
        """Return True if the variable set is empty, False otherwise.

        Returns:
            bool: Return True if the variable set is empty, False otherwise.
        """
        return len(self._variables) == 0

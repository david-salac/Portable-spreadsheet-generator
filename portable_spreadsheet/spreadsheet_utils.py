from typing import Dict, Union, Optional
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
        _excel_format (Dict[str, dict]): Style/format for showing values of
            selected variables.
        spreadsheet (Spreadsheet): Reference to spreadsheet instance.
    """
    def __init__(self, spreadsheet):
        """
        Args:
            spreadsheet (Spreadsheet): Reference to spreadsheet instance.
        """
        self._variables: Dict[str, Dict[str, object]] = {}
        self._excel_format: Dict[str, dict] = {}
        self.spreadsheet = spreadsheet

    @property
    def excel_format(self):
        """Return the dictionary defining Excel format for the XlsxWriter.

        Read the documentation: https://xlsxwriter.readthedocs.io/format.html

        Returns:
            Dict[str, dict]: Dictionary defining Excel format for XlsxWriter.
        """
        return self._excel_format

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

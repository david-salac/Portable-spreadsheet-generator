from numbers import Number
from typing import Iterable, Tuple, Union, List, Optional
import copy

import numpy as np

from .cell import Cell
from .cell_indices import CellIndices
from .serialization import Serialization

# Acceptable values for the slice
T_slice = Union[np.ndarray, List[Number], List[Cell], Number, Cell]


class CellSlice(Serialization):
    """Encapsulate aggregating functionality and setting of the slices.

    Attributes:
        start_idx (Tuple[int, int]): Integer position of the starting cell
            inside the spreadsheet. Top left cell of the slice.
        end_idx (Tuple[int, int]): Integer position of the ending cell
            inside the spreadsheet. Bottom right cell of the slice.
        start_cell (Cell): Top left cell of the slice.
        end_cell (Cell): Bottom right cell of the slice.
        cell_subset (Iterable[Cell]): The list of all cells in the slice.
        driving_sheet (Spreadsheet): Reference to the spreadsheet.
    """
    def __init__(self,
                 start_idx: Tuple[int, int],
                 end_idx: Tuple[int, int],
                 cell_subset: Iterable[Cell],
                 driving_sheet
                 ):
        """Create a cell slice from the spreadsheet.

        Args:
            start_idx (Tuple[int, int]): Integer position of the starting cell
                inside the spreadsheet. Top left cell of the slice.
            end_idx (Tuple[int, int]): Integer position of the ending cell
                inside the spreadsheet. Bottom right cell of the slice.
            cell_subset (Iterable[Cell]): The list of all cells in the slice.
            driving_sheet (Spreadsheet): Reference to the spreadsheet.
        """
        # Initialise functionality for serialization:
        super().__init__(export_offset=start_idx,
                         warning_logger=driving_sheet.warning_logger,
                         export_subset=True)

        self.start_idx: Tuple[int, int] = start_idx
        self.end_idx: Tuple[int, int] = end_idx
        self.start_cell: Cell = driving_sheet.iloc[start_idx]
        self.end_cell: Cell = driving_sheet.iloc[end_idx]
        self.cell_subset: Iterable[Cell] = cell_subset
        self.driving_sheet = driving_sheet

    def sum(self, skip_none_cell: bool = True) -> Cell:
        """Compute the sum of the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.sum(self.start_cell, self.end_cell, cell_subset)

    def product(self, skip_none_cell: bool = True) -> Cell:
        """Compute the product of the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.product(self.start_cell, self.end_cell, cell_subset)

    def min(self, skip_none_cell: bool = True) -> Cell:
        """Find the minimum of the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.min(self.start_cell, self.end_cell, cell_subset)

    def max(self, skip_none_cell: bool = True) -> Cell:
        """Find the maximum of the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.max(self.start_cell, self.end_cell, cell_subset)

    def mean(self, skip_none_cell: bool = True) -> Cell:
        """Compute the mean-average of the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.mean(self.start_cell, self.end_cell, cell_subset)

    def average(self, skip_none_cell: bool = True) -> Cell:
        """Compute the mean-average of the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        return self.mean(skip_none_cell=skip_none_cell)

    def stdev(self, skip_none_cell: bool = True) -> Cell:
        """Compute the standard deviation of the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.stdev(self.start_cell, self.end_cell, cell_subset)

    def median(self, skip_none_cell: bool = True) -> Cell:
        """Compute the median of the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.median(self.start_cell, self.end_cell, cell_subset)

    def count(self, skip_none_cell: bool = True) -> Cell:
        """Compute the number of items in the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.count(self.start_cell, self.end_cell, cell_subset)

    def irr(self, skip_none_cell: bool = True) -> Cell:
        """Compute the Internal Rate of Return (IRR) of items in the aggregate.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: a new cell with the result.
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.irr(self.start_cell, self.end_cell, cell_subset)

    def match_negative_before_positive(self,
                                       skip_none_cell: bool = True) -> Cell:
        """Find the position of the last negative number in the series that
            is located just before the first non-negative number.

        Args:
            skip_none_cell (bool): If true, skips all the cells with None as
                a value (and does not raise exception).

        Returns:
            Cell: Return the position of the negative number in a series that
                is located just before the first positive number (or zero).
        """
        if skip_none_cell:
            cell_subset = [nn_cell for nn_cell in self.cell_subset
                           if nn_cell.value is not None]
        else:
            cell_subset = self.cell_subset
        return Cell.match_negative_before_positive(self.start_cell,
                                                   self.end_cell, cell_subset)

    @property
    def excel_format(self):
        """Should not be accessible for slides."""
        raise NotImplementedError

    @excel_format.setter
    def excel_format(self, new_format: dict):
        """Set the Excel cell format/style.

        Read the documentation: https://xlsxwriter.readthedocs.io/format.html

        Args:
            new_format (dict): New format definition.
        """
        if not isinstance(new_format, dict):
            raise ValueError("New format has to be a dictionary!")
        for row in range(self.start_idx[0], self.end_idx[0] + 1):
            for col in range(self.start_idx[1],
                             self.end_idx[1] + 1):
                self.driving_sheet.iloc[row, col].excel_format = new_format

    @property
    def description(self) -> Optional[str]:
        """Not implementable.
        """
        raise NotImplementedError

    @description.setter
    def description(self, new_description: Optional[str]):
        """Set the cell description.

        Args:
            new_description (Optional[str]): description of the cell.
        """
        if (new_description is not None
                and not isinstance(new_description, str)):
            raise ValueError("Cell description has to be a string value!")
        for row in range(self.start_idx[0], self.end_idx[0] + 1):
            for col in range(self.start_idx[1],
                             self.end_idx[1] + 1):
                self.driving_sheet.iloc[row, col].description = new_description

    def _set_value_on_position(self, other: Union[Cell, Number],
                               row: int, col: int) -> None:
        """Set the cell on given position in the spreadsheet to the value
            'other'.
        Args:
            other (Union[Cell, Number]): new value to be set.
            row (int): the row integer position in the spreadsheet (indexed
                from 0).
            col (int): the column integer position in the spreadsheet (indexed
                from 0).
        """
        if isinstance(other, Cell):
            # Set the right values
            if other.anchored:
                self.driving_sheet.iloc[row, col] = \
                    Cell.reference(other)
            else:
                # Create a deep copy
                self.driving_sheet.iloc[row, col] = \
                    copy.deepcopy(other)
                # Anchor it:
                self.driving_sheet.iloc[row, col].coordinates = (row, col)
        else:
            # Call the external logic to manage the same
            self.driving_sheet.iloc[row, col] = other

    # Set to scalar / Other cells:
    def set(self, other: T_slice) -> None:
        """Set all the values in the slice to the new one (or the list of
            values).

        Args:
            other: Union[np.ndarray, List[Number], List[Cell], Number, Cell]:
                Some value or list (or numpy array) of values that should be
                set for all the cells inside slice.
        """
        if isinstance(other, (np.ndarray, list)):
            dim_match = True
            is_list = True
            is_1d = False
            by_row = self.shape[0] > self.shape[1]
            if hasattr(other, "shape"):
                dim_match = other.shape == self.shape
                is_list = False
                is_1d = len(other.shape) == 1
                if is_1d:
                    dim_match = max(other.shape) == max(self.shape)
            else:
                is_list = True
                if min(self.shape) == 1:
                    dim_match = len(other) == max(self.shape)
                    is_1d = True
            if not dim_match:
                raise ValueError("Shape of the input does not match to the "
                                 "shape of the slice!")
            if is_1d:
                col = self.start_idx[1]
                row = self.start_idx[0]
                for val in other:
                    self._set_value_on_position(val, row, col)
                    if by_row:
                        row += 1
                    else:
                        col += 1
            else:
                # If is N-dimensional
                for row in range(self.start_idx[0], self.end_idx[0] + 1):
                    for col in range(self.start_idx[1],
                                     self.end_idx[1] + 1):
                        if is_list:
                            val = other[row - self.start_idx[0]][
                                col - self.start_idx[1]
                            ]
                        else:
                            val = other[
                                row - self.start_idx[0],
                                col - self.start_idx[1]
                            ]
                        self._set_value_on_position(val, row, col)

        else:
            for row in range(self.start_idx[0], self.end_idx[0] + 1):
                for col in range(self.start_idx[1], self.end_idx[1] + 1):
                    # Set the right values
                    self._set_value_on_position(other, row, col)

    def __ilshift__(self, other: T_slice):
        """Overrides operator <<= to do a set functionality.
        """
        self.set(other)

    # ==== OVERRIDE ABSTRACT METHODS AND PROPERTIES OF SERIALIZATION CLASS ====
    @Serialization.shape.getter
    def shape(self) -> Tuple[int, int]:
        """Return the shape of the sheet in the NumPy logic.

        Returns:
            Tuple[int]: Number of rows, Number of columns
        """
        return (self.end_idx[0] - self.start_idx[0] + 1,
                self.end_idx[1] - self.start_idx[1] + 1)

    @Serialization.cell_indices.getter
    def cell_indices(self) -> CellIndices:
        """Get the cell indices.

        Returns:
            CellIndices: Cell indices of the spreadsheet.
        """
        return self.driving_sheet._cell_indices

    def _get_cell_at(self, row: int, column: int) -> 'Cell':
        """Get the particular cell on the (row, column) position.

        Returns:
            Cell: The call on given position.
        """
        return self.driving_sheet.iloc[self.start_idx[0] + row,
                                       self.start_idx[1] + column]

    def _get_variables(self):
        """Return the sheet variables as _SheetVariables object.

        Returns:
            _SheetVariables: Sheet variables.
        """
        return self.driving_sheet.var
    # =========================================================================

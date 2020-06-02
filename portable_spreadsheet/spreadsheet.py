from numbers import Number
from typing import Tuple, List, Union, Optional, Callable
import copy

from .cell import Cell
from .cell_indices import CellIndices, T_lg_col_row
from .cell_slice import CellSlice
from .spreadsheet_utils import _Location, _Functionality, _SheetVariables
from .serialization import Serialization

# ==== TYPES ====
# Type for the sheet (list of the list of the cells)
T_sheet = List[List[Cell]]
# Sheet cell value
T_cell_val = Union[Number, Cell]
# ===============


class Spreadsheet(Serialization):
    """Simple spreadsheet that keeps tracks of each operations in defined
        languages.

    Logic allows export sheets to Excel files (and see how each cell is
        computed), to the JSON strings with description of computation e. g.
        in native language. It also allows to reconstruct behaviours in native
        Python with Numpy.

    Attributes:
        self.cell_indices (CellIndices): Define indices and the shape of the
            spreadsheet.
        _sheet (T_sheet): Array holding actual sheet.
        iloc (_Location): To make cells accessible using
            obj.iloc[integer_index_x, integer_index_y]
        loc (_Location): To make cells accessible using
            obj.loc[nick_x, nick_y]
        fn (_Functionality): To make accessible shortcuts for functionality
        var (_SheetVariables): Variables in the sheet.
    """

    def __init__(self,
                 cell_indices: CellIndices,
                 warning_logger: Optional[Callable[[str], None]] = None):
        """Initialize the spreadsheet object

        Args:
            cell_indices (CellIndices): The definition of the shape and columns
                and rows labels, help texts and descriptors.
            warning_logger (Optional[Callable[[str], None]]): Function that
                logs the warnings (or None if skipped).
        """
        # Initialise functionality for serialization:
        super().__init__(warning_logger=warning_logger)

        self._cell_indices: CellIndices = copy.deepcopy(cell_indices)

        self._sheet: T_sheet = self._initialise_array()
        # To make cells accessible using obj.iloc[pos_x, pos_y]
        self.iloc: _Location = _Location(self, True)
        # To make cells accessible using obj.loc[nick_x, nick_y]
        self.loc: _Location = _Location(self, False)
        # To make accessible shortcuts for functionality
        self.fn: _Functionality = _Functionality(self)
        # Variables of the sheet
        self.var: _SheetVariables = _SheetVariables(self)

    @staticmethod
    def create_new_sheet(
            number_of_rows: int,
            number_of_columns: int,
            rows_columns: Optional[T_lg_col_row] = None,
            /, *,  # noqa E999
            rows_labels: List[str] = None,
            columns_labels: List[str] = None,
            rows_help_text: List[str] = None,
            columns_help_text: List[str] = None,
            excel_append_row_labels: bool = True,
            excel_append_column_labels: bool = True,
            warning_logger: Optional[Callable[[str], None]] = None
    ) -> 'Spreadsheet':
        """Direct way of creating instance.

        Args:
            number_of_rows (int): Number of rows.
            number_of_columns (int): Number of columns.
            rows_columns (T_lg_col_row): List of all row names and column names
                for each user defined language.
            rows_labels (List[str]): List of masks (aliases) for row
                names.
            columns_labels (List[str]): List of masks (aliases) for column
                names.
            rows_help_text (List[str]): List of help texts for each row.
            columns_help_text (List[str]): List of help texts for each column.
            excel_append_row_labels (bool): If True, one column is added
                on the beginning of the sheet as a offset for labels.
            excel_append_column_labels (bool): If True, one row is added
                on the beginning of the sheet as a offset for labels.
            warning_logger (Optional[Callable[[str], None]]): Function that
                logs the warnings (or None if skipped).

        Returns:
            Spreadsheet: New instance of spreadsheet.
        """
        class_index = CellIndices(
            number_of_rows,
            number_of_columns,
            rows_columns,
            rows_labels=rows_labels,
            columns_labels=columns_labels,
            rows_help_text=rows_help_text,
            columns_help_text=columns_help_text,
            excel_append_row_labels=excel_append_row_labels,
            excel_append_column_labels=excel_append_column_labels,
            warning_logger=warning_logger
        )
        return Spreadsheet(class_index, warning_logger)

    def _initialise_array(self) -> T_sheet:
        """Initialise the first empty spreadsheet array on the beginning.

        Returns:
            T_sheet: New empty spreadsheet.
        """
        array: T_sheet = []
        for row_idx in range(self.cell_indices.shape[0]):
            row: List[Cell] = []
            for col_idx in range(self.cell_indices.shape[1]):
                row.append(Cell(row_idx, col_idx,
                                cell_indices=self.cell_indices))
            array.append(row)
        return array

    def _set_item(self,
                  value: T_cell_val,
                  index_integer: Tuple[int, int] = None,
                  index_label: Tuple[object, object] = None) -> None:
        """Set the spreadsheet cell on the desired index to the new value.

        Args:
            value (T_cell_val): New value to be inserted.
            index_integer (Tuple[int, int]): Return the value on the integer
                index (row, column) inside spreadsheet (indexed from 0).
            index_label (Tuple[str, str]): Return the value on the index
                (row label, column label) inside spreadsheet.
        """
        if index_integer is not None and index_label is not None:
            raise ValueError("Only one of parameters 'index_integer' and"
                             "'index_label' has to be set!")
        if index_label is not None:
            _x = self.cell_indices.rows_labels.index(index_label[0])
            _y = self.cell_indices.columns_labels.index(index_label[1])
            index_integer = (_x, _y)
        if index_integer is not None:
            _x = index_integer[0]
            _y = index_integer[1]
            # If negative, take n-th item from the end
            if _x < 0:
                _x += self.shape[0]
            if _y < 0:
                _y += self.shape[1]
            if isinstance(value, Cell):
                if value.anchored:
                    _value = Cell.reference(value)
                else:
                    # Create a deep copy
                    _value = copy.deepcopy(value)
                    # Anchor it:
                    _value.coordinates = (_x, _y)
            else:
                _value = Cell(_x, _y,
                              value=value, cell_indices=self.cell_indices)
            self._sheet[_x][_y] = _value

    def _get_item(self,
                  index_integer: Tuple[int, int] = None,
                  index_label: Tuple[object, object] = None) -> Cell:
        """Get the cell on the particular index.

        Args:
            index_integer (Tuple[int, int]): Return the value on the integer
                index (row, column) inside spreadsheet (indexed from 0).
            index_label (Tuple[str, str]): Return the value on the index
                (row label, column label) inside spreadsheet.

        Returns:
            Cell: The Cell on the desired index.
        """
        if index_integer is not None and index_label is not None:
            raise ValueError("Only one of parameters 'index_integer' and"
                             "'index_label' has to be set!")
        if index_label is not None:
            _x = self.cell_indices.rows_labels.index(index_label[0])
            _y = self.cell_indices.columns_labels.index(index_label[1])
            index_integer = (_x, _y)
        if index_integer is not None:
            _x = index_integer[0]
            _y = index_integer[1]
            # If negative, take n-th item from the end
            if _x < 0:
                _x += self.shape[0]
            if _y < 0:
                _y += self.shape[1]
            return self._sheet[_x][_y]

    def _get_slice(self,
                   index_integer: Tuple[slice, slice],
                   index_label: Tuple[slice, slice]) -> CellSlice:
        """Get the values in the slice.

        Args:
            index_integer (Tuple[int, int]): The position of the slice in the
                spreadsheet. Mutually exclusive with parameter index_label
            index_label (Tuple[object, object]): The position of the slice
                in the spreadsheet. Mutually exclusive with parameter
                index_integer (only one can be set to not None).
        Returns:
            CellSlice: Slice of the cells (aggregate).
        """
        if index_integer is not None and index_label is not None:
            raise ValueError("Only one of parameters 'index_integer' and"
                             "'index_label' has to be set!")

        if index_label is not None:
            if isinstance(index_label[0], slice):
                # If the first index is slice
                _x_start = 0
                if index_label[0].start:
                    _x_start = self.cell_indices.rows_labels.index(
                        index_label[0].start)
                _x_end = self.shape[0]
                if index_label[0].stop:
                    _x_end = self.cell_indices.rows_labels.index(
                        index_label[0].stop)
                _x_step = 1
                if index_label[0].step:
                    _x_step = int(index_label[0].step)
            else:
                # If the first index is scalar
                _x_start = self.cell_indices.rows_labels.index(
                    index_label[0])
                _x_end = _x_start + 1
                _x_step = 1

            if isinstance(index_label[1], slice):
                # If the second index is slice
                _y_start = 0
                if index_label[1].start:
                    _y_start = self.cell_indices.columns_labels.index(
                        index_label[1].start)
                _y_end = self.shape[1]
                if index_label[1].stop:
                    _y_end = self.cell_indices.columns_labels.index(
                        index_label[1].stop)
                _y_step = 1
                if index_label[1].step:
                    _y_step = int(index_label[1].step)
            else:
                # If the first index is scalar
                _y_start = self.cell_indices.columns_labels.index(
                    index_label[1])
                _y_end = _y_start + 1
                _y_step = 1

        if index_integer is not None:
            if isinstance(index_integer[0], slice):
                # If the first index is slice
                _x_start = 0
                if index_integer[0].start:
                    _x_start = int(index_integer[0].start)
                    # Negative index starts from end
                    if _x_start < 0:
                        _x_start = self.shape[0] + _x_start
                _x_end = self.shape[0]
                if index_integer[0].stop:
                    _x_end = int(index_integer[0].stop)
                    # Negative index starts from end
                    if _x_end < 0:
                        _x_end = self.shape[0] + _x_end
                _x_step = 1
                if index_integer[0].step:
                    _x_step = int(index_integer[0].step)
            else:
                # If the first index is scalar
                _x_start = index_integer[0]
                _x_end = _x_start + 1
                _x_step = 1

            if isinstance(index_integer[1], slice):
                # If the second index is slice
                _y_start = 0
                if index_integer[1].start:
                    _y_start = int(index_integer[1].start)
                    # Negative index starts from end
                    if _y_start < 0:
                        _y_start = self.shape[1] + _y_start
                _y_end = self.shape[1]
                if index_integer[1].stop:
                    _y_end = int(index_integer[1].stop)
                    # Negative index starts from end
                    if _y_end < 0:
                        _y_end = self.shape[1] + _y_end
                _y_step = 1
                if index_integer[1].step:
                    _y_step = int(index_integer[1].step)
            else:
                # If the first index is scalar
                _y_start = index_integer[1]
                _y_end = _y_start + 1
                _y_step = 1

        # Create the CellSlice object
        cell_subset = []
        for x in range(_x_start, _x_end, _x_step):
            for y in range(_y_start, _y_end, _y_step):
                cell_subset.append(self.iloc[x, y])
        cell_slice: CellSlice = CellSlice((_x_start, _y_start),
                                          (_x_end - 1, _y_end - 1),
                                          cell_subset,
                                          self)
        return cell_slice

    def _set_slice(self,
                   value: T_cell_val,
                   index_integer: Tuple[int, int],
                   index_label: Tuple[object, object]) -> None:
        """Set the value of each cell in the slice

        Args:
            value (T_cell_val): New value to be set.
            index_integer (Tuple[int, int]): The position of the slice in the
                spreadsheet. Mutually exclusive with parameter index_label
            index_label (Tuple[object, object]): The position of the slice
                in the spreadsheet. Mutually exclusive with parameter
                index_integer (only one can be set to not None).
        """
        cell_slice: CellSlice = self._get_slice(index_integer, index_label)
        cell_slice.set(value)

    def expand(self,
               new_number_of_rows: int,
               new_number_of_columns: int,
               new_rows_columns: Optional[T_lg_col_row] = {},
               /, *,  # noqa E225
               new_rows_labels: List[str] = None,
               new_columns_labels: List[str] = None,
               new_rows_help_text: List[str] = None,
               new_columns_help_text: List[str] = None
               ):
        """Expand the size of the table.

        Args:
            new_number_of_rows (int): Number of rows to be added.
            new_number_of_columns (int): Number of columns to be added.
            new_rows_columns (T_lg_col_row): List of all row names and column
                names for each language to be added.
            new_rows_labels (List[str]): List of masks (aliases) for row
                names to be added.
            new_columns_labels (List[str]): List of masks (aliases) for
                column names to be added.
            new_rows_help_text (List[str]): List of help texts for each row to
                be added.
            new_columns_help_text (List[str]): List of help texts for each
                column to be added.
        """
        self.expand_using_cell_indices(
            self.cell_indices.expand_size(
                new_number_of_rows,
                new_number_of_columns,
                new_rows_columns,

                new_rows_labels=new_rows_labels,
                new_columns_labels=new_columns_labels,
                new_rows_help_text=new_rows_help_text,
                new_columns_help_text=new_columns_help_text
            )
        )

    def expand_using_cell_indices(self, cell_indices: CellIndices) -> None:
        """Resize the spreadsheet object to the greater size

        Args:
            cell_indices (CellIndices): The definition of the shape and columns
                and rows labels, help texts and descriptors.
        """
        shape_origin = self.shape
        self._cell_indices = copy.deepcopy(cell_indices)
        for row_idx in range(self.shape[0]):
            if row_idx >= shape_origin[0]:
                # Append wholly new rows
                row: List[Cell] = []
                for col in range(self.cell_indices.shape[1]):
                    row.append(Cell(cell_indices=self.cell_indices))
                self._sheet.append(row)
            else:
                # Expand columns:
                for col in range(self.cell_indices.shape[1] - shape_origin[1]):
                    self._sheet[row_idx].append(
                        Cell(cell_indices=self.cell_indices)
                    )
            for col_idx in range(self.shape[1]):
                # Has to refresh cell indices everywhere inside
                self.iloc[row_idx,
                          col_idx].cell_indices = self.cell_indices

    # ==== OVERRIDE ABSTRACT METHODS AND PROPERTIES OF SERIALIZATION CLASS ====
    @Serialization.shape.getter
    def shape(self) -> Tuple[int, int]:
        """Return the shape of the sheet in the NumPy logic.

        Returns:
            Tuple[int]: Number of rows, Number of columns
        """
        return self.cell_indices.shape

    @Serialization.cell_indices.getter
    def cell_indices(self) -> CellIndices:
        """Get the cell indices.

        Returns:
            CellIndices: Cell indices of the spreadsheet.
        """
        return self._cell_indices

    def _get_cell_at(self, row: int, column: int) -> 'Cell':
        """Get the particular cell on the (row, column) position.

        Returns:
            Cell: The call on given position.
        """
        return self.iloc[row, column]

    def _get_variables(self) -> '_SheetVariables':
        """Return the sheet variables as _SheetVariables object.

        Returns:
            _SheetVariables: Sheet variables.
        """
        return self.var
    # =========================================================================

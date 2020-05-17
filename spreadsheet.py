from typing import Tuple, List, Dict, Union
import copy

import xlsxwriter

from cell import Cell
from cell_indices import CellIndices
from cell_type import CellType

# ==== TYPES ====
# Type for the sheet (list of the list of the cells)
T_sheet = List[List[Cell]]
# Type for the output dictionary with the
#   logic: 'columns'/'rows' -> col/row key -> 'rows'/'columns' -> row/col key
#   -> (pseudo)language -> value
T_out_dict = Dict[
    str,  # 'Rows'/'Columns'
    Dict[
        object,  # Rows/Column key
        Union[
            # For values:
            Dict[
                str,  # 'Columns'/'Rows' (in iversion order to above)
                Union[
                    Dict[object, Dict[str, Union[str, float]]],  # Values
                    str  # For help text
                     ]
                ],
            str  # For help text
            ]
    ]
]
# ===============


class Spreadsheet(object):
    class _Location(object):
        def __init__(self,
                     spreadsheet: 'Spreadsheet',
                     by_integer: bool):
            self.spreadsheet: 'Spreadsheet' = spreadsheet
            self.by_integer: str = by_integer

        def __setitem__(self, index, val):
            if self.by_integer:
                self.spreadsheet._set_item(val, index, None)
            else:
                self.spreadsheet._set_item(val, None, index)

        def __getitem__(self, index):
            if self.by_integer:
                return self.spreadsheet._get_item(index, None)
            else:
                return self.spreadsheet._get_item(None, index)

    def __init__(self,
                 cell_indices: CellIndices):
        """Initialize the spreadsheet object

        Args:
            cell_indices (CellIndices): The definition of the shape and columns
                and rows labels, help texts and descriptors.
        """
        self.cell_indices: CellIndices = copy.deepcopy(cell_indices)

        self._sheet: T_sheet = self._initialise_array()
        # To make cells accessible using obj.loc[nick_x, nick_y]
        self.iloc = self._Location(self, True)
        # To make cells accessible using obj.iloc[pos_x, pos_y]
        self.loc = self._Location(self, False)

    def _initialise_array(self) -> T_sheet:
        array: T_sheet = []
        for row_idx in range(self.cell_indices.shape[0]):
            row: List[Cell] = []
            for col_idx in range(self.cell_indices.shape[1]):
                row.append(Cell(cell_indices=self.cell_indices))
            array.append(row)
        return array

    def _set_item(self, value,
                  index_integer: Tuple[int, int] = None,
                  index_nickname: Tuple[object, object] = None):
        if index_integer is not None and index_nickname is not None:
            raise ValueError("Only one of parameters 'index_integer' and"
                             "'index_nickname' has to be set!")
        if index_nickname is not None:
            _x = self.cell_indices.rows_nicknames.index(index_nickname[0])
            _y = self.cell_indices.rows_nicknames.index(index_nickname[1])
            index_integer = (_x, _y)
        if index_integer is not None:
            _value = value
            if not isinstance(value, Cell):
                _value = Cell(index_integer[0], index_integer[1],
                              value=value, cell_indices=self.cell_indices)
            self._sheet[index_integer[0]][index_integer[1]] = _value

    def _get_item(self,
                  index_integer: Tuple[int, int] = None,
                  index_nickname: Tuple[object, object] = None) -> Cell:
        if index_integer is not None and index_nickname is not None:
            raise ValueError("Only one of parameters 'index_integer' and"
                             "'index_nickname' has to be set!")
        if index_nickname is not None:
            _x = self.cell_indices.rows_nicknames.index(index_nickname[0])
            _y = self.cell_indices.rows_nicknames.index(index_nickname[1])
            index_integer = (_x, _y)
        if index_integer is not None:
            return self._sheet[index_integer[0]][index_integer[1]]

    def expand_size(self, cell_indices: CellIndices):
        """Resize the spreadsheet object to the greather size

        Args:
            cell_indices (CellIndices): The definition of the shape and columns
                and rows labels, help texts and descriptors.
        """
        shape_origin = self.shape
        self.cell_indices = copy.deepcopy(cell_indices)
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
                pass

    @property
    def shape(self) -> Tuple[int]:
        return self.cell_indices.shape

    def to_excel(self, file_path: str, sheet_name: str = "Results") -> None:
        """Export the values inside Spreadsheet instance to the
            Excel 2010 compatible .xslx file

        Args:
            file_path (str): Path to the target .xlsx file.
            sheet_name (str): The name of the sheet inside the file.
        """
        # Quick sanity check
        if ".xlsx" not in file_path[-5:]:
            raise ValueError("Suffix of the file has to be '.xslx'!")
        if not isinstance(sheet_name, str) or len(sheet_name) < 1:
            raise ValueError("Sheet name has to be non-empty string!")
        # Open or create an Excel file and create a sheet inside:
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet(name=sheet_name)
        # Iterate through all columns and rows and add data
        for row_idx in range(self.shape[0]):
            for col_idx in range(self.shape[1]):
                cell: Cell = self.iloc[row_idx, col_idx]
                if cell.value is not None:
                    offset = 0
                    if self.cell_indices.excel_append_labels:
                        offset = 1
                    if cell.cell_type == CellType.value_only:
                        # If the cell is a value only, use method 'write'
                        worksheet.write(row_idx + offset,
                                        col_idx + offset,
                                        cell.value)
                    else:
                        # If the cell is a formula, use method 'write_formula'
                        worksheet.write_formula(row_idx + offset,
                                                col_idx + offset,
                                                cell.parse['excel'],
                                                value=cell.value)
        # Add the labels for rows and columns
        if self.cell_indices.excel_append_labels:
            for col_idx in range(self.shape[1]):
                worksheet.write(0,
                                col_idx + 1,
                                self.cell_indices.columns_nicknames[col_idx])
            for row_idx in range(self.shape[0]):
                worksheet.write(row_idx + 1,
                                0,
                                self.cell_indices.rows_nicknames[row_idx])
        # Store results
        workbook.close()

    def to_dictionary(self,
                      languages: List[str] = None, /, *,
                      by_row: bool = True,
                      languages_pseudonyms: List[str] = None) -> T_out_dict:
        """Export this spreadsheet to the dictionary that can be parsed to the
            JSON format.

        Args:
            languages (List[str]): List of languages that should be exported.
            by_row (bool): If True, rows are the first indices and columns
                are the second in the order. If False it is vice-versa.
            languages_pseudonyms (List[str]): Rename languages to the strings
                inside this list.

        Returns:
            Dict[object, Dict[object, Dict[str, Union[str, float]]]]: The
                Dictionary with keys: 1. column/row, 2. row/column, 3. language
                or language pseudonym or 'value' keyword for values -> value as
                a value or as a cell building string.
        """
        # Assign all languages if languages is None:
        if languages is None:
            languages = self.cell_indices.languages
        # Quick sanity check:
        if (
                languages_pseudonyms is not None
                and len(languages_pseudonyms) != len(languages)
        ):
            raise ValueError("Language pseudonyms does not have the same size "
                             "as the language array!")
        # Language array (use pseudonyms if possible, language otherwise)
        languages_used = languages
        if languages_pseudonyms is not None:
            languages_used = languages_pseudonyms
        # If by column (not by_row)
        # The x-axes represents the columns
        x_range = self.shape[1]
        x = self.cell_indices.columns_nicknames
        x_helptext = self.cell_indices.columns_help_text
        x_start_key = 'columns'
        # The y-axes represents the rows
        y_range = self.shape[0]
        y = self.cell_indices.rows_nicknames
        y_helptext = self.cell_indices.rows_help_text
        y_start_key = 'rows'
        if by_row:
            # The x-axes represents the rows
            x_range = self.shape[0]
            x = self.cell_indices.rows_nicknames
            x_helptext = self.cell_indices.rows_help_text
            x_start_key = 'rows'
            # The y-axes represents the columns
            y_range = self.shape[1]
            y = self.cell_indices.columns_nicknames
            y_helptext = self.cell_indices.columns_help_text
            y_start_key = 'columns'

        # Export the spreadsheet to the dictionary (that can by JSON-ified)
        values = {x_start_key: {}}
        for idx_x in range(x_range):
            y_values = {y_start_key: {}}
            for idx_y in range(y_range):
                # Select the correct cell
                if by_row:
                    cell = self.iloc[idx_x, idx_y]
                else:
                    cell = self.iloc[idx_y, idx_x]
                # Skip if cell value is None:
                if cell.value is None:
                    continue
                # Receive values from cell (either integer or building text)
                parsed_cell = cell.parse
                pseudolang_and_val = {}
                for i, language in enumerate(languages):
                    pseudolang_and_val[languages_used[i]] = \
                        parsed_cell[language]
                # Append the value:
                pseudolang_and_val['value'] = cell.value
                y_values[y_start_key][y[idx_y]] = pseudolang_and_val
                if y_helptext is not None:
                    y_values[y_start_key][y[idx_x]]['help_text'] = \
                        x_helptext[idx_x]
            values[x_start_key][x[idx_x]] = y_values
            if x_helptext is not None:
                values[x_start_key][x[idx_x]]['help_text'] = x_helptext[idx_x]
        return values

    def values_to_string(self):
        export = "["
        for row_idx in range(self.cell_indices.shape[0]):
            export += "["
            for col_idx in range(self.cell_indices.shape[1]):
                export += str(self.iloc[row_idx, col_idx].value)
                if col_idx < self.cell_indices.shape[1] - 1:
                    export += ', '
            export += "]"
            if row_idx < self.cell_indices.shape[0] - 1:
                export += ",\n"
        return export + "]"


# -----------------------------------------------------------------------------
from cell_indices_templates import cell_indices_generators
# Some quick tests
number_of_rows = 5
number_of_columns = 6

indices = CellIndices(
    number_of_rows, number_of_columns,
    {
        "native": cell_indices_generators['native'](number_of_rows, number_of_columns),
    },
    rows_nicknames=['row_a', 'row_ab', 'row_ac', 'row_ad', 'row_ae'],
    columns_nicknames=['col_a', 'col_b', 'col_c', 'col_d', 'col_e', 'col_f'],
    rows_help_text=['H1', 'h2', 'h3', 'h4', 'h5'],
)

sheet = Spreadsheet(indices)
sheet.iloc[0,0] = 7
sheet.iloc[1,0] = 8
sheet.iloc[2,0] = 9
sheet.iloc[3,0] = 10
sheet.iloc[4,0] = 11

sheet.iloc[0,1] = sheet.iloc[0,0] + sheet.iloc[1,0]

print(sheet.values_to_string())
sheet.to_excel("/home/david/Temp/excopu/excel.xlsx")
print(
    sheet.to_dictionary(
        #['native', 'excel'],
        #languages_pseudonyms=['description', 'xlsx'],
        by_row=True,
        )
)

number_of_rows = 1
number_of_columns = 1
indices.expand_size(number_of_rows, number_of_columns,
    {
        "native": cell_indices_generators['native'](number_of_rows, number_of_columns),
    },
    new_rows_nicknames=['row_ex',],
    new_columns_nicknames=['col_x',],
    new_rows_help_text=['Hx',] # 'h2', 'h3', 'h4', 'h5']
                    )
sheet.expand_size(indices)
print(sheet.shape)
print(sheet.values_to_string())

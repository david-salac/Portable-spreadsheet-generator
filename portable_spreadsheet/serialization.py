import abc
from typing import Tuple, List, Dict, Union
from numbers import Number

import xlsxwriter
import numpy

from .cell_type import CellType

# ==== TYPES ====
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


class Serialization(abc.ABC):
    """Provides basic functionality for exporting to required formats.
    """
    @property
    def shape(self) -> Tuple[int, int]:
        """Get the shape as the tuple of number of rows and columns.

        Returns:
            Tuple[int, int]: number of rows, columns
        """
        raise NotImplementedError

    @property
    def cell_indices(self) -> 'CellIndices':
        """Get the cell indices.

        Returns:
            CellIndices: Cell indices of the spreadsheet.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_cell_at(self, row: int, column: int) -> 'Cell':
        """Get the particular cell on the (row, column) position.

        Returns:
            Cell: The call on given position.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_variables(self) -> '_SheetVariables':
        """Return the sheet variables as _SheetVariables object.

        Returns:
            _SheetVariables: Sheet variables.
        """
        raise NotImplementedError

    def to_excel(self,
                 file_path: str,
                 /, *,  # noqa E999
                 sheet_name: str = "Results",
                 spaces_replacement: str = ' ',
                 label_format: dict = {'bold': True}) -> None:
        """Export the values inside Spreadsheet instance to the
            Excel 2010 compatible .xslx file

        Args:
            file_path (str): Path to the target .xlsx file.
            sheet_name (str): The name of the sheet inside the file.
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            label_format (dict): Excel styles for the label rows and columns,
                documentation: https://xlsxwriter.readthedocs.io/format.html
        """
        # Quick sanity check
        if ".xlsx" not in file_path[-5:]:
            raise ValueError("Suffix of the file has to be '.xslx'!")
        if not isinstance(sheet_name, str) or len(sheet_name) < 1:
            raise ValueError("Sheet name has to be non-empty string!")
        # Open or create an Excel file and create a sheet inside:
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet(name=sheet_name)
        # Register all variables:
        for name, value in self._get_variables().variables_dict.items():
            workbook.define_name(name, str(value))
        # Register the style for the labels:
        cell_format = workbook.add_format(label_format)
        # Iterate through all columns and rows and add data
        for row_idx in range(self.shape[0]):
            for col_idx in range(self.shape[1]):
                cell: 'Cell' = self._get_cell_at(row_idx, col_idx)
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
                                self.cell_indices.columns_labels[
                                    col_idx
                                ].replace(' ', spaces_replacement),
                                cell_format)
            for row_idx in range(self.shape[0]):
                worksheet.write(row_idx + 1,
                                0,
                                self.cell_indices.rows_labels[
                                    row_idx
                                ].replace(' ', spaces_replacement),
                                cell_format)
        # Store results
        workbook.close()

    def to_dictionary(self,
                      languages: List[str] = None,
                      /, *,  # noqa E999
                      by_row: bool = True,
                      languages_pseudonyms: List[str] = None,
                      spaces_replacement: str = ' ') -> T_out_dict:
        """Export this spreadsheet to the dictionary that can be parsed to the
            JSON format.

        Args:
            languages (List[str]): List of languages that should be exported.
            by_row (bool): If True, rows are the first indices and columns
                are the second in the order. If False it is vice-versa.
            languages_pseudonyms (List[str]): Rename languages to the strings
                inside this list.
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.

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
        x = [label.replace(' ', spaces_replacement)
             for label in self.cell_indices.columns_labels]
        x_helptext = self.cell_indices.columns_help_text
        x_start_key = 'columns'
        # The y-axes represents the rows
        y_range = self.shape[0]
        y = [label.replace(' ', spaces_replacement)
             for label in self.cell_indices.rows_labels]
        y_helptext = self.cell_indices.rows_help_text
        y_start_key = 'rows'
        if by_row:
            # The x-axes represents the rows
            x_range = self.shape[0]
            x = [label.replace(' ', spaces_replacement)
                 for label in self.cell_indices.rows_labels]
            x_helptext = self.cell_indices.rows_help_text
            x_start_key = 'rows'
            # The y-axes represents the columns
            y_range = self.shape[1]
            y = [label.replace(' ', spaces_replacement)
                 for label in self.cell_indices.columns_labels]
            y_helptext = self.cell_indices.columns_help_text
            y_start_key = 'columns'

        # Export the spreadsheet to the dictionary (that can by JSON-ified)
        values = {x_start_key: {}}
        for idx_x in range(x_range):
            y_values = {y_start_key: {}}
            for idx_y in range(y_range):
                # Select the correct cell
                if by_row:
                    cell = self._get_cell_at(idx_x, idx_y)
                else:
                    cell = self._get_cell_at(idx_y, idx_x)
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
                    y_values[y_start_key][y[idx_y]]['help_text'] = \
                        y_helptext[idx_y]
            values[x_start_key][x[idx_x]] = y_values
            if x_helptext is not None:
                values[x_start_key][x[idx_x]]['help_text'] = x_helptext[idx_x]
        # Add variables
        values['variables'] = self._get_variables().variables_dict
        return values

    def to_string_of_values(self) -> str:
        """Export values inside table to the Python array definition string.

        Returns:
            str: Python list definition string.
        """
        export = "["
        for row_idx in range(self.shape[0]):
            export += "["
            for col_idx in range(self.shape[1]):
                export += str(self._get_cell_at(row_idx, col_idx).value)
                if col_idx < self.shape[1] - 1:
                    export += ', '
            export += "]"
            if row_idx < self.shape[0] - 1:
                export += ",\n"
        return export + "]"

    def to_2d_list(self) -> List[List[object]]:
        """Export values 2 dimensional Python array.

        Returns:
            str: Python array.
        """
        export: list = []
        for row_idx in range(self.shape[0]):
            row: list = []
            for col_idx in range(self.shape[1]):
                row.append(self._get_cell_at(row_idx, col_idx).value)
            export.append(row)
        return export

    def to_csv(self, *,
               spaces_replacement: str = ' ',
               top_right_corner_text: str = "Sheet",
               sep: str = ',',
               line_terminator: str = '\n',
               na_rep: str = '') -> str:
        """Export values to the string in the CSV logic

        Args:
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            top_right_corner_text (str): Text in the top right corner.
            sep (str): Separator of values in a row.
            line_terminator (str): Ending sequence (character) of a row.
            na_rep (str): Replacement for the missing data.

        Returns:
            str: CSV of the values
        """
        export = ""
        for row_idx in range(-1, self.shape[0]):
            if row_idx == -1:
                export += top_right_corner_text + sep
                for col_i in range(self.shape[1]):
                    col = self.cell_indices.columns_labels[col_i]
                    export += col.replace(' ', spaces_replacement)
                    if col_i < self.shape[1] - 1:
                        export += sep
            else:
                export += self.cell_indices.rows_labels[row_idx].replace(
                    ' ', spaces_replacement
                ) + sep
                for col_idx in range(self.shape[1]):
                    value = self._get_cell_at(row_idx, col_idx).value
                    if value is None:
                        value = na_rep
                    export += str(value)
                    if col_idx < self.shape[1] - 1:
                        export += sep
            if row_idx < self.shape[0] - 1:
                export += line_terminator
        return export

    def to_markdown(self, *,
                    spaces_replacement: str = ' ',
                    top_right_corner_text: str = "Sheet",
                    na_rep: str = ''):
        """Export values to the string in the Markdown (MD) file logic

        Args:
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            top_right_corner_text (str): Text in the top right corner.
            na_rep (str): Replacement for the missing data.

        Returns:
            str: Markdown (MD) compatible table of the values
        """
        export = ""
        for row_idx in range(-2, self.shape[0]):
            if row_idx == -2:
                # Add the labels and top right corner text
                export += "| " + top_right_corner_text + " |"
                for col_i in range(self.shape[1]):
                    col = self.cell_indices.columns_labels[col_i]
                    export += "*" + col.replace(' ', spaces_replacement) + "*"
                    if col_i < self.shape[1] - 1:
                        export += " | "
                    elif col_i == self.shape[1] - 1:
                        export += " |\n"

            elif row_idx == -1:
                # Add the separator to start the table body:
                export += "|----|"
                for col_i in range(self.shape[1]):
                    export += "----|"
                    if col_i == self.shape[1] - 1:
                        export += "\n"
            else:
                export += "| *" + \
                          self.cell_indices.rows_labels[row_idx].replace(
                              ' ', spaces_replacement
                          ) + "*" + " | "
                for col_idx in range(self.shape[1]):
                    value = self._get_cell_at(row_idx, col_idx).value
                    if value is None:
                        value = na_rep
                    export += str(value)
                    if col_idx < self.shape[1] - 1:
                        export += " | "
                    elif col_idx == self.shape[1] - 1:
                        export += " |\n"
        return export

    def to_numpy(self) -> numpy.ndarray:
        """Exports the values to the numpy.ndarray.

        Returns:
            numpy.ndarray: 2 dimensions array with values
        """
        results = numpy.zeros(self.shape)
        for row_idx in range(self.shape[0]):
            for col_idx in range(self.shape[1]):
                if (value := self._get_cell_at(row_idx, col_idx).value) is not None:  # noqa E999
                    if isinstance(value, Number):
                        results[row_idx, col_idx] = value
                    else:
                        results[row_idx, col_idx] = numpy.nan
                else:
                    results[row_idx, col_idx] = numpy.nan
        return results

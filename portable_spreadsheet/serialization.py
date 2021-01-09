import abc
import json
from typing import Tuple, List, Dict, Union, Callable, Optional
from types import MappingProxyType
from numbers import Number
import pathlib

import xlsxwriter
import numpy

from .cell import Cell, CellValueError
from .cell_type import CellType
from .cell_indices import CellIndices
from .skipped_label import SkippedLabel
from .serialization_interface import SerializationInterface
from .utils import NumPyEncoder
from .cell_indices_templates import excel_column

# ==== TYPES ====
# Type for the output dictionary with the logic:
# table->data->rows/columns->Row/Col label->columns/rows/help_text->
#   Column/Row label->cell keys (value, description, language alias)->value
T_out_dict = Dict[
    str,  # 'table', 'variables', 'row-labels', 'column-labels'
    Union[
        # Cell values:
        Dict[
            str,  # 'data'
            Dict[
                str,  # 'rows' exclusive or 'columns'
                Dict[
                    str,  # Row/Column key (label)
                    # For values:
                    Dict[
                        str,  # 'columns' xor 'rows' (or 'help_text')
                        Union[
                            Dict[
                                str,  # Column/Row key (label)
                                Dict[
                                    str,  # Cell key ('value', 'description',)
                                    Union[float, int, str]  # Cell values
                                    ]
                                ],
                            str  # For help text
                             ]
                        ]
                    ]
                ]
            ],
        # Variables:
        Dict[
            str,  # 'variables'
            Dict[
                str,  # variable name
                Dict[
                    str,  # 'value' or 'description'
                    Union[float, int, str]  # Variable value
                    ]
                ]
            ],
        # Labels of rows and columns
        Dict[
            str,  # 'row-labels' or 'column-labels'
            str  # Row/Column label
            ],
        # Optional dictionary values appended by user
        Optional[
            dict
            ]
        ],
    ]
# ===============


class Serialization(SerializationInterface, abc.ABC):
    """Provides basic functionality for exporting to required formats.

    Attributes:
        export_offset (Tuple[int, int]): Defines how many rows and
            columns are skiped from the left top corner. First index is
            number of rows, second number of columns.
        warning_logger (Callable[[str], None]): Function that logs the
            warnings.
        export_subset (bool): If true, warning are raised when exporting.
        name (Optional[str]): Name of this object (typically sheet).
    """

    def __init__(self, *,
                 export_offset: Tuple[int, int] = (0, 0),
                 export_subset: bool = False,
                 warning_logger: Optional[Callable[[str], None]] = None,
                 name: Optional[str] = "Results"):
        """Initialise functionality for serialization.

        Args:
            export_offset (Tuple[int, int]): Defines how many rows and
                columns are skipped from the left top corner. First index is
                number of rows, second number of columns.
            export_subset (bool): If true, warning are raised when exporting.
            warning_logger (Optional[Callable[[str], None]]): Function that
                logs the warnings (or None if skipped).
            name (Optional[str]): Name of this object (typically sheet).
        """
        # Export offset of rows, columns
        self.export_offset: Tuple[int, int] = export_offset
        if warning_logger is not None:
            self.warning_logger: Callable[[str], None] = warning_logger
        else:
            # Silent logger
            self.warning_logger: Callable[[str], None] = lambda _mess: _mess
        self.export_subset: bool = export_subset
        self.name: Optional[str] = name

    @property
    def shape(self) -> Tuple[int, int]:
        """Get the shape as the tuple of number of rows and columns.

        Returns:
            Tuple[int, int]: number of rows, columns
        """
        raise NotImplementedError

    @property
    def cell_indices(self) -> CellIndices:
        """Get the cell indices.

        Returns:
            CellIndices: Cell indices of the spreadsheet.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_cell_at(self, row: int, column: int) -> Cell:
        """Get the particular cell on the (row, column) position.

        Returns:
            Cell: The call on given position.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_variables(self):
        """Return the sheet variables as _SheetVariables object.

        Returns:
            _SheetVariables: Sheet variables.
        """
        raise NotImplementedError

    def log_export_subset_warning_if_needed(self):
        """Log the export subset warning if needed.
        """
        if self.export_subset:
            self.warning_logger("Slice is being exported => there is"
                                " a possibility of data losses.")

    def _excel_register_variables(self, workbook):
        """Register variables in Excel spreadsheet.

        Args:
            workbook: Workbook where variables are registered.
        """
        # Just register variables (without writing them to sheet)
        for name, value in self._get_variables().variables_dict.items():
            workbook.define_name(name, str(value['value']))

    @staticmethod
    def _excel_write_variables_to_sheet(workbook: object,
                                        variables_sheet: object,
                                        variables: List[object],
                                        offset_rows: int = 0,
                                        offset_columns: int = 0,
                                        col_label_format: object = None,
                                        header: Optional[Dict[str, str]] = None
                                        ) -> object:
        """Create sheet with variables.

        Args:
            workbook (object): Workbook where variables are registered.
            variables_sheet (object): Sheet where variables are defined.
            variables (List[object]): List of variables set.
            offset_rows (int): How many rows should be skipped.
            offset_columns (int): How many columns should be skipped.
            header (Optional[Dict[str, str]]): Definition of the first line
                with header. If None, header line is skipped.
            col_label_format (object): Define style for header.

        Returns:
            xlsxwriter.worksheet.Worksheet: Worksheet with variables
        """
        row_idx = offset_rows
        if header:
            # Insert header (labels)
            variables_sheet.write(row_idx, offset_columns + 0,
                                  header['name'], col_label_format)
            variables_sheet.write(row_idx, offset_columns + 1,
                                  header['value'], col_label_format)
            variables_sheet.write(row_idx, offset_columns + 2,
                                  header['description'], col_label_format)
            row_idx += 1

        for var_set in variables:
            for var_n, var_v in var_set.variables_dict.items():
                # Format the variable style
                try:
                    style_var = var_set.excel_format[var_n]
                    variable_style = workbook.add_format(style_var)
                except KeyError:
                    variable_style = None
                # Insert variables to the sheet
                variables_sheet.write(row_idx, offset_columns + 0,
                                      var_n)
                variables_sheet.write(row_idx, offset_columns + 1,
                                      var_v['value'], variable_style)
                variables_sheet.write(row_idx, offset_columns + 2,
                                      var_v['description'])
                # Register variable
                workbook.define_name(
                    var_n, '={}!${}${}'.format(
                        variables_sheet.name,
                        excel_column(offset_columns + 1),
                        row_idx + 1
                    )
                )
                row_idx += 1

        return variables_sheet

    def _to_excel(self, *,
                  spaces_replacement: str = ' ',
                  label_row_format: dict = MappingProxyType({'bold': True}),
                  label_column_format: dict = MappingProxyType({'bold': True}),
                  variables_sheet_name: Optional[str] = None,
                  variables_sheet_header: Dict[str, str] = MappingProxyType(
                      {
                          "name": "Name",
                          "value": "Value",
                          "description": "Description"
                      }),
                  values_only: bool = False,
                  skipped_label_replacement: str = '',
                  row_height: List[float] = tuple(),
                  column_width: List[float] = tuple(),
                  top_left_corner_text: str = "",
                  workbook: xlsxwriter.Workbook,
                  worksheet: Optional[object] = None,
                  register_variables: bool = True
                  ) -> object:
        """Export the values inside Spreadsheet instance to the
            Excel 2010 compatible .xslx file

        Args:
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            label_row_format (dict): Excel styles for the label of rows,
                documentation: https://xlsxwriter.readthedocs.io/format.html
            label_column_format (dict): Excel styles for the label of columns,
                documentation: https://xlsxwriter.readthedocs.io/format.html
            variables_sheet_name (Optional[str]): If set, creates the new
                sheet with variables and their description and possibility
                to set them up (directly from the sheet). If None, does not
                write any sheet (also when there is no variable).
            variables_sheet_header (Dict[str, str]): Define the labels (header)
                for the sheet with variables (first row in the sheet).
            values_only (bool): If true, only values (and not formulas) are
                exported.
            skipped_label_replacement (str): Replacement for the SkippedLabel
                instances.
            row_height (List[float]): List of row heights, or empty for the
                default height (or None for default height in the series).
                If row labels are included, there is a label row height on the
                first position in array.
            column_width (List[float]): List of column widths, or empty for the
                default widths (or None for the default width in the series).
                If column labels are included, there is a label column width
                on the first position in array.
            top_left_corner_text (str): Text in the top left corner. Apply
                only when the row and column labels are included.
            workbook (xlsxwriter.Workbook): Handler of the file.
            worksheet (object): Sheet where values should be written.
            register_variables (bool): If false, variable registration is
                skipped.

        Return:
            object: Created worksheet.
        """
        # Log warning if needed
        self.log_export_subset_warning_if_needed()

        # A) Create a sheet inside Excel file:
        if worksheet is None:
            worksheet = workbook.add_worksheet(name=self.name)

        # B) Register the style for the labels:
        col_label_format = workbook.add_format(label_column_format)
        row_label_format = workbook.add_format(label_row_format)

        # C) Register all variables:
        if self._get_variables().empty or not register_variables:
            # If there are no variables, skip this
            pass
        elif variables_sheet_name is None:
            # Just register variables (without writing them to sheet)
            self._excel_register_variables(workbook)
        else:
            # Register variables and create the variable's sheet
            variables_sheet = workbook.add_worksheet(name=variables_sheet_name)

            # Write variable sheet
            self._excel_write_variables_to_sheet(
                workbook, variables_sheet, [self._get_variables()], 0, 0,
                col_label_format, variables_sheet_header
            )

        # D) Iterate through all columns and rows and add data
        for row_idx in range(self.shape[0]):
            for col_idx in range(self.shape[1]):
                cell: Cell = self._get_cell_at(row_idx, col_idx)
                if cell.value is not None:
                    # Offset here is either 0 or 1, indicates if we writes
                    # row/column labels to the first row and column.
                    offset_row = 0
                    offset_col = 0
                    if self.cell_indices.excel_append_row_labels:
                        offset_col = 1
                    if self.cell_indices.excel_append_column_labels:
                        offset_row = 1
                    # Excel format/style for the cell:
                    if len(cell.excel_format) > 0:
                        # Register the format
                        cell_format = workbook.add_format(cell.excel_format)
                    else:
                        cell_format = None
                    # Write actual data
                    if type(cell.value) == CellValueError:
                        worksheet.write_formula(row_idx + offset_row,
                                                col_idx + offset_col,
                                                cell.parse['excel'],
                                                value='#VALUE!',
                                                cell_format=cell_format)
                    elif values_only or (
                            cell.cell_type == CellType.value_only):
                        # If the cell is a value only, use method 'write'
                        worksheet.write(row_idx + offset_row,
                                        col_idx + offset_col,
                                        cell.value,
                                        cell_format)
                    else:
                        # If the cell is a formula, use method 'write_formula'
                        worksheet.write_formula(row_idx + offset_row,
                                                col_idx + offset_col,
                                                cell.parse['excel'],
                                                value=cell.value,
                                                cell_format=cell_format)
        # E) Add the labels for rows and columns
        if self.cell_indices.excel_append_column_labels:
            # Add labels of column
            for col_idx in range(self.shape[1]):
                col_lbl = self.cell_indices.columns_labels[
                                    # Reflect the export offset
                                    col_idx + self.export_offset[1]
                                ].replace(' ', spaces_replacement)
                if isinstance(col_lbl, SkippedLabel):
                    col_lbl = skipped_label_replacement
                worksheet.write(0,
                                col_idx + int(
                                    self.cell_indices.excel_append_row_labels
                                ),
                                col_lbl,
                                col_label_format)
        if self.cell_indices.excel_append_row_labels:
            # Add labels for rows
            for row_idx in range(self.shape[0]):
                # Reflect the export offset
                row_lbl = self.cell_indices.rows_labels[
                    row_idx + self.export_offset[0]
                ].replace(' ', spaces_replacement)
                if isinstance(row_lbl, SkippedLabel):
                    row_lbl = skipped_label_replacement
                worksheet.write(row_idx + int(
                    self.cell_indices.excel_append_column_labels
                ),
                                0,
                                row_lbl,
                                row_label_format)
            if self.cell_indices.excel_append_column_labels:
                # Write the left/top corner text
                worksheet.write(0, 0,
                                top_left_corner_text,
                                row_label_format)

        # Set the row heights:
        for row_position, s_row_height in enumerate(row_height):
            if s_row_height is not None:
                worksheet.set_row(row_position, s_row_height)

        # Set the column widths:
        for col_position, s_col_width in enumerate(column_width):
            if s_col_width is not None:
                worksheet.set_column(col_position, col_position, s_col_width)

        # Return results
        return worksheet, worksheet

    def to_excel(self,
                 file_path: Union[str, pathlib.Path],
                 *,
                 spaces_replacement: str = ' ',
                 label_row_format: dict = {'bold': True},
                 label_column_format: dict = {'bold': True},
                 variables_sheet_name: Optional[str] = None,
                 variables_sheet_header: Dict[str, str] = MappingProxyType(
                     {
                         "name": "Name",
                         "value": "Value",
                         "description": "Description"
                     }),
                 values_only: bool = False,
                 skipped_label_replacement: str = '',
                 row_height: List[float] = [],
                 column_width: List[float] = [],
                 top_left_corner_text: str = ""
                 ) -> None:
        """Export the values inside Spreadsheet instance to the
            Excel 2010 compatible .xslx file

        Args:
            file_path (Union[str, pathlib.Path]): Path to the target Excel
                .xlsx file.
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            label_row_format (dict): Excel styles for the label of rows,
                documentation: https://xlsxwriter.readthedocs.io/format.html
            label_column_format (dict): Excel styles for the label of columns,
                documentation: https://xlsxwriter.readthedocs.io/format.html
            variables_sheet_name (Optional[str]): If set, creates the new
                sheet with variables and their description and possibility
                to set them up (directly from the sheet).
            variables_sheet_header (Dict[str, str]): Define the labels (header)
                for the sheet with variables (first row in the sheet).
            values_only (bool): If true, only values (and not formulas) are
                exported.
            skipped_label_replacement (str): Replacement for the SkippedLabel
                instances.
            row_height (List[float]): List of row heights, or empty for the
                default height (or None for default height in the series).
                If row labels are included, there is a label row height on the
                first position in array.
            column_width (List[float]): List of column widths, or empty for the
                default widths (or None for the default width in the series).
                If column labels are included, there is a label column width
                on the first position in array.
            top_left_corner_text (str): Text in the top left corner. Apply
                only when the row and column labels are included.
        """
        # Quick sanity check
        if ".xlsx" not in pathlib.Path(file_path).suffix:
            raise ValueError("Suffix of the file has to be '.xslx'!")
        if not isinstance(self.name, str) or len(self.name) < 1:
            raise ValueError("Sheet name has to be non-empty string!")

        workbook = xlsxwriter.Workbook(str(file_path))
        # Create a sheet inside Excel file:
        worksheet = workbook.add_worksheet(name=self.name)
        self._to_excel(
            spaces_replacement=spaces_replacement,
            label_row_format=label_row_format,
            label_column_format=label_column_format,
            variables_sheet_name=variables_sheet_name,
            variables_sheet_header=variables_sheet_header,
            values_only=values_only,
            skipped_label_replacement=skipped_label_replacement,
            row_height=row_height,
            column_width=column_width,
            top_left_corner_text=top_left_corner_text,
            workbook=workbook,
            worksheet=worksheet
        )
        workbook.close()

    def to_dictionary(self,
                      languages: List[str] = None,
                      use_language_for_description: Optional[str] = None,
                      *,
                      by_row: bool = True,
                      languages_pseudonyms: List[str] = None,
                      spaces_replacement: str = ' ',
                      skip_nan_cell: bool = False,
                      nan_replacement: object = None,
                      error_replacement: object = None,
                      append_dict: dict = MappingProxyType({}),
                      generate_schema: bool = False
                      ) -> T_out_dict:
        """Export this spreadsheet to the dictionary.

        Args:
            languages (List[str]): List of languages that should be exported.
                If it has value None, all the languages are exported.
            use_language_for_description (Optional[str]): If set-up (using
                the language name), description field is set to be either
                the description value (if defined) or the value of this
                language.
            by_row (bool): If True, rows are the first indices and columns
                are the second in the order. If False it is vice-versa.
            languages_pseudonyms (List[str]): Rename languages to the strings
                inside this list.
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            skip_nan_cell (bool): If True, None (NaN) values are skipped.
            nan_replacement (object): Replacement for the None (NaN) value.
            error_replacement (object): Replacement for the error value.
            append_dict (dict): Append this dictionary to output.
            generate_schema (bool): If true, returns the JSON schema.

        Returns:
            dict:
                Output dictionary with the logic:
                table->data->rows/columns->Row/Col label->
                columns/rows/help_text->Column/Row label->
                cell keys (value, description, language alias)->value
        """
        if generate_schema:
            return self.generate_json_schema()

        # Log warning if needed
        self.log_export_subset_warning_if_needed()

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

        # A) The x-axes represents the columns
        x_range = self.shape[1]
        x = [label.replace(' ', spaces_replacement)
             for label in self.cell_indices.columns_labels[
                          # Reflects the column offset for export
                          self.export_offset[1]:self.shape[1]
                          ]
             ]
        if (x_helptext := self.cell_indices.columns_help_text) is not None:  # noqa E203
            # Reflects the column offset for export
            x_helptext = x_helptext[self.export_offset[1]:self.shape[1]]
        x_start_key = 'columns'
        # The y-axes represents the rows
        y_range = self.shape[0]
        y = [label.replace(' ', spaces_replacement)
             for label in self.cell_indices.rows_labels[
                          # Reflects the row offset for export
                          self.export_offset[0]:self.shape[0]
                          ]
             ]
        if (y_helptext := self.cell_indices.rows_help_text) is not None:  # noqa E203
            # Reflects the row offset for export
            y_helptext = y_helptext[self.export_offset[0]:self.shape[0]]
        y_start_key = 'rows'

        # B) The x-axes represents the rows:
        if by_row:
            x_range = self.shape[0]
            x = [label.replace(' ', spaces_replacement)
                 for label in self.cell_indices.rows_labels[
                          # Reflects the row offset for export
                          self.export_offset[0]:self.shape[0]
                          ]
                 ]
            if (x_helptext := self.cell_indices.rows_help_text) is not None:  # noqa E203
                # Reflects the row offset for export
                x_helptext = x_helptext[self.export_offset[0]:self.shape[0]]
            x_start_key = 'rows'
            # The y-axes represents the columns
            y_range = self.shape[1]
            y = [label.replace(' ', spaces_replacement)
                 for label in self.cell_indices.columns_labels[
                          # Reflects the column offset for export
                          self.export_offset[1]:self.shape[1]
                          ]]
            if (y_helptext := self.cell_indices.columns_help_text) is not None:  # noqa E203
                # Reflects the column offset for export
                y_helptext = y_helptext[self.export_offset[1]:self.shape[1]]
            y_start_key = 'columns'

        # Export the spreadsheet to the dictionary (that can by JSON-ified)
        values = {x_start_key: {}}
        for idx_x in range(x_range):
            if isinstance(x[idx_x], SkippedLabel):
                # Skip labels that are intended to be skipped
                continue
            y_values = {y_start_key: {}}
            for idx_y in range(y_range):
                if isinstance(y[idx_y], SkippedLabel):
                    # Skip labels that are intended to be skipped
                    continue
                # Select the correct cell
                if by_row:
                    cell = self._get_cell_at(idx_x, idx_y)
                else:
                    cell = self._get_cell_at(idx_y, idx_x)
                # Skip if cell value is None if required:
                cell_value = cell.value
                if cell_value is None and skip_nan_cell:
                    continue
                # Replace the NaN value as required
                if cell_value is None:
                    cell_value = nan_replacement
                elif type(cell_value) == CellValueError:
                    cell_value = error_replacement
                # Receive values from cell (either integer or building text)
                parsed_cell = cell.parse
                # Following dict is the dict that is exported as a cell
                pseudolang_and_val = {}
                cell_description: str = cell.description
                if cell_description is None:
                    # Replace cell description to NaN replacement
                    cell_description = nan_replacement
                    # If the cell description should be equal to some language
                    if descr_lang := use_language_for_description:  # noqa
                        cell_description = parsed_cell[descr_lang]
                # If it is an empty string, use None value instead
                if cell_description == "":
                    cell_description = nan_replacement
                # Add description in all languages wanted (by aliases)
                for i, language in enumerate(languages):
                    pseudolang_and_val[languages_used[i]] = \
                        parsed_cell[language]
                # Append the value:
                pseudolang_and_val['value'] = cell_value
                pseudolang_and_val['description'] = cell_description
                y_values[y_start_key][y[idx_y]] = pseudolang_and_val

            values[x_start_key][x[idx_x]] = y_values

        # Create data parent
        data = {'data': values}

        # Add variables
        data['variables'] = self._get_variables().variables_dict
        # Add a row and column labels as arrays
        if not by_row:
            x, y = y, x

        # Add column/row metadata

        # Add row description (and labels)
        data['rows'] = []
        for idx, x_label in enumerate(x):
            if isinstance(x_label, SkippedLabel):
                # Skip labels that are intended to be skipped
                continue
            metadata: dict = {"name": x_label}
            if x_helptext is not None:
                # Add the help text (description) for the row
                if (ht := x_helptext[idx]) is None or len(  # noqa
                        x_helptext[idx]) == 0:
                    # If it is not set or is empty string, use NaN value
                    ht = nan_replacement
                metadata['description'] = ht
            data['rows'].append(metadata)

        # Add column description (and labels)
        data['columns'] = []
        for idx, y_label in enumerate(y):
            if isinstance(y_label, SkippedLabel):
                # Skip labels that are intended to be skipped
                continue
            metadata = {"name": y_label}
            if y_helptext is not None:
                # Add the help text (description) for the column
                if (ht := y_helptext[idx]) is None or len(  # noqa
                        y_helptext[idx]) == 0:
                    # If it is not set or is empty string, use NaN value
                    ht = nan_replacement
                metadata['description'] = ht
            data['columns'].append(metadata)
        # Create table parent
        table = {'table': data}

        # Append dictionary:
        for a_key, a_val in append_dict.items():
            table[a_key] = a_val

        return table

    def to_json(self,
                languages: List[str] = None,
                use_language_for_description: Optional[str] = None,
                *,
                by_row: bool = True,
                languages_pseudonyms: List[str] = None,
                spaces_replacement: str = ' ',
                skip_nan_cell: bool = False,
                nan_replacement: object = None,
                error_replacement: object = None,
                append_dict: dict = MappingProxyType({}),
                generate_schema: bool = False) -> str:
        """Dumps the exported dictionary to the JSON object.

        Args:
            languages (List[str]): List of languages that should be exported.
                If it has value None, all the languages are exported.
            use_language_for_description (Optional[str]): If set-up (using
                the language name), description field is set to be either
                the description value (if defined) or the value of this
                language.
            by_row (bool): If True, rows are the first indices and columns
                are the second in the order. If False it is vice-versa.
            languages_pseudonyms (List[str]): Rename languages to the strings
                inside this list.
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            skip_nan_cell (bool): If True, None (NaN) values are skipped.
            nan_replacement (object): Replacement for the None (NaN) value.
            error_replacement (object): Replacement for the error value.
            append_dict (dict): Append this dictionary to output.
            generate_schema (bool): If true, returns the JSON schema.

        Returns:
            dict:
                Output dictionary with the logic:
                table->data->rows/columns->Row/Col label->
                columns/rows/help_text->Column/Row label->
                cell keys (value, description, language alias)->value
        """
        # Return correctly encoded JSON
        return json.dumps(
            self.to_dictionary(languages, use_language_for_description,
                               by_row=by_row,
                               languages_pseudonyms=languages_pseudonyms,
                               spaces_replacement=spaces_replacement,
                               skip_nan_cell=skip_nan_cell,
                               nan_replacement=nan_replacement,
                               error_replacement=error_replacement,
                               append_dict=append_dict,
                               generate_schema=generate_schema),
            cls=NumPyEncoder
        )

    @staticmethod
    def generate_json_schema() -> dict:
        """Generate JSON schema.

        Returns:
            dict: JSON schema for the Portable Spreadsheet JSON sheet output.
        """
        false = False
        schema = {
            "$id": "http://portable-spreadsheet.com/spreadsheet.v3.schema.json",  # noqa
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Portable Spreadsheet JSON output schema",
            "description": "JSON schema of the Portable Spreadsheet output",

            "type": "object",
            "required": ["table"],

            "properties": {
                "table": {
                    "type": "object",
                    "required": ["variables",
                                 "rows",
                                 "columns",
                                 "data"],  # noqa
                    "properties": {
                        "rows": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "number"},
                                            {"type": "null"}
                                        ]
                                    },
                                    "description": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "number"},
                                            {"type": "null"}
                                        ]
                                    },
                                },
                                "additionalProperties": false,
                                "required": ['name']
                            },
                            "additionalProperties": false
                        },
                        "columns": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "number"},
                                            {"type": "null"}
                                        ]
                                    },
                                    "description": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "number"},
                                            {"type": "null"}
                                        ]
                                    },
                                },
                                "additionalProperties": false,
                                "required": ['name']
                            },
                            "additionalProperties": false
                        },
                        "variables": {
                            "minProperties": 0,
                            "type": "object",
                            "propertyNames": {
                                "type": "string"
                            },
                            "patternProperties": {
                                "^.*$": {
                                    "type": "object",
                                    "properties": {
                                        "value": {
                                            "anyOf": [
                                                {"type": "string"},
                                                {"type": "number"},
                                                {"type": "null"}
                                            ]
                                        },
                                        "description": {
                                            "anyOf": [
                                                {"type": "string"},
                                                {"type": "number"},
                                                {"type": "null"}
                                            ]
                                        }
                                    },
                                    "required": ["value", "description"],
                                    "additionalProperties": false
                                }
                            },
                            "additionalProperties": false
                        },
                        "data": {
                            "type": "object",
                            "minProperties": 1,
                            "maxProperties": 2,
                            "additionalProperties": false,
                            "patternProperties": {
                                r"rows|columns": {
                                    "type": "object",
                                    "minProperties": 0,
                                    "propertyNames": {
                                        "type": "string"
                                    },
                                    "patternProperties": {
                                        "^.*$": {
                                            "type": "object",
                                            "patternProperties": {
                                                r"rows|columns": {
                                                    "type": "object",
                                                    "minProperties": 0,
                                                    "propertyNames": {
                                                        "type": "string"
                                                    },
                                                    "patternProperties": {
                                                        "^.*$": {
                                                            "type": "object",
                                                            "minProperties": 2,
                                                            "propertyNames": {
                                                                "type": "string" # noqa
                                                            },
                                                            "patternProperties": {  # noqa
                                                                "value": {
                                                                    "anyOf": [
                                                                        {"type": "string"},  # noqa
                                                                        {"type": "number"},  # noqa
                                                                        {"type": "null"}  # noqa
                                                                    ]
                                                                },
                                                                "description": {  # noqa
                                                                    "anyOf": [
                                                                        {"type": "string"},  # noqa
                                                                        {"type": "number"},  # noqa
                                                                        {"type": "null"}  # noqa
                                                                    ]
                                                                },
                                                                "^.*$": {
                                                                    "anyOf": [
                                                                        {"type": "string"},  # noqa
                                                                        {"type": "number"},  # noqa
                                                                        {"type": "null"}  # noqa
                                                                    ]
                                                                },
                                                            },
                                                            "required": ['value', 'description'],  # noqa
                                                            "additionalProperties": false  # noqa
                                                        }
                                                    }
                                                }
                                            },
                                            "minProperties": 1,
                                            "maxProperties": 2,
                                            "additionalProperties": false
                                        }
                                    },
                                    "additionalProperties": false
                                }
                            }
                        }
                    },
                    "additionalProperties": false
                }
            },
            "additionalProperties": {
                "type": "object"
            }
        }

        return schema

    def to_string_of_values(self) -> str:
        """Export values inside table to the Python array definition string.
            (Mainly helpful for debugging purposes)

        Returns:
            str: Python list definition string.
        """
        # Log warning if needed
        self.log_export_subset_warning_if_needed()

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

    def to_list(self, *,
                language: Optional[str] = None,
                skip_labels: bool = False,
                na_rep: Optional[object] = None,
                spaces_replacement: str = ' ',
                skipped_label_replacement: str = '') -> List[List[object]]:
        """Export values to two dimensional Python array.

        Args:
            language (Optional[str]): If set-up, export the word in this
                language in each cell instead of values.
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            na_rep (str): Replacement for the missing data (cells with value
                equals to None).
            skip_labels (bool): If true, first row and column with labels is
                skipped
            skipped_label_replacement (str): Replacement for the SkippedLabel
                instances.

        Returns:
            List[List[object]]: Python array.
        """
        # Log warning if needed
        self.log_export_subset_warning_if_needed()

        export: list = []
        for row_idx in range(-1, self.shape[0]):
            row: list = []
            if row_idx == -1:
                if skip_labels:
                    continue
                row.append(self.name)
                # Insert labels of columns:
                for col_i in range(self.shape[1]):
                    col_lbl = self.cell_indices.columns_labels[
                        col_i + self.export_offset[1]
                    ].replace(' ', spaces_replacement)
                    if isinstance(col_lbl, SkippedLabel):
                        col_lbl = skipped_label_replacement
                    row.append(col_lbl)
            else:
                if not skip_labels:
                    # Insert labels of rows
                    row_lbl = self.cell_indices.rows_labels[
                                  row_idx + self.export_offset[0]
                              ].replace(' ', spaces_replacement)
                    if isinstance(row_lbl, SkippedLabel):
                        row_lbl = skipped_label_replacement
                    row.append(row_lbl)
                for col_idx in range(self.shape[1]):
                    # Append actual values:
                    cell_at_position = self._get_cell_at(row_idx, col_idx)

                    if language is not None:
                        # Get the word of cell on current position
                        value_to_write = cell_at_position.parse[language]
                    else:
                        # Get the value of cell on current position
                        value_to_write = cell_at_position.value
                    if value_to_write is None:
                        # Replacement for None
                        value_to_write = na_rep
                    row.append(value_to_write)

            export.append(row)
        return export

    def to_csv(self, *,
               language: Optional[str] = None,
               skip_labels: bool = False,
               na_rep: Optional[object] = '',
               spaces_replacement: str = ' ',

               sep: str = ',',
               line_terminator: str = '\n',
               skipped_label_replacement: str = ''
               ) -> str:
        """Export values to the string in the CSV logic

        Args:
            language (Optional[str]): If set-up, export the word in this
                language in each cell instead of values.
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            sep (str): Separator of values in a row.
            line_terminator (str): Ending sequence (character) of a row.
            na_rep (str): Replacement for the missing data.
            skip_labels (bool): If true, first row and column with labels is
                skipped
            skipped_label_replacement (str): Replacement for the SkippedLabel
                instances.

        Returns:
            str: CSV of the values
        """
        sheet_as_array = self.to_list(
            na_rep=na_rep,
            skip_labels=skip_labels,
            spaces_replacement=spaces_replacement,
            language=language,
            skipped_label_replacement=skipped_label_replacement
        )
        export = ""
        for row_idx in range(len(sheet_as_array)):
            for col_idx in range(len(sheet_as_array[row_idx])):
                export += str(sheet_as_array[row_idx][col_idx])
                if col_idx < (len(sheet_as_array[row_idx]) - 1):
                    export += sep
            if row_idx < (len(sheet_as_array) - 1):
                export += line_terminator
        return export

    def to_markdown(self, *,
                    language: Optional[str] = None,
                    skip_labels: bool = False,
                    na_rep: Optional[object] = '',
                    spaces_replacement: str = ' ',
                    skipped_label_replacement: str = ''
                    ):
        """Export values to the string in the Markdown (MD) file logic

        Args:
            language (Optional[str]): If set-up, export the word in this
                language in each cell instead of values.
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            na_rep (str): Replacement for the missing data.
            skip_labels (bool): If true, first row and column with labels is
                skipped
            skipped_label_replacement (str): Replacement for the SkippedLabel
                instances.

        Returns:
            str: Markdown (MD) compatible table of the values
        """
        sheet_as_array = self.to_list(
            na_rep=na_rep,
            skip_labels=skip_labels,
            spaces_replacement=spaces_replacement,
            language=language,
            skipped_label_replacement=skipped_label_replacement
        )
        export = ""
        for row_idx in range(len(sheet_as_array)):
            # Add values:
            export += "| "
            for col_idx in range(len(sheet_as_array[row_idx])):
                if (row_idx == 0 or col_idx == 0) and not skip_labels:
                    export += '*'
                export += str(sheet_as_array[row_idx][col_idx])
                if (row_idx == 0 or col_idx == 0) and not skip_labels:
                    export += '*'
                if col_idx < (len(sheet_as_array[row_idx]) - 1):
                    export += " | "
                else:
                    export += " |"
            export += "\n"
            # Add |---| sequence after the first line
            if row_idx == 0 and not skip_labels:
                for col_idx in range(len(sheet_as_array[row_idx])):
                    export += "|----"
                    if col_idx == (len(sheet_as_array[row_idx]) - 1):
                        export += '|'
                export += "\n"
        # Add first two lines if labels are skipped
        if skip_labels:
            # Add empty || separators for missing labels
            first_line = "|"
            for col_idx in range(len(sheet_as_array[0])):
                first_line += "|"
            first_line += "|\n"
            # Add |---| sequence after the first line
            for col_idx in range(len(sheet_as_array[0])):
                first_line += "|----"
                if col_idx == (len(sheet_as_array[0]) - 1):
                    first_line += '|'
            export = first_line + "\n" + export

        return export

    def to_numpy(self) -> numpy.ndarray:
        """Exports the values to the numpy.ndarray.

        Returns:
            numpy.ndarray: 2 dimensions array with values
        """
        # Log warning if needed
        self.log_export_subset_warning_if_needed()

        results = numpy.zeros(self.shape)
        # Variable for indicating that logging is needed (for logging that
        # replacement of some value for NaN is done):
        contains_nonumeric_values = False
        for row_idx in range(self.shape[0]):
            for col_idx in range(self.shape[1]):
                if (value := self._get_cell_at(row_idx, col_idx).value) is not None:  # noqa E999
                    if isinstance(value, Number):
                        results[row_idx, col_idx] = value
                    else:
                        results[row_idx, col_idx] = numpy.nan
                        # For logging that replacement is done
                        contains_nonumeric_values = True
                else:
                    results[row_idx, col_idx] = numpy.nan
        # Log warning if needed
        if contains_nonumeric_values:
            self.warning_logger(
                "Some values in the sheet are not numbers, the "
                "nan value is set instead."
            )
        return results

    def to_html_table(self, *,
                      spaces_replacement: str = ' ',
                      na_rep: str = '',
                      language_for_description: str = None,
                      skip_labels: bool = False,
                      skipped_label_replacement: str = '') -> str:
        """Export values to the string in the HTML table logic

        Args:
            spaces_replacement (str): All the spaces in the rows and columns
                descriptions (labels) are replaced with this string.
            na_rep (str): Replacement for the missing data.
            language_for_description (str): If not None, the description
                of each computational cell is inserted as word of this
                language (if the property description is not set).
            skip_labels (bool): If true, first row and column with labels is
                skipped
            skipped_label_replacement (str): Replacement for the SkippedLabel
                instances.

        Returns:
            str: HTML table definition
        """
        # Log warning if needed
        self.log_export_subset_warning_if_needed()

        export = "<table>"
        for row_idx in range(-1, self.shape[0]):
            if skip_labels and row_idx == -1:
                continue
            export += "<tr>"
            if row_idx == -1:
                export += "<th>"
                export += self.name
                export += "</th>"
                # Insert labels of columns:
                for col_i in range(self.shape[1]):
                    export += "<th>"
                    col = self.cell_indices.columns_labels[
                        col_i + self.export_offset[1]
                        ].replace(' ', spaces_replacement)
                    if isinstance(col, SkippedLabel):
                        col = skipped_label_replacement
                    if (help_text :=  # noqa 203
                            self.cell_indices.columns_help_text) is not None:
                        title_attr = ' title="{}"'.format(
                            help_text[col_i + self.export_offset[1]]
                        )
                    else:
                        title_attr = ""
                    export += f'<a href="javascript:;" {title_attr}>'
                    export += col
                    export += "</a>"
                    export += "</th>"
            else:
                if not skip_labels:
                    # Insert labels of rows
                    if (help_text :=  # noqa: 203
                            self.cell_indices.rows_help_text) is not None:
                        title_attr = ' title="{}"'.format(
                            help_text[row_idx + self.export_offset[1]]
                        )
                    else:
                        title_attr = ""
                    export += "<td>"
                    export += f'<a href="javascript:;" {title_attr}>'
                    row_lbl = self.cell_indices.rows_labels[
                                  row_idx + self.export_offset[0]
                                  ].replace(' ', spaces_replacement)
                    if isinstance(row_lbl, SkippedLabel):
                        row_lbl = skipped_label_replacement
                    export += row_lbl
                    export += "</a>"
                    export += "</td>"

                # Insert actual values in the spreadsheet
                for col_idx in range(self.shape[1]):
                    title_attr = ""
                    cell_at_pos = self._get_cell_at(row_idx, col_idx)
                    if (description := # noqa 203
                            cell_at_pos.description) is not None:
                        title_attr = ' title="{}"'.format(description)
                    elif language_for_description is not None:
                        if cell_at_pos.cell_type == CellType.computational:
                            title = cell_at_pos.constructing_words.words[
                                language_for_description
                            ]
                            title_attr = f' title="{title}"'
                    export += "<td>"
                    export += f'<a href="javascript:;" {title_attr}>'
                    value = cell_at_pos.value
                    if value is None:
                        value = na_rep
                    export += str(value)
                    export += "</a>"
                    export += "</td>"
            export += '</tr>'
        export += '</table>'
        return export

    @property
    def columns(self) -> List[str]:
        """Return the labels of columns.

        Returns:
            List[str]: List of column labels
        """
        return self.cell_indices.columns_labels_str[self.export_offset[1]:(
                self.export_offset[1] + self.shape[1])
               ]

    @property
    def index(self) -> List[str]:
        """Return the labels of rows.

        Returns:
            List[str]: List of row labels.
        """
        return self.cell_indices.rows_labels_str[self.export_offset[0]:(
                self.export_offset[0] + self.shape[0])
               ]

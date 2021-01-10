from types import MappingProxyType
from typing import List, Optional, Union, Tuple, Iterable
from dataclasses import dataclass
import json
import pathlib

import xlsxwriter

from .serialization_interface import SerializationInterface
from .serialization import Serialization
from .sheet import Sheet
from .utils import ClassVarsToDict, NumPyEncoder


@dataclass()
class ExcelParameters(ClassVarsToDict):
    spaces_replacement: str = ' '
    label_row_format: dict = MappingProxyType({'bold': True})
    label_column_format: dict = MappingProxyType({'bold': True})
    values_only: bool = False
    skipped_label_replacement: str = ''
    row_height: Tuple[float] = tuple([])
    column_width: Tuple[float] = tuple([])
    top_left_corner_text: str = ""


@dataclass()
class DictionaryParameters(ClassVarsToDict):
    languages: List[str] = None
    use_language_for_description: Optional[str] = None
    by_row: bool = True
    languages_pseudonyms: List[str] = None
    spaces_replacement: str = ' '
    skip_nan_cell: bool = False
    nan_replacement: object = None
    error_replacement: object = None
    append_dict: dict = MappingProxyType({})
    generate_schema: bool = False


@dataclass()
class ListParameters(ClassVarsToDict):
    language: Optional[str] = None
    skip_labels: bool = False
    na_rep: Optional[object] = None
    spaces_replacement: str = ' '
    skipped_label_replacement: str = ''


class WorkBook(SerializationInterface):
    """Container for sheets that allows export multiple sheets to one output.

    Attributes:
        sheets(Iterable[Sheet]): Sheets the are the subject of export.
        variable_sheet_offset (Tuple[int, int]): Offset of rows and columns
            of variable sheet.
        variable_sheet_name (Optional[str]): Name of the variable sheet.
    """

    def __init__(self, *sheets: Iterable[Sheet]):
        """Initialize instance.

        Args:
            sheets(Iterable[Sheet]): Sheets the are the subject of export.
        """
        self.sheets: List[Serialization] = list(sheets)
        self.variable_sheet_offset: Tuple[int, int] = None
        self.variable_sheet_name: Optional[str] = None

    def create_variable_sheet(self,
                              *,
                              nr_rows_prefix: int = 0,
                              nr_rows_suffix: int = 0,
                              nr_columns_prefix: int = 0,
                              nr_columns_suffix: int = 0,
                              sheet_name: str = "config",
                              position: int = 0
                              ) -> Sheet:
        """Allows to customize the way how the variable definition tab
        in Excel looks like.

        Args:
            nr_rows_prefix (int): defines the number of rows that are prefix
                for variables definition segment.
            nr_rows_suffix (int): defines the number of rows that are suffix
                for variables definition segment.
            nr_columns_prefix (int): defines the number of columns that are
                prefix for variables definition segment.
            nr_columns_suffix (int): defines the number of columns that are
                suffix for variables definition segment.
            sheet_name (str): Name of the sheet for variables.
            position (int): Relative position in the workbook (indexed from 0).

        Returns:
            Sheet: Sheet for variables definition.
        """
        # Get the number of variables in all sheets
        number_of_variables: int = sum([len(sht.var) for sht in self.sheets])
        if number_of_variables == 0:
            raise ValueError("there has to be at least 1 variable")
        if self.variable_sheet_offset is not None:
            # Check if singleton
            raise ValueError("there can be just one sheet for variables")

        self.variable_sheet_offset = (nr_rows_prefix, nr_columns_prefix)

        number_of_rows = number_of_variables + nr_rows_prefix + nr_rows_suffix
        # Three for var_name, var_value, var_description
        number_of_columns = 3 + nr_columns_prefix + nr_columns_suffix

        # Create a sheet for variables
        var_sheet = Sheet.create_new_sheet(
            number_of_rows, number_of_columns,
            name=sheet_name,
            excel_append_column_labels=False,
            excel_append_row_labels=False
        )

        # Insert sheet to workbook
        self.sheets = self.sheets[:position] + \
            [var_sheet] + self.sheets[position:]
        self.variable_sheet_name = sheet_name

        # Return sheet
        return var_sheet

    def to_excel(self,
                 file_path: Union[str, pathlib.Path],
                 /, *,  # noqa: E225
                 export_parameters: Tuple[ExcelParameters]
                 ) -> None:
        """Export to Excel file.

        Args:
            file_path (Union[str, pathlib.Path]): Path to file
            export_parameters (Tuple[ExcelParameters]): Parameters for
                exporting each sheet.
        """
        # Quick sanity check
        if ".xlsx" not in pathlib.Path(file_path).suffix:
            raise ValueError("Suffix of the file has to be '.xslx'!")

        workbook = xlsxwriter.Workbook(str(file_path))
        # Pre-prepare sheets in correct order and identify variable sheet
        worksheets = []
        variable_sheet_idx = -1
        for idx, sheet in enumerate(self.sheets):
            worksheets.append(workbook.add_worksheet(sheet.name))
            if sheet.name == self.variable_sheet_name:
                if variable_sheet_idx > -1:
                    raise RuntimeError("There can be just one variable sheet!")
                variable_sheet_idx = idx
        if variable_sheet_idx >= 0:
            variable_sheet = self.sheets[variable_sheet_idx]
        else:
            variable_sheet = None

        # Deal with variables:
        if variable_sheet:
            variable_worksheet = worksheets[variable_sheet_idx]
            variables = [sheet._get_variables() for sheet in self.sheets]
            Sheet._excel_write_variables_to_sheet(
                workbook, variable_worksheet, variables,
                *self.variable_sheet_offset
            )
        else:
            # Just register variables
            for sheet in self.sheets:
                sheet._excel_register_variables(workbook)

        # Write all sheets
        for idx, sheet in enumerate(self.sheets):
            sheet._to_excel(
                **dict(export_parameters[idx]),
                workbook=workbook,
                worksheet=worksheets[idx],
                register_variables=False
            )

        # Write to file and close
        workbook.close()

    def to_dictionary(self,
                      *,
                      export_parameters: Tuple[DictionaryParameters]
                      ) -> dict:
        """Export sheets as JSON.

        Args:
            export_parameters (Tuple[ListParameters]): Parameters for exporting
                sheets as dict.
        """
        res: dict = {}
        for idx, sheet in enumerate(self.sheets):
            res[sheet.name] = sheet.to_dictionary(
                **dict(export_parameters[idx])
            )
        return res

    def to_json(self,
                *,
                export_parameters: Tuple[DictionaryParameters]) -> str:
        """Export sheets as JSON.

        Args:
            export_parameters (Tuple[ListParameters]): Parameters for exporting
                sheets as dict.
        """
        return json.dumps(
            self.to_dictionary(export_parameters=export_parameters),
            cls=NumPyEncoder
        )

    @staticmethod
    def generate_json_schema() -> dict:
        """Generate JSON schema.

        Returns:
            dict: JSON schema for the JSON workbook output.
        """
        schema = Sheet.generate_json_schema()
        schema['required'] = ['tables']
        schema['properties'] = {
            "tables": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        **schema['properties']
                    }
                }
            }
        }
        return schema

    def to_string_of_values(self) -> str:
        """Export sheets' values to 3D list and convert it to string.

        Returns:
            str: Representation of the sheets as a string.
        """
        outputs = "["
        for sheet in self.sheets:
            outputs += sheet.to_string_of_values()
            outputs += ","
        outputs += "]"
        return outputs

    def to_list(self,
                *,
                export_parameters: Tuple[ListParameters]) -> list:
        """Export sheets to 3D list.

        Args:
            export_parameters (Tuple[ListParameters]): Parameters for exporting
                each sheet.
        """
        res = []
        for idx, sheet in enumerate(self.sheets):
            res.append(sheet.to_list(**dict(export_parameters[idx])))
        return res

    def __getitem__(self, sheet_name: str):
        """Returns the concrete sheet in the work book.

        Args:
            sheet_name (str): The concrete sheet name.
        """
        for sheet in self.sheets:
            if sheet.name == sheet_name:
                return sheet
        raise IndexError(f"there is no sheet named {sheet_name}")

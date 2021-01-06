from types import MappingProxyType
from typing import List, Optional, Union, Tuple, Iterable
from dataclasses import dataclass
import json
import pathlib

import xlsxwriter
import numpy as np

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
    """

    def __init__(self, *sheets: Iterable[Sheet]):
        """Initialize instance.

        Args:
            sheets(Iterable[Sheet]): Sheets the are the subject of export.
        """
        self.sheets: List[Serialization] = list(sheets)

    def excel_create_variable_tab(self,
                                  *,
                                  nr_rows_prefix: int = 0,
                                  nr_rows_suffix: int = 0,
                                  nr_columns_prefix: int = 0,
                                  nr_columns_suffix: int = 0,
                                  include_header_line: bool = True
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
            include_header_line (bool): if True, the first (default) line
                defining variable header is exported as well.
        """
        # Get the number of variables in all sheets
        number_of_variables: int = sum([len(sht.var) for sht in self.sheets])
        return Sheet.create_new_sheet(
            excel_append_column_labels=False
        )

    def to_excel(self,
                 file_path: Union[str, pathlib.Path],
                 /, *,  # noqa: E225, E999
                 export_parameters: Tuple[ExcelParameters]
                 ) -> None:
        """Export to Excel file.

        Args:
            file_path (Union[str, pathlib.Path]): Path to file
            export_parameters (Tuple[ExcelParameters]): Parameters for
                exporting each sheet.
        """
        # Quick sanity check
        if ".xlsx" not in file_path[-5:]:
            raise ValueError("Suffix of the file has to be '.xslx'!")

        workbook = xlsxwriter.Workbook(str(file_path))
        for idx, sheet in enumerate(self.sheets):
            sheet._to_excel(
                **dict(export_parameters[idx]),
                workbook=workbook
            )
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
                        schema['properties']
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

    def __getattr__(self, sheet_name: str):
        """Returns the concrete sheet in the work book.

        Args:
            sheet_name (str): The concrete sheet name.
        """
        for sheet in self.sheets:
            if sheet.name == sheet_name:
                return sheet
        raise IndexError(f"there is no sheet named {sheet_name}")

from types import MappingProxyType
from typing import List, Optional, Dict, Tuple, Iterable
from dataclasses import dataclass
import json

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
    """

    def __init__(self, *sheets: Iterable[Sheet]):
        self.sheets: List[Serialization] = list(sheets)

    def to_excel(self,
                 file_path: str,
                 /, *,  # noqa: E225, E999
                 export_parameters: Tuple[ExcelParameters]
                 ) -> None:
        # Quick sanity check
        if ".xlsx" not in file_path[-5:]:
            raise ValueError("Suffix of the file has to be '.xslx'!")

        workbook = xlsxwriter.Workbook(file_path)
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
        res: dict = {}
        for idx, sheet in enumerate(self.sheets):
            res[sheet.name] = sheet.to_dictionary(
                **dict(export_parameters[idx])
            )
        return res

    def to_json(self,
                *,
                export_parameters: Tuple[DictionaryParameters]) -> str:
        return json.dumps(
            self.to_dictionary(export_parameters=export_parameters),
            cls=NumPyEncoder
        )

    @staticmethod
    def generate_json_schema() -> dict:
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

    def to_string_of_values(self):
        outputs = "["
        for sheet in self.sheets:
            outputs += sheet.to_string_of_values()
            outputs += ","
        outputs += "]"
        return outputs

    def to_list(self,
                *,
                export_parameters: Tuple[ListParameters]) -> list:
        res = []
        for idx, sheet in enumerate(self.sheets):
            res.append(sheet.to_list(**dict(export_parameters[idx])))
        return res

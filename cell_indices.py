from typing import List, Tuple, Dict, Optional
import copy

from grammars import GRAMMARS
from cell_indices_templates import cell_indices_generators, system_languages

# ==== TYPES ====
# mapping from language to list, used for mapping from language to list rows
#   names or column names
T_lg_ar = Dict[str, List[str]]
T_lg_col_row = Dict[str, Tuple[List[str], List[str]]]
# ===============


class CellIndices(object):
    def __init__(self,
                 number_of_rows: int,
                 number_of_columns: int,
                 rows_columns: Optional[T_lg_col_row] = None, /, *,
                 rows_nicknames: List[str] = None,
                 columns_nicknames: List[str] = None,
                 rows_help_text: List[str] = None,
                 columns_help_text: List[str] = None,
                 excel_append_labels: bool = True
                 ):
        """Create cell indices object.

        Args:
            number_of_rows (int): Number of rows.
            number_of_columns (int): Number of columns.
            rows_columns (T_lg_col_row): List of all row names and column names
                for each language.
            rows_nicknames (List[str]): List of masks (nicknames) for row
                names.
            columns_nicknames (List[str]): List of masks (nicknames) for column
                names.
            rows_help_text (List[str]): List of help texts for each row.
            columns_help_text (List[str]): List of help texts for each column.
        """
        # Quick sanity check:
        for language in rows_columns.keys():
            rows, columns = rows_columns[language]
            if len(rows) != number_of_rows:
                raise ValueError("Number of rows is not the same for every "
                                 "language!")
            if len(columns) != number_of_columns:
                raise ValueError("Number of columns is not the same for every "
                                 "language!")
        if number_of_rows < 1 or number_of_columns < 1:
            raise ValueError("Number of rows and columns has to at least 1!")
        # check the columns and rows nicknames sizes
        if (rows_nicknames is not None
                and len(rows_nicknames) != number_of_rows):
            raise ValueError("Number of rows nicknames has to be the same"
                             "as number of rows!")
        if (columns_nicknames is not None
                and len(columns_nicknames) != number_of_columns):
            raise ValueError("Number of columns nicknames has to be the same"
                             "as number of columns!")
        # check the help texts sizes
        if (rows_help_text is not None
                and len(rows_help_text) != number_of_rows):
            raise ValueError("Number of rows help texts has to be the same"
                             "as number of rows!")
        if (columns_help_text is not None
                and len(columns_help_text) != number_of_columns):
            raise ValueError("Number of columns help texts has to be the same"
                             "as number of columns!")
        # -------------------
        self.rows: T_lg_ar = {}
        self.columns: T_lg_ar = {}
        # Append the system languages
        for language, generator in cell_indices_generators.items():
            if language not in system_languages:
                continue
            offset = 0
            if excel_append_labels and language == "excel":
                offset = 1
            rows, cols = generator(number_of_rows + offset,
                                   number_of_columns + offset)
            self.rows[language] = rows[offset:]
            self.columns[language] = cols[offset:]
        # Append the not-system languages and user defined languages
        for language, values in rows_columns.items():
            rows, cols = values
            self.rows[language] = rows
            self.columns[language] = cols
        # Define user defined names for rows and columns
        self.rows_nicknames: List[str] = copy.deepcopy(rows_nicknames)
        self.columns_nicknames: List[str] = copy.deepcopy(columns_nicknames)
        # Or define auto generated nicknames as an integer sequence from 0
        if rows_nicknames is None:
            self.rows_nicknames = list(range(number_of_rows))
        if columns_nicknames is None:
            self.columns_nicknames = list(range(number_of_columns))
        # assign the help texts
        self.rows_help_text: List[str] = copy.deepcopy(rows_help_text)
        self.columns_help_text: List[str] = copy.deepcopy(columns_help_text)
        self.excel_append_labels: bool = excel_append_labels

    @property
    def shape(self) -> Tuple[int]:
        """Return the shape of the object in the NumPy logic.

        Returns:
            Tuple[int]: Number of rows, Number of columns
        """
        language = list(self.columns.keys())[0]
        return len(self.rows[language]), len(self.columns[language])

    @property
    def languages(self) -> List[str]:
        """Return all supported languages.

        Returns:
            List[str]: List of all supported languages.
        """
        return [str(lan) for lan in self.rows.keys()]

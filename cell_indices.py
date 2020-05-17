from typing import List, Tuple, Dict, Optional
import copy

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
            excel_append_labels (bool): If True, one row and column is added
                on the beginning of the sheet as a offset for labels.
        """
        # Quick sanity check:
        if rows_columns is not None:
            for language in rows_columns.keys():
                rows, columns = rows_columns[language]
                if len(rows) != number_of_rows:
                    raise ValueError("Number of rows is not the same for every"
                                     " language!")
                if len(columns) != number_of_columns:
                    raise ValueError("Number of columns is not the same for "
                                     "every language!")
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
        self.number_of_rows: int = number_of_rows
        self.number_of_columns: int = number_of_columns
        self.excel_append_labels: bool = excel_append_labels
        self.rows: T_lg_ar = {}
        self.columns: T_lg_ar = {}
        # Append the system languages
        for language, generator in cell_indices_generators.items():
            if language not in system_languages:
                continue
            offset = 0
            if self.excel_append_labels and language == "excel":
                offset = 1
            rows, cols = generator(self.number_of_rows + offset,
                                   self.number_of_columns + offset)
            self.rows[language] = rows[offset:]
            self.columns[language] = cols[offset:]
        # Append the not-system languages and user defined languages
        self.user_defined_languages: List[str] = []
        if rows_columns is not None:
            for language, values in rows_columns.items():
                rows, cols = values
                self.rows[language] = rows
                self.columns[language] = cols
                self.user_defined_languages.append(language)
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

    @property
    def supported_languages(self) -> List[str]:
        """Returns all languages supported by the indicies.

        Returns:
            List[str]: All languages supported by this indices.
        """
        return [].extend(self.user_defined_languages, system_languages)

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

    def expand_size(self,
                    new_number_of_rows: int,
                    new_number_of_columns: int,
                    new_rows_columns: Optional[T_lg_col_row] = None, /, *,
                    new_rows_nicknames: List[str] = None,
                    new_columns_nicknames: List[str] = None,
                    new_rows_help_text: List[str] = None,
                    new_columns_help_text: List[str] = None,
                    ) -> 'CellIndices':
        """Expand the size of the table.

        Args:
            new_number_of_rows (int): Number of rows to be added.
            new_number_of_columns (int): Number of columns to be added.
            new_rows_columns (T_lg_col_row): List of all row names and column
                names for each language to be added.
            new_rows_nicknames (List[str]): List of masks (nicknames) for row
                names to be added.
            new_columns_nicknames (List[str]): List of masks (nicknames) for
                column names to be added.
            new_rows_help_text (List[str]): List of help texts for each row to
                be added.
            new_columns_help_text (List[str]): List of help texts for each
                column to be added.
        """
        # Quick sanity check:
        if new_number_of_rows < 1 and new_number_of_columns < 1:
            return
        # check the columns and rows nicknames sizes
        if (new_rows_nicknames is not None
                and len(new_rows_nicknames) != new_number_of_rows):
            raise ValueError("Number of rows nicknames has to be the same"
                             "as number of rows!")
        if (new_columns_nicknames is not None
                and len(new_columns_nicknames) != new_number_of_columns):
            raise ValueError("Number of columns nicknames has to be the same"
                             "as number of columns!")
        # check the help texts sizes
        if (new_rows_help_text is not None
                and len(new_rows_help_text) != new_number_of_rows):
            raise ValueError("Number of rows help texts has to be the same"
                             "as number of rows!")
        if (new_columns_help_text is not None
                and len(new_columns_help_text) != new_number_of_columns):
            raise ValueError("Number of columns help texts has to be the same"
                             "as number of columns!")
        # -------------------
        # Append the system languages
        for language, generator in cell_indices_generators.items():
            if language not in system_languages:
                continue
            offset = 0
            if self.excel_append_labels and language == "excel":
                offset = 1
            rows, cols = generator(self.number_of_rows +
                                   new_number_of_rows + offset,
                                   self.number_of_columns +
                                   new_number_of_columns + offset)
            self.rows[language] = rows[offset:]
            self.columns[language] = cols[offset:]
        # Append rows to user defined languages
        for language, values in new_rows_columns.items():
            rows, cols = values
            # Quick sanity check
            if language not in self.user_defined_languages:
                raise ValueError("Users languages has to match to existing "
                                 "ones!")
            if len(rows) != new_number_of_rows:
                raise ValueError("Number of rows has to be the same"
                                 "as number of rows to be added!")
            if len(cols) != new_number_of_columns:
                raise ValueError("Number of columns has to be the same"
                                 "as number of columns to be added!")
            # ------------------

            self.rows[language].extend(rows)
            self.columns[language].extend(cols)

        # Define user defined names for rows and columns
        if new_rows_nicknames is not None:
            self.rows_nicknames.extend(new_rows_nicknames)
        else:
            self.rows_nicknames = list(
                range(self.number_of_rows + new_number_of_rows)
            )
        if new_columns_nicknames is not None:
            self.columns_nicknames.extend(new_columns_nicknames)
        else:
            self.columns_nicknames = list(
                range(self.number_of_columns + new_number_of_columns)
            )
        # Or define auto generated nicknames as an integer sequence from 0
        if new_columns_nicknames is None:
            self.columns_nicknames = list(
                range(self.number_of_columns + new_number_of_columns)
            )
        # assign the help texts
        if self.rows_help_text is not None and new_number_of_rows > 0:
            if new_rows_help_text is None:
                raise ValueError("Rows help texts has to set.")
            self.rows_help_text.extend(new_rows_help_text)
        if self.columns_help_text is not None and new_number_of_columns > 0:
            if new_columns_help_text is None:
                raise ValueError("Columns help texts has to set.")
            self.columns_help_text.extend(new_columns_help_text)

        # Modify the number of rows/columns
        self.number_of_rows += new_number_of_rows
        self.number_of_columns += new_number_of_columns

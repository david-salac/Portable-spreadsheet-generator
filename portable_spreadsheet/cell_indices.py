from typing import List, Tuple, Dict, Optional, Callable
import copy

from .grammars import GRAMMARS
from .cell_indices_templates import cell_indices_generators, system_languages

# ==== TYPES ====
# mapping from language to list, used for mapping from language to list rows
#   names or column names
T_lg_ar = Dict[str, List[str]]
T_lg_col_row = Dict[str, Tuple[List[str], List[str]]]
# ===============


class CellIndices(object):
    """Represent the indices of the cells and its labels for each language.
    """
    def __init__(self,
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
                 ):
        """Create cell indices object.

        Args:
            number_of_rows (int): Number of rows.
            number_of_columns (int): Number of columns.
            rows_columns (T_lg_col_row): List of all row names and column names
                for each language.
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
        """
        # Quick sanity check:
        if rows_labels is not None \
                and len(set(rows_labels)) != len(rows_labels):
            warning_logger("There are some duplications in row labels.")
        if columns_labels is not None \
                and len(set(columns_labels)) != len(columns_labels):
            warning_logger("There are some duplications in column labels.")

        if rows_columns is not None:
            for language in rows_columns.keys():
                # Does the language include the last cell?
                #   if yes, offset of size 1 has to be included.
                offset = 0
                if GRAMMARS[
                    language
                ]['cells']['aggregation']['include_last_cell']:
                    offset = 1
                rows, columns = rows_columns[language]
                if len(rows) != number_of_rows + offset:
                    e_mess = "Number of rows is not the same for every " \
                             "language! Or you have not included offset " \
                             "caused by excluding the last value of the slice!"
                    raise ValueError(e_mess)
                if len(columns) != number_of_columns + offset:
                    e_mess = "Number of columns is not the same for every " \
                             "language! Or you have not included offset " \
                             "caused by excluding the last value of the slice!"
                    raise ValueError(e_mess)
        if number_of_rows < 1 or number_of_columns < 1:
            raise ValueError("Number of rows and columns has to at least 1!")
        # check the columns and rows aliases sizes
        if (rows_labels is not None
                and len(rows_labels) != number_of_rows):
            raise ValueError("Number of rows aliases has to be the same "
                             "as number of rows!")
        if (columns_labels is not None
                and len(columns_labels) != number_of_columns):
            raise ValueError("Number of columns aliases has to be the same "
                             "as number of columns!")
        # check the help texts sizes
        if (rows_help_text is not None
                and len(rows_help_text) != number_of_rows):
            raise ValueError("Number of rows help texts has to be the same "
                             "as number of rows!")
        if (columns_help_text is not None
                and len(columns_help_text) != number_of_columns):
            raise ValueError("Number of columns help texts has to be the same "
                             "as number of columns!")
        # -------------------
        self.number_of_rows: int = number_of_rows
        self.number_of_columns: int = number_of_columns
        self.excel_append_row_labels: bool = excel_append_row_labels
        self.excel_append_column_labels: bool = excel_append_column_labels
        self.rows: T_lg_ar = {}
        self.columns: T_lg_ar = {}
        # Append the system languages
        for language, generator in cell_indices_generators.items():
            if language not in system_languages:
                continue
            offset_row = 0
            offset_column = 0
            if self.excel_append_row_labels and language == "excel":
                offset_column = 1
            if self.excel_append_column_labels and language == "excel":
                offset_row = 1

            rows, cols = generator(self.number_of_rows,
                                   self.number_of_columns,
                                   offset_row,
                                   offset_column)
            self.rows[language] = rows
            self.columns[language] = cols
        # Append the not-system languages and user defined languages
        self.user_defined_languages: List[str] = []
        if rows_columns is not None:
            for language, values in rows_columns.items():
                rows, cols = values
                self.rows[language] = rows
                self.columns[language] = cols
                self.user_defined_languages.append(language)
        # Define user defined names for rows and columns
        self.rows_labels: List[str] = copy.deepcopy(rows_labels)
        self.columns_labels: List[str] = copy.deepcopy(columns_labels)
        # Or define auto generated aliases as an integer sequence from 0
        if rows_labels is None:
            self.rows_labels = [str(_row_n) for _row_n in
                                range(number_of_rows)]
        if columns_labels is None:
            self.columns_labels = [str(_col_n) for _col_n in
                                   range(number_of_columns)]
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
                    new_rows_columns: Optional[T_lg_col_row] = {},
                    /, *,  # noqa E225
                    new_rows_labels: List[str] = None,
                    new_columns_labels: List[str] = None,
                    new_rows_help_text: List[str] = None,
                    new_columns_help_text: List[str] = None,
                    ) -> 'CellIndices':
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
        expanded = copy.deepcopy(self)
        # Quick sanity check:
        if new_number_of_rows < 1 and new_number_of_columns < 1:
            return
        # check the columns and rows aliases sizes
        if (new_rows_labels is not None
                and len(new_rows_labels) != new_number_of_rows):
            raise ValueError("Number of rows aliases has to be the same "
                             "as number of rows!")
        if (new_columns_labels is not None
                and len(new_columns_labels) != new_number_of_columns):
            raise ValueError("Number of columns aliases has to be the same "
                             "as number of columns!")
        # check the help texts sizes
        if (new_rows_help_text is not None
                and len(new_rows_help_text) != new_number_of_rows):
            raise ValueError("Number of rows help texts has to be the same "
                             "as number of rows!")
        if (new_columns_help_text is not None
                and len(new_columns_help_text) != new_number_of_columns):
            raise ValueError("Number of columns help texts has to be the same "
                             "as number of columns!")
        # -------------------
        # Append the system languages
        for language, generator in cell_indices_generators.items():
            if language not in system_languages:
                continue
            offset_row = 0
            offset_column = 0
            if expanded.excel_append_row_labels and language == "excel":
                offset_column = 1
            if expanded.excel_append_column_labels and language == "excel":
                offset_row = 1
            rows, cols = generator(expanded.number_of_rows +
                                   new_number_of_rows + offset_row,
                                   expanded.number_of_columns +
                                   new_number_of_columns + offset_column)
            expanded.rows[language] = rows[offset_row:]
            expanded.columns[language] = cols[offset_column:]
        # Append rows to user defined languages
        for language, values in new_rows_columns.items():
            # Does the language include the last cell?
            #   if yes, offset of size 1 has to be included.
            offset = 0
            if GRAMMARS[
                language
            ]['cells']['aggregation']['include_last_cell']:
                offset = 1
            rows, cols = values
            # Quick sanity check
            if language not in expanded.user_defined_languages:
                raise ValueError("Users languages has to match to existing "
                                 "ones!")
            if len(rows) != new_number_of_rows + offset:
                raise ValueError("Number of rows has to be the same "
                                 "as number of rows to be added! Plus the "
                                 "offset for the ending row.")
            if len(cols) != new_number_of_columns + offset:
                raise ValueError("Number of columns has to be the same "
                                 "as number of columns to be added! Plus the "
                                 "offset for the ending row.")
            # ------------------
            if offset == 1:
                del expanded.rows[language][-1]
                del expanded.columns[language][-1]

            expanded.rows[language].extend(rows)
            expanded.columns[language].extend(cols)

        # Define user defined names for rows and columns
        if new_rows_labels is not None:
            expanded.rows_labels.extend(new_rows_labels)
        else:
            expanded.rows_labels = [
                str(i)
                for i in range(expanded.number_of_rows + new_number_of_rows)
            ]
        if new_columns_labels is not None:
            expanded.columns_labels.extend(new_columns_labels)
        else:
            expanded.columns_labels = [
                str(i)
                for i in range(
                    expanded.number_of_columns + new_number_of_columns
                )
            ]
        # Or define auto generated aliases as an integer sequence from 0
        if new_columns_labels is None:
            expanded.columns_labels = [
                str(i)
                for i in range(
                    expanded.number_of_columns + new_number_of_columns
                )
            ]
        # assign the help texts
        if expanded.rows_help_text is not None and new_number_of_rows > 0:
            if new_rows_help_text is None:
                raise ValueError("Rows help texts has to set.")
            expanded.rows_help_text.extend(new_rows_help_text)
        if expanded.columns_help_text is not None \
                and new_number_of_columns > 0:
            if new_columns_help_text is None:
                raise ValueError("Columns help texts has to set.")
            expanded.columns_help_text.extend(new_columns_help_text)

        # Modify the number of rows/columns
        expanded.number_of_rows += new_number_of_rows
        expanded.number_of_columns += new_number_of_columns

        # Return new expanded indices
        return expanded

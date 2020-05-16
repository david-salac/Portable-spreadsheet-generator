from typing import List, Tuple

from cell_indices_generators import cell_indices_generators


class CellIndices(object):
    def __init__(self,
                 number_of_rows: int,
                 number_of_columns: int,
                 rows_nicknames: List[object] = None,
                 columns_nicknames: List[object] = None
                 ):
        self.rows: dict = {}
        self.columns: dict = {}
        for language, generator in cell_indices_generators.items():
            rows, cols = generator(number_of_rows, number_of_columns)
            self.rows[language] = rows
            self.columns[language] = cols
        # Define user defined names for rows and columns
        self.rows_nicknames: List[object] = rows_nicknames
        self.columns_nicknames: List[object] = columns_nicknames
        if rows_nicknames is None:
            self.rows_nicknames = list(range(number_of_rows))
        if columns_nicknames is None:
            self.columns_nicknames = list(range(number_of_columns))

    def add_rows(self, number: int):
        for language, generator in cell_indices_generators.items():
            number_of_rows = len(self.rows[language])
            rows, cols = generator(number_of_rows + number, 1)
            self.rows[language] = rows
            # TODO: Regenerate nickname rows

    def add_column(self, number: int):
        for language, generator in cell_indices_generators.items():
            number_of_columns = len(self.columns[language])
            rows, cols = generator(1, number_of_columns + number)
            self.columns[language] = cols
            # TODO: Regenerate nickname rows

    @property
    def shape(self) -> Tuple[int]:
        language = list(self.columns.keys())[0]
        return len(self.rows[language]), len(self.columns[language])

    @property
    def languages(self) -> List[str]:
        """Return all supported languages.

        Returns:
            List[str]: List of all supported languages.
        """
        return [str(lan) for lan in cell_indices_generators.keys()]

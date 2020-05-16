from typing import Tuple, List, Optional
import copy

from cell import Cell
from cell_indices import CellIndices

T_sheet = List[List[Cell]]


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
        self.cell_indices: CellIndices = copy.deepcopy(cell_indices)

        self._sheet: T_sheet = self._initialise_array()
        # To make cells accessible using obj.loc[nick_x, nick_y]
        self.iloc = self._Location(self, True)
        # To make cells accessible using obj.iloc[pos_x, pos_y]
        self.loc = self._Location(self, False)

    def _initialise_array(self) -> T_sheet:
        array: T_sheet = []
        for row in range(self.cell_indices.shape[0]):
            row: List[Cell] = []
            for col in range(self.cell_indices.shape[1]):
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

    @property
    def shape(self) -> Tuple[int]:
        return self.cell_indices.shape[0], self.cell_indices.shape[1]

    def reshape(self,
                cell_indices: CellIndices,
                in_place: bool = True) -> Optional['Spreadsheet']:
        pass

    def to_excel(self, file_path: str, sheet_name: str = "Results"):
        # TODO
        pass

    def to_dictionary(self,
                      languages: List[str], /, *,
                      by_row: bool = True,
                      languages_pseudonyms: List[str] = None) -> dict:
        # TODO
        pass

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


indices = CellIndices(5, 6)

sheet = Spreadsheet(indices)
sheet.iloc[0,0] = 7
sheet.iloc[1,0] = 8
sheet.iloc[2,0] = 9
sheet.iloc[3,0] = 10
sheet.iloc[4,0] = 11

sheet.iloc[0,1] = sheet.iloc[0,0] + sheet.iloc[1,0]

print(sheet.values_to_string())

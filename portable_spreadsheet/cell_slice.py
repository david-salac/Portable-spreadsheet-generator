from numbers import Number
from typing import Iterable, Tuple, Union, List

from .cell import Cell


class CellSlice(object):
    def __init__(self,
                 start_idx: Tuple[int, int],
                 end_idx: Tuple[int, int],
                 cell_subset: Iterable[Cell],
                 driving_sheet
                 ):
        self.start_idx: Tuple[int, int] = start_idx
        self.end_idx: Tuple[int, int] = end_idx
        self.cell_subset: Iterable[Cell] = cell_subset
        self.driving_sheet = driving_sheet

    @property
    def shape(self) -> Tuple[int, int]:
        return (self.end_idx[0] - self.start_idx[0] + 1,
                self.end_idx[1] - self.start_idx[1] + 1)

    def sum(self) -> Cell:
        return Cell.sum(self.start_idx, self.end_idx, self.cell_subset)

    def product(self) -> Cell:
        return Cell.product(self.start_idx, self.end_idx, self.cell_subset)

    def min(self) -> Cell:
        return Cell.min(self.start_idx, self.end_idx, self.cell_subset)

    def max(self) -> Cell:
        return Cell.max(self.start_idx, self.end_idx, self.cell_subset)

    def mean(self) -> Cell:
        return Cell.mean(self.start_idx, self.end_idx, self.cell_subset)

    def average(self):
        return self.mean()

    # Set to scalar / Other cells:
    def set(self, other: Union[List[Number], List[Cell],
                               Number, Cell]):
        if isinstance(other, Number):
            # If the scalar is set
            for row in range(self.start_idx[0], self.end_idx[0] + 1):
                for col in range(self.start_idx[1], self.end_idx[1] + 1):
                    cell = self.driving_sheet.iloc[row, col]
                    new_cell = Cell(row, col,
                                    value=other,
                                    cell_indices=cell.cell_indices)
                    self.driving_sheet.iloc[row, col] = new_cell
        elif isinstance(other, Cell):
            # If the reference to a single cell is set
            for row in range(self.start_idx[0], self.end_idx[0] + 1):
                for col in range(self.start_idx[1], self.end_idx[1] + 1):
                    new_cell = Cell(row, col,
                                    cell_indices=other.cell_indices)
                    self.driving_sheet.iloc[row, col] = new_cell.reference(
                        other
                    )

    def __ilshift__(self, other):
        self.set(other)

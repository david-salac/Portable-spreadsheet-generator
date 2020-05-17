from typing import Iterable, Tuple

from cell import Cell


class CellSlice(object):
    def __init__(self,
                 start_idx: Tuple[int, int],
                 end_idx: Tuple[int, int],
                 cell_subset: Iterable[Cell]
                 ):
        self.start_idx: Tuple[int, int] = start_idx
        self.end_idx: Tuple[int, int] = end_idx
        self.cell_subset: Iterable[Cell] = cell_subset

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
    def set(self, other):
        # TODO:
        pass

    def __ilshift__(self, other):
        self.set(other)

from typing import Dict, Optional, Iterable, Tuple, Callable

import numpy as np

from .word_constructor import WordConstructor
from .cell_type import CellType
from .cell_indices import CellIndices


class Cell(object):
    def __init__(self,
                 row: Optional[int] = None,
                 column: Optional[int] = None, /,  # noqa E999
                 value: Optional[float] = None, *,
                 words: Optional[WordConstructor] = None,
                 cell_type: CellType = CellType.value_only,
                 cell_indices: CellIndices):
        if row is not None and column is None \
                or row is None and column is not None:
            raise ValueError("The values of 'row' and 'column' parameters have"
                             " to be either both not None or both None.")
        self.row: Optional[int] = row
        self.column: Optional[int] = column
        self._value: Optional[float] = value
        self.cell_type: CellType = cell_type
        self.cell_indices: cell_indices = cell_indices  # pass only reference
        self.anchored = not(row is None or column is None)

        if words is not None:
            self.words: WordConstructor = words
        else:
            self.words: WordConstructor = WordConstructor.init_from_values(
                column, row, cell_indices=cell_indices,
                cell_type=cell_type, value=value
            )

    @property
    def value(self):
        return self._value

    @staticmethod
    def brackets(other: 'Cell', /):  # noqa E225
        return Cell(value=other._value,
                    words=WordConstructor.brackets(other.words),
                    cell_indices=other.cell_indices,
                    cell_type=CellType.computational)

    def add(self, other: 'Cell', /):  # noqa E225
        return Cell(value=self._value + other._value,
                    words=self.words.add(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def subtract(self, other: 'Cell', /):  # noqa E225
        return Cell(value=self._value - other._value,
                    words=self.words.subtract(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def multiply(self, other: 'Cell', /):  # noqa E225
        return Cell(value=self._value * other._value,
                    words=self.words.multiply(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def divide(self, other: 'Cell', /):  # noqa E225
        return Cell(value=self._value / other._value,
                    words=self.words.divide(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def power(self, other: 'Cell', /):  # noqa E225
        return Cell(value=self._value ** other._value,
                    words=self.words.power(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def logarithm(self, other: 'Cell', /):  # noqa E225
        # TODO: Check this word creation
        return Cell(value=np.log(number),
                    words=self.words.logarithm(number),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def exponential(self, other: 'Cell', /):  # noqa E225
        # TODO: Check this word creation
        return Cell(value=np.exp(number),
                    words=self.words.exponential(number),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    # Overload the operator *
    def __mul__(self, other):
        return self.multiply(other)

    # Overload the operator -
    def __sub__(self, other):
        return self.subtract(other)

    # Overload the operator +
    def __add__(self, other):
        return self.add(other)

    # Overload the operator /
    def __truediv__(self, other):
        return self.divide(other)

    # Overload the operator **
    def __pow__(self, power, modulo=None):
        return self.power(power)

    # override
    def __str__(self):
        return str(self.parse)

    @property
    def parse(self) -> Dict[str, str]:
        return self.words.parse(self.cell_type, constant_value=self.value)

    @staticmethod
    def sum(start_idx: Tuple[int, int], end_idx: Tuple[int, int],
            subset: Iterable['Cell']) -> 'Cell':
        return Cell._aggregate_fun(start_idx, end_idx, subset,
                                   'sum', np.sum)

    @staticmethod
    def product(start_idx: Tuple[int, int], end_idx: Tuple[int, int],
                subset: Iterable['Cell']) -> 'Cell':
        return Cell._aggregate_fun(start_idx, end_idx, subset,
                                   'product', np.prod)

    @staticmethod
    def mean(start_idx: Tuple[int, int], end_idx: Tuple[int, int],
             subset: Iterable['Cell']) -> 'Cell':
        return Cell._aggregate_fun(start_idx, end_idx, subset,
                                   'mean', np.mean)

    @staticmethod
    def min(start_idx: Tuple[int, int], end_idx: Tuple[int, int],
            subset: Iterable['Cell']) -> 'Cell':
        return Cell._aggregate_fun(start_idx, end_idx, subset,
                                   'minimum', np.min)

    @staticmethod
    def max(start_idx: Tuple[int, int], end_idx: Tuple[int, int],
            subset: Iterable['Cell']) -> 'Cell':
        return Cell._aggregate_fun(start_idx, end_idx, subset,
                                   'maximum', np.max)

    @staticmethod
    def _aggregate_fun(
            start_idx: Tuple[int, int],
            end_idx: Tuple[int, int],
            subset: Iterable['Cell'],
            grammar_method: str,
            method_np: Callable[[Iterable[float]], float]
    ) -> 'Cell':
        return Cell(value=method_np([c.value for c in subset]),
                    cell_indices=subset[0].cell_indices,
                    cell_type=CellType.computational,
                    words=subset[0].words.aggregation(start_idx, end_idx,
                                                      grammar_method))

    @staticmethod
    def reference(other: 'Cell', /):  # noqa E225
        return Cell(other.row, other.column,
                    value=other.value,
                    words=WordConstructor.init_from_values(
                        other.column, other.row,
                        other.cell_indices, CellType.computational
                    ),
                    cell_indices=other.cell_indices,
                    cell_type=CellType.computational)

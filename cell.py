from typing import Dict, Optional

import numpy as np

from word_constructor import WordConstructor
from cell_type import CellType
from cell_indices import CellIndices


class Cell(object):
    def __init__(self,
                 row: Optional[int] = None,
                 column: Optional[int] = None, /,
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
    def brackets(other: 'Cell', /):
        return Cell(value=other._value,
                    words=WordConstructor.brackets(other.words),
                    cell_indices=other.cell_indices,
                    cell_type=CellType.computational)

    def add(self, other: 'Cell', /):
        return Cell(value=self._value + other._value,
                    words=self.words.add(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def subtract(self, other: 'Cell', /):
        return Cell(value=self._value - other._value,
                    words=self.words.subtract(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def multiply(self, other: 'Cell', /):
        return Cell(value=self._value * other._value,
                    words=self.words.multiply(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def divide(self, other: 'Cell', /):
        return Cell(value=self._value / other._value,
                    words=self.words.divide(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def power(self, other: 'Cell', /):
        return Cell(value=self._value ** other._value,
                    words=self.words.power(other.words),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def logarithm(self, number: float, /):
        return Cell(value=np.log(number),
                    words=self.words.constant(np.log(number)),
                    cell_indices=self.cell_indices,
                    cell_type=CellType.computational)

    def exponential(self, number: float, /):
        return Cell(value=np.exp(number),
                    words=self.words.constant(np.log(number)),
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


# TODO: delete following:
"""
indices = CellIndices(5, 5)
A1 = Cell(0, 0, 2, cell_indices=indices)
B2 = Cell(1, 1, 5, cell_indices=indices)
C1 = Cell(0, 2, 6, cell_indices=indices)

A3 = Cell.brackets(B2 + C1) * A1 / B2
A4 = Cell.brackets(B2)
print(A1.parse)
print(B2.parse)
print(A3.parse)
print(A3)
print(A4)
print(A3.value)
print(B2.parse)
A1 = B2 * Cell(value=8.0, cell_type=CellType.value_only, cell_indices=indices)
print(A1.parse)
print(A1.value)
"""
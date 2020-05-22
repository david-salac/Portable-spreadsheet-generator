import abc
from typing import Tuple


class Serialization(abc.ABC):
    """Provides basic functionality for exporting to required formats.
    """
    @abc.abstractmethod
    def get_shape(self) -> Tuple[int, int]:
        """Get the shape as the tuple of number of rows and columns.

        Returns:
            Tuple[int, int]: number of rows, columns
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_cell_at(self, row: int, column: int) -> 'Cell':
        """Get the particular cell on the (row, column) position.

        Returns:
            Cell: The call on given position.
        """
        raise NotImplementedError

from enum import Enum


class CellType(Enum):
    """Reflect the cell type in the table, there are just two types one is the
        cell holding some constant and another one is the cell doing some
        computations.
    """
    # Type of cell that contains only constant
    value_only = "value_only"
    # Type of cell that does computations
    computational = "computational"

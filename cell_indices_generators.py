from typing import List, Tuple


def general_interface(rows: int, columns: int) -> Tuple[List[str], List[str]]:
    """Generate the series of the labels for rows and columns.

    Args:
        rows (int): How many rows should be generated
        columns (int): How many columns should be generated
    Return:
        Tuple[List[str], List[str]]: Tuple of indices for rows and columns
    """
    # This is the template interface
    pass


def excel_generator(rows: int, columns: int) -> Tuple[List[str], List[str]]:
    rows = list([str(row) for row in range(1, rows + 1)])
    letter_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    cols = []
    for column in range(0, columns):
        col = column + 1
        result = []
        while col:
            col, rem = divmod(col - 1, 26)
            result[:0] = letter_list[rem]
        cols.append(''.join(result))
    return rows, cols


def python_numpy_generator(rows: int, columns: int) \
        -> Tuple[List[str], List[str]]:
    rows = list([str(row) for row in range(0, rows)])
    cols = list([str(col) for col in range(0, columns)])
    return rows, cols


def native_generator(rows: int, columns: int) -> Tuple[List[str], List[str]]:
    rows = list([str(row) for row in range(1, rows + 1)])
    cols = list([str(col) for col in range(1, columns + 1)])
    return rows, cols


cell_indices_generators = {
    "excel": excel_generator,
    "python_numpy": python_numpy_generator,
    "native": native_generator,
}

from typing import List, Tuple


def general_interface(rows: int,
                      columns: int,
                      offset_row: int = 0,
                      offset_column: int = 0) -> Tuple[List[str], List[str]]:
    """Generate the series of the labels for rows and columns.

    Args:
        rows (int): How many rows should be generated
        columns (int): How many columns should be generated
        offset_row (int) The row offset from the beginning
        offset_column (int) The column offset from the beginning

    Return:
        Tuple[List[str], List[str]]: Tuple of indices for rows and columns
    """
    # This is the template interface
    pass


def excel_column(column: int) -> str:
    """Convert column position (indexed from 0) to Excel column name.

    Args:
        column (int): Column index (position from 0).

    Returns:
        str: Definition of column in Excel.
    """
    letter_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = []
    column += 1
    while column:
        column, rem = divmod(column - 1, 26)
        result[:0] = letter_list[rem]
    return ''.join(result)


def excel_generator(rows: int,
                    columns: int,
                    offset_row: int = 0,
                    offset_column: int = 0) -> Tuple[List[str], List[str]]:
    rows = list([str(row)
                 for row in range(1 + offset_row, rows + 1 + offset_row)])
    letter_list = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    cols = []
    for column in range(offset_column, columns + offset_column):
        col = column + 1
        result = []
        while col:
            col, rem = divmod(col - 1, 26)
            result[:0] = letter_list[rem]
        cols.append(''.join(result))
    return rows, cols


def python_numpy_generator(rows: int,
                           columns: int,
                           offset_row: int = 0,
                           offset_column: int = 0
                           ) -> Tuple[List[str], List[str]]:
    # the + 1 value is because of offset for slices
    rows = list([str(row) for row in range(offset_row, rows + offset_row + 1)])
    # the + 1 value is because of offset for slices
    cols = list([str(col) for col in range(offset_column,
                                           columns + offset_column + 1)])
    return rows, cols


def native_generator(rows: int,
                     columns: int,
                     offset_row: int = 0,
                     offset_column: int = 0) -> Tuple[List[str], List[str]]:
    rows = list([str(row) for row in range(
        1 + offset_row, rows + offset_row + 1)]
                )
    cols = list([str(col) for col in range(
        1 + offset_column, columns + offset_column + 1)])
    return rows, cols


cell_indices_generators = {
    "excel": excel_generator,
    "python_numpy": python_numpy_generator,
    "native": native_generator,
}
system_languages = [] #['excel']  # ['excel', 'python_numpy']

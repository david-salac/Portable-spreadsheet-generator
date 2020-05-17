import portable_spreadsheet as ps

nr_row = 5
nr_col = 6
# Define the indices for columns and rows and (potentially) help texts
cell_indices = ps.CellIndices(
    nr_row, nr_col,
    {
        "native": ([str(i + 1) for i in range(nr_row)],
                   [str(i + 1) for i in range(nr_col)])
    },
    rows_nicknames=['first row', 'second row', 'third row', 'fourth row',
                    'fifth row'],
    columns_nicknames=['first column', 'second column', 'third column',
                       'fourth column', 'fifth column', 'sixth column'],
    rows_help_text=['Super row 1', 'Super row 2', 'Super row 3', 'Super row 4',
                    'Super row 5'],
)

sheet = ps.Spreadsheet(cell_indices)

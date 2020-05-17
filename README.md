# Simple Portable Python Spreadsheet Generator
Author: David Salac <http://github.com/david-salac>

Simple spreadsheet that keeps tracks of each operations in defined languages.
Logic allows export sheets to Excel files (and see how each cell is computed),
to the JSON strings with description of computation e. g. in native language.
It also allows to reconstruct behaviours in native Pandas with Numpy.

## Software User Manual (SUM), how to use it?
### Installation
TODO (will be a package with setup.py)

### Demo
```
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
# Insert some fixed values to the first column
sheet.loc[:, 'first column'] = 23
# Say that first item in second column is the sum of all values in first col
sheet.iloc[0, 1] = sheet.loc[:, "first column"].sum()
# Say that value B2 is the result of A1 + B1
sheet.iloc[1, 1] = sheet.iloc[0, 0] + sheet.iloc[0, 1]

# If you want to export result to the Excel:
# sheet.to_excel("PATH_TO_EXCEL_FILE.xlsx")

# If you want to export result to JSON (or dictionary):
dictionary = sheet.to_dictionary(['native'])
# Dictionary looks like:
# {'rows': {'first row': {'columns': {'first column': {'native': '23',
# 'value': 23}, 'second column': {'native': 'sum of values from (1, 1) to
# (5, 1)', 'value': 115}}, 'help_text': 'Super row 1'}, 'second row':
# {'columns': {'first column': {'native': '23', 'value': 23}, 'second column':
# {'native': 'value at (1, 1) + sum of values from (1, 1) to (5, 1)', 'value':
# 138}}, 'help_text': 'Super row 2'}, 'third row': {'columns': {'first column':
# {'native': '23', 'value': 23}}, 'help_text': 'Super row 3'}, 'fourth row':
# {'columns': {'first column': {'native': '23', 'value': 23}}, 'help_text':
# 'Super row 4'}, 'fifth row': {'columns': {'first column': {'native': '23',
# 'value': 23}}, 'help_text': 'Super row 5'}}}
```

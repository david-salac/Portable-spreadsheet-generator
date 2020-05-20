# Simple Portable Python Spreadsheet Generator
Author: David Salac <http://github.com/david-salac>

Simple spreadsheet that keeps tracks of each operation in defined languages.
Logic allows export sheets to Excel files (and see how each cell is computed),
to the JSON strings with description of computation e. g. in native language.
Other formats like CSV and Markdown (MD) are also supported. It also allows
to reconstruct behaviours in native Python with NumPy.

## Key components of the library
There are five main objects in the library:
Grammar: the set of rule that defines language.
Cell: single cell inside the spreadsheet.
Word: the word describing how the cell is created in each language.
Spreadsheet: a set of cells with a defined shape.
Cell slice: a subset of the spreadsheet. 
### Grammar
The grammar defines a context-free language (by Chomsky hierarchy). It is used for describing each operation that is done with the cell. The typical world is constructed using prefix, suffix and actual value by creating a string like "PrefixValueSuffix". Each supported operation is defined in grammar (that tells how the word is created when the operation is called).
There are two system languages (grammars): Python and Excel. There is also one language "native" that describes operations in a native tongue logic.
#### Adding the new grammar
Operations with grammars are encapsulated in the class `GrammarUtils`.

Grammar has to be defined as is described in the file `grammars.py` in the global variable `GRAMMAR_PATTERN`. It is basically the dictionary matching the description.

To validate the grammar (in the variable `grammar`) use: 
```
is_valid: bool = GrammarUtils.validate_grammar(grammar)
```
To add the grammar describing some language (in the variable `language`) to the system (in the variable `grammar`) use: 
```
GrammarUtils.add_grammar(grammar, language)
```
### Cells
It represents the smallest element in the spreadsheet. Cell encapsulates basic arithmetic operations that are needed. A cell is represented by the class of the same name `Cell`. It is highly recommended not to use this class directly but only through the spreadsheet instance.
Currently, the supported operations are:
Adding: (method add), operator +, simply add two cells.
Subtracting: (method subtract), operator -, simply subtract two cells.
Multiplying: (method multiply), operator *, simply multiply two cells.
Dividing: (method divide), operator /, simply divide two cells.
Power to: (method power), operator **, simply compute cell power to another cell.
Brackets: add brackets around the formula.
Aggregated functions: sum, product, minimum, maximum, average (aka mean) that operates with a set of cells.
Logarithm: (method logarithm), simply compute a natural logarithm of a cell.
Exponential: (method exponential), simply compute an exponential value of a cell.
The main purpose of the cell is to keep the value (the numerical result of the computation) and the word (how is an operation or constant represented in all languages).

### Words
Word represents the current computation or value of the cell using in given languages.
A typical example of the word can be (in language excel):
```
B2*(C1+C2)
```
The equivalent word in the language Python:
```
values[1,1]*(values[0,2]+values[1,2])
```
Words are constructed using prefixes and suffixes defined by the grammar. Each language also has some special features that are also described in the grammar (like whether the first index represents column or a row).
Words are important later when the output is exported to some file in given format or to JSON.
Operations with words (and word as a data structure) are located in the class `WordConstructor`. It should not be used directly.

### Spreadsheet class
The Spreadsheet is the most important class of the whole package. It is located in the file `spreadsheet.py`. It encapsulates the functionality related to accessing cells and modifying them as well as the functionality for exporting of the computed results to various formats.

Class is strongly motivated by the API of the Pandas DataFrame. 

Spreadsheet functionality is documented bellow in a special section.

### Cell slice
Represents the special object that is created when some part slice of the spreadsheet is created. Basically, it encapsulates the set of cells and aggregating operations (sum, product, minimum, maximum, average). For example:
```
some_slice = spreadsheet_instance.iloc[1,:]
average_of_slice = some_slice.mean()
```
selected the second row in the spreadsheet and compute the average (mean) of values in the slice.

Cell slice is represented in the class `CellSlice` in the file `cell_slice.py`.

#### Functionality of the CellSlice class
Cell slice is mainly related to the aggregating functions:
Average (or Mean), available in function `average` (as well as `mean`): computes the arithmetical mean-average of the cells in the slice.
Sum, available in function `sum`: computes the sum of the cells in the slice.
Product, available in function `product`: computes the product of the cells in the slice (multiply all of them).
Minimum and Maximum, available in the functions `min` and `max`: compute the minimum or maximum of the cells in the slice.
There is also a functionality related to setting the values to some constant or reference to another cell. This functionality should not be used directly.

## Spreadsheets functionality


## Software User Manual (SUM), how to use it?
### Installation
To install package use the command:

`pip install portable-spreadsheet`

### Demo
The following demo contains the simple example with aggregations.
```
import portable_spreadsheet as ps
import numpy as np

# This is a simple demo that represents the possibilities of the package
#   The purpose of this demo is to create a class rooms and monitor students

sheet = ps.Spreadsheet.create_new_sheet(
    # Size of the table (rows, columns):
    24, 8,
    rows_labels=['Adam', 'Oliver', 'Harry', 'George', 'John', 'Jack', 'Jacob',
                 'Leo', 'Oscar', 'Charlie', 'Peter', 'Olivia', 'Amelia',
                 'Isla', 'Ava', 'Emily', 'Isabella', 'Mia', 'Poppy',
                 'Ella', 'Lily', 'Average of all', 'Average of boys',
                 'Average of girls'],
    columns_labels=['Biology', 'Physics', 'Math', 'English', 'French',
                    'Best performance', 'Worst performance', 'Mean'],
    columns_help_text=[
        'Annual performance', 'Annual performance', 'Annual performance',
        'Annual performance', 'Annual performance',
        'Best performance of all subjects',
        'Worst performance of all subjects',
        'Mean performance of all subjects',
    ]
)

# === Insert some percentiles to students performance: ===
# A) In this case insert random values in the first row to the 3rd row from the
#   end, and in the first column.
sheet.iloc[:-3, 0] = np.random.random(21) * 100
# B) Same can be achieved using the label indices:
sheet.loc["Adam":'Average of all', 'Physics'] = np.random.random(21) * 100
# C) Or by using the cell by cell approach:
for row_idx in range(21):
    # I) Again by the simple integer index
    sheet.iloc[row_idx, 2] = np.random.random() * 100
    # II) Or by the label
    row_label: str = sheet.cell_indices.rows_labels[row_idx]
    sheet.loc[row_label, 'English'] = np.random.random() * 100
# Insert values to last column
sheet.iloc[:21, 4] = np.random.random(21) * 100

# === Insert computations ===
# Insert the computations on the row
for row_idx in range(21):
    # I) Maximal value
    sheet.iloc[row_idx, 5] = sheet.iloc[row_idx, 0:5].max()
    # II) Minimal value
    sheet.iloc[row_idx, 6] = sheet.iloc[row_idx, 0:5].min()
    # II) Mean value
    sheet.iloc[row_idx, 7] = sheet.iloc[row_idx, 0:5].mean()
# Insert the similar to rows:
for col_idx in range(8):
    # I) Values of all
    sheet.iloc[21, col_idx] = sheet.iloc[0:21, col_idx].average()
    # II) Values of boys
    sheet.iloc[22, col_idx] = sheet.iloc[0:11, col_idx].average()
    # II) Values of girls
    sheet.iloc[23, col_idx] = sheet.iloc[11:21, col_idx].average()

# Export results to Excel file:
sheet.to_excel("outputs/student_marks.xlsx", sheet_name="Marks")

# Top print table as Markdown
print(sheet.to_markdown())
```

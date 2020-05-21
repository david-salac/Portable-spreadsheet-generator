# Simple Portable Python Spreadsheet Generator
Author: David Salac <http://github.com/david-salac>

Simple spreadsheet that keeps tracks of each operation in defined languages.
Logic allows export sheets to Excel files (and see how each cell is computed),
to the JSON strings with description of computation e. g. in native language.
Other formats like CSV and Markdown (MD) are also supported. It also allows
to reconstruct behaviours in native Python with NumPy.

## Key components of the library
There are five main objects in the library:

1. Grammar: the set of rule that defines language.
2. Cell: single cell inside the spreadsheet.
3. Word: the word describing how the cell is created in each language.
4. Spreadsheet: a set of cells with a defined shape.
5. Cell slice: a subset of the spreadsheet. 

### Grammar
The grammar defines a context-free language (by Chomsky hierarchy). It is
used for describing each operation that is done with the cell. The typical
world is constructed using prefix, suffix and actual value by creating a
string like "PrefixValueSuffix". Each supported operation is defined in
grammar (that tells how the word is created when the operation is called).

There are two system languages (grammars): Python and Excel. There is also
one language "native" that describes operations in a native tongue logic.
#### Adding the new grammar
Operations with grammars are encapsulated in the class `GrammarUtils`.

Grammar has to be defined as is described in the file `grammars.py` in the
global variable `GRAMMAR_PATTERN`. It is basically the dictionary matching
the description.

To validate the grammar (in the variable `grammar`) use: 
```
is_valid: bool = GrammarUtils.validate_grammar(grammar)
```
To add the grammar describing some language (in the variable `language`)
to the system (in the variable `grammar`) use: 
```
GrammarUtils.add_grammar(grammar, language)
```
### Cells
It represents the smallest element in the spreadsheet. Cell encapsulates basic
arithmetic operations that are needed. A cell is represented by the class of
the same name `Cell`. It is highly recommended not to use this class directly
but only through the spreadsheet instance.

Currently, the supported operations are:

* Adding: (method add), operator +, simply add two cells.
* Subtracting: (method subtract), operator -, simply subtract two cells.
* Multiplying: (method multiply), operator *, simply multiply two cells.
* Dividing: (method divide), operator /, simply divide two cells.
* Power to: (method power), operator **, simply compute cell power to another
cell.
* Brackets: add brackets around the formula.
* Aggregated functions: sum, product, minimum, maximum, average (aka mean)
that operates with a set of cells.
* Logarithm: (method logarithm), simply compute a natural logarithm of a cell.
* Exponential: (method exponential), simply compute an exponential value of a
cell.

The main purpose of the cell is to keep the value (the numerical result of
the computation) and the word (how is an operation or constant represented
in all languages).

### Words
Word represents the current computation or value of the cell using in given
languages.

A typical example of the word can be (in language excel):
```
B2*(C1+C2)
```
The equivalent word in the language Python:
```
values[1,1]*(values[0,2]+values[1,2])
```
Words are constructed using prefixes and suffixes defined by the grammar.
Each language also has some special features that are also described in
the grammar (like whether the first index represents column or a row).

Words are important later when the output is exported to some file in given
format or to JSON.
Operations with words (and word as a data structure) are located in the
class `WordConstructor`. It should not be used directly.

### Spreadsheet class
The Spreadsheet is the most important class of the whole package. It is
located in the file `spreadsheet.py`. It encapsulates the functionality
related to accessing cells and modifying them as well as the functionality
for exporting of the computed results to various formats.

Class is strongly motivated by the API of the Pandas DataFrame. 

Spreadsheet functionality is documented bellow in a special section.

### Cell slice
Represents the special object that is created when some part slice of the
spreadsheet is created. Basically, it encapsulates the set of cells and
aggregating operations (sum, product, minimum, maximum, average). For example:
```
some_slice = spreadsheet_instance.iloc[1,:]
average_of_slice = some_slice.mean()
```
selected the second row in the spreadsheet and compute the average (mean)
of values in the slice.

Cell slice is represented in the class `CellSlice` in the
file `cell_slice.py`.

#### Functionality of the CellSlice class
Cell slice is mainly related to the aggregating functions:

1. Average (or Mean), available in function `average` (as well as `mean`):
computes the arithmetical mean-average of the cells in the slice.
2. Sum, available in function `sum`: computes the sum of the cells in the
slice.
3. Product, available in function `product`: computes the product of the
cells in the slice (multiply all of them).
4. Minimum and Maximum, available in the functions `min` and `max`: compute
the minimum or maximum of the cells in the slice.

There is also a functionality related to setting the values to some
constant or reference to another cell. This functionality should not
be used directly.

## Spreadsheets functionality
All following examples expect that user has already imported package.
```
import portable_spreadsheet as ps
```
The default (or system) languages are Excel and Python. There is also
a language called 'native' ready to be used.

### How to create a spreadsheet
The easiest function is to use the built-in static method `create_new_sheet`:
```
sheet = ps.SpreadSheet.create_new_sheet(
    number_of_rows, number_of_columns, [rows_columns]
)
```
if you wish to include some user-defined languages or the language
called 'native' (which is already in the system), you also need to
pass the argument `rows_columns` (that is a dictionary with keys as
languages and values as lists with column names in a given language).
If you choose to add a 'native' language, you can use a shorter version:
```
sheet = ps.SpreadSheet.create_new_sheet(
    number_of_rows, number_of_columns, 
    {
        "native": cell_indices_generators['native'](number_of_rows, 
                                                    number_of_columns),
    }
)
```
Other (keywords) arguments:

1. rows_labels (List[str]): List of masks (nicknames) for row names.
2. columns_labels (List[str]): List of masks (nicknames) for column names.
3. rows_help_text (List[str]): List of help texts for each row.
4. columns_help_text (List[str]): List of help texts for each column.
5. excel_append_labels (bool): If True, one row and column is added on the
beginning of the sheet as an offset for labels.

First two are the most important because they define labels for the columns
and rows indices.

#### How to change the size of the spreadsheet
You can only expand the size of the spreadsheet (it's because of the
built-in behaviour of languages). We, however, strongly recommend not to
do so.
```
sheet.expand_size(
    sheet.cell_indices.expand_size(
        number_of_new_rows, number_of_new_columns, [new_rows_columns]
    )
)
```
Parameters of the `cell_indices.expand_size` method are of the same
logic as the parameters of `SpreadSheet.create_new_sheet`.

### Shape of the SpreadSheet object
If you want to know what is the actual size of the spreadsheet, you can
use the property `shape` that behaves as in Pandas. It returns you the
tuple with a number of rows and number of columns (on the second position).

### Accessing/setting the cells in the spreadsheet
You to access the value in the position you can use either the integer
position (indexed from 0) or the label of the row/column.
```
# Returns the value at second row and third column:
value = sheet.iloc[1,2]
# Returns the value by the name of the row, column
value = sheet.loc['super the label of row', 'even better label of column']
```
As you can see, there are build-in properties `loc` and `iloc` for accessing
the values (the `loc` access based on the label, and `iloc` access the cell
based on the integer position).

The same logic can be used for setting-up the values:
```
# Set the value at second row and third column:
sheet.iloc[1,2] = value
# Set the value by the name of the row, column
sheet.loc['super the label of row', 'even better label of column'] = value
```
where the variable `value` can be either some constant (string, float or
created by the `fn` method described below) or the result of some
operations with cells:
```
sheet.iloc[1,2] = sheet.iloc[1,3] + sheet.iloc[1,4]
```
In the case that you want to assign the result of some operation (or just
reference to another cell), make sure that it does not contains any reference
to itself (coordinates where you are assigning). It would not work
correctly otherwise.
### Working with slices
Similarly, like in NumPy or Pandas DataFrame, there is a possibility
how to work with slices (e. g. if you want to select a whole row, column
or set of rows and columns). Following code, select the third column:
```
sheet.iloc[:,2]
```
You can again set the values in the slice to some constant, or the array
of constants, or to another cell, or to the result of some computation.
```
sheet.iloc[:,2] = constant  # Constant (float, string)
sheet.iloc[:,2] = sheet.iloc[1,3] + sheet.iloc[1,4]  # Computation result
sheet.iloc[:,2] = sheet.iloc[1,3]  # Just a reference to a cell
```
#### Aggregate functions
The slice itself can be used for computations using aggregate functions
(sum, product, average, minimum, maximum): 
```
sheet.iloc[1,3] = sheet.iloc[:,2].sum()  # Find sum of cells in the 3rd row.
sheet.iloc[1,3] = sheet.iloc[:,2].product()  # Find the product...
sheet.iloc[1,3] = sheet.iloc[:,2].min()  # Find the minimum...
sheet.iloc[1,3] = sheet.iloc[:,2].max()  # Find the maximum...
sheet.iloc[1,3] = sheet.iloc[:,2].mean()  # Find the mean-average...
```
You can also export slice to the NumPy array using `.to_numpy()` method.

### Computations
All operations have to be done using the objects of type Cell. 

#### Constants
If you want to use a constant value, you need to create an un-anchored cell
with this value. The easiest way of doing so is:
```
# For creating the Cell for computation with constant value 7
constant_cell = sheet.fn.const(7)
```
The value OPERAND bellow is always the reference to another cell in the
sheet or the constant created as just described.
#### Unary operations
There are just two unary operations: exponential and logarithm of the value:
```
# Natural logarithm:
sheet[i,j] = sheet.fn.ln(OPERAND)
# Exponential function:
sheet[i,j] = sheet.fn.exp(OPERAND)
```
All unary operators are defined in the `fn` property of the SpreadSheet
object (together with brackets, that works exactly the same - see bellow).
#### Binary operations
All the basic operations are covered: adding, subtracting, multiplying,
dividing, the power to something. They are accessible using the overloaded
operators (`+`, `-`, `*`, `/`, `**`):
```
sheet[i,j] = OPERAND_1 + OPERAND_2
sheet[i,j] = OPERAND_1 - OPERAND_2
sheet[i,j] = OPERAND_1 * OPERAND_2
sheet[i,j] = OPERAND_1 / OPERAND_2
sheet[i,j] = OPERAND_1 ** OPERAND_2
```
Operations can be chained in the string:
```
sheet[i,j] = OPERAND_1 + OPERAND_2 * OPERAND_3 ** OPERAND_4
```
The priority of the operators is the same as in normal mathematics. If
you need to modify priority, you need to use brackets.
#### Brackets for computation
Brackets are technically speaking just another unary operator. They are
defined in the `fn` property. They can be used like:
```
sheet[i,j] = sheet.fn.brackets(OPERAND_1 + OPERAND_2) * OPERAND_3 ** OPERAND_4
```
#### Example
For example
```
# Equivalent of: value at [1,0] * (value at [2,1] + value at [3,1]) * exp(9)
sheet[0,0] = sheet[1,0] * sheet.fn.brackets(sheet[2,1] + sheet[3,1]) 
             * sheet.fn.exp(sheet.fn.const(9))
```
### Accessing the computed values
You can access either to the actual numerical value of the cell or to the
word that is created in all the languages. The numerical value is accessible
using the `value` property, whereas the words are accessible using
the `parse` property (it returns a dictionary with languages as keys
and word as values).
```
# Access the value of the cell
value_of_cell: float = sheet[i, j].value
# Access all the words in the cell
word: dict = sheet[i, j].parse
# Access the word in language 'lang'
word_in_language_lang = word['lang']
```

### Exporting the results
There are various methods available for exporting the results:
* `to_excel`: Export the sheet to the Excel-compatible file.
* `to_dictionary`: Export the sheet to the dictionary (`dict` type) that
can be used for creating of JSON.
* `to_string_of_values`: Export values to the string that looks like Python
array definition string.
* `to_csv`: Export the values to the CSV compatible string (that can be saved
to the file)
* `to_markdown`: Export the values to MD (Markdown) file format string.
Defined as a table.
* `to_numpy`: Export the sheet as a numpy.ndarray object.

#### Exporting to Excel
It can be done using the interface:
```
sheet.to_excel(file_path: str, /, *, sheet_name: str = "Results", 
               spaces_replacement: str = ' ', 
               label_format: dict = {'bold': True})
```
The only required argument is the path to the destination file (positional
only parameter). Other parameters are passed as keywords (non-positional only). 
* **file_path** (str): Path to the target .xlsx file. (REQUIRED, only
positional)
* sheet_name (str): The name of the sheet inside the file.
* spaces_replacement (str): All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* label_format (dict): Excel styles for the label rows and columns, see
documentation: https://xlsxwriter.readthedocs.io/format.html

#### Exporting to the dictionary
It can be done using the interface:
```
sheet.to_excel(languages: List[str] = None, /, *, by_row: bool = True,
               languages_pseudonyms: List[str] = None,
               spaces_replacement: str = ' ')
```
Parameters are (all optional):

* languages (List[str]): List of languages that should be exported.
* by_row (bool): If True, rows are the first indices and columns are the
second in the order. If False it is vice-versa.
* languages_pseudonyms (List[str]): Rename languages to the strings inside
this list.
* spaces_replacement (str): All the spaces in the rows and columns
descriptions (labels) are replaced with this string.

**The return value is:** 

Dictionary with keys: 1. column/row, 2. row/column, 3. language or
language pseudonym or 'value' keyword for values -> value as a value or
as a cell building string.

#### Exporting to the CSV
It can be done using the interface:
```
sheet.to_excel(*, spaces_replacement: str = ' ', sep: str = ',',
               line_terminator: str = '\n', na_rep: str = '')
```
Parameters are (all optional):

* spaces_replacement (str): All the spaces in the rows and columns descriptions
(labels) are replaced with this string.
* sep (str): Separator of values in a row.
* line_terminator (str): Ending sequence (character) of a row.
* na_rep (str): Replacement for the missing data.


**The return value is:** 

CSV of the values as a string.

#### Exporting to Markdown (MD) format
It can be done using the interface:
```
sheet.to_markdown(*, spaces_replacement: str = ' ', 
                  top_right_corner_text: str = "Sheet", na_rep: str = '')
```
Parameters are (all optional):

* spaces_replacement (str): All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* top_right_corner_text (str): Text in the top right corner.
* na_rep (str): Replacement for the missing data.

**The return value is:** 

Markdown (MD) compatible table of the values as a string.

## Software User Manual (SUM), how to use it?
### Installation
To install the most actual package, use the command:
```
git clone https://github.com/david-salac/Portable-spreadsheet-generator
cd Portable-spreadsheet-generator/
python setup.py install
```

### Demo
The following demo contains a simple example with aggregations.
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
    # III) Mean value
    sheet.iloc[row_idx, 7] = sheet.iloc[row_idx, 0:5].mean()
# Insert the similar to rows:
for col_idx in range(8):
    # I) Values of all
    sheet.iloc[21, col_idx] = sheet.iloc[0:21, col_idx].average()
    # II) Values of boys
    sheet.iloc[22, col_idx] = sheet.iloc[0:11, col_idx].average()
    # III) Values of girls
    sheet.iloc[23, col_idx] = sheet.iloc[11:21, col_idx].average()

# Export results to Excel file, TODO: change the target directory:
sheet.to_excel("OUTPUTS/student_marks.xlsx", sheet_name="Marks")

# Top print table as Markdown
print(sheet.to_markdown())
```

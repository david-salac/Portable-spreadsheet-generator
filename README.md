# Simple Portable Python Spreadsheet Generator
Author: David Salac <http://github.com/david-salac>

Simple spreadsheet that keeps tracks of each operation in defined languages.
Logic allows export sheets to Excel files (and see how each cell is computed),
to the JSON strings with description of computation e. g. in native language.
Other formats like CSV and Markdown (MD) are also supported. It also allows
to reconstruct behaviours in native Python with NumPy.

## Key components of the library
There are five main objects in the library:

1. **_Grammar_**: the set of rule that defines language.
2. **_Cell_**: single cell inside the spreadsheet.
3. **_Word_**: the word describing how the cell is created in each language.
4. **_Spreadsheet_**: a set of cells with a defined shape.
5. **_Cell slice_**: a subset of the spreadsheet. 

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

User can also check what languages are currently available using the
static method `get_languages`:
```
languages_in_the_system: Set[str] = GrammarUtils.get_languages()
```
### Cells
It represents the smallest element in the spreadsheet. Cell encapsulates basic
arithmetic and logical operations that are needed. A cell is represented by
the class of the same name `Cell`. It is highly recommended not to use
this class directly but only through the spreadsheet instance.

Currently, the supported operations are described in the subsections
_Computations_ bellow in this document (as all that unary, binary and other
functions).

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
Cell slice is mainly related to the aggregating functions described in
the subsection _Aggregate functions_ bellow.

There is also a functionality related to setting the values to some
constant or reference to another cell. This functionality should not
be used directly.

Cell slices can be exported in the same way as a whole spreadsheet (methods
are discussed below).

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
sheet = ps.Spreadsheet.create_new_sheet(
    number_of_rows, number_of_columns, [rows_columns]
)
```
if you wish to include some user-defined languages or the language
called 'native' (which is already in the system), you also need to
pass the argument `rows_columns` (that is a dictionary with keys as
languages and values as lists with column names in a given non-system
language).

For example, if you choose to add _'native'_ language (already available in
grammars), you can use a shorter version:
```
sheet = ps.Spreadsheet.create_new_sheet(
    number_of_rows, number_of_columns, 
    {
        "native": cell_indices_generators['native'](number_of_rows, 
                                                    number_of_columns),
    }
)
```

Other (keywords) arguments:
1. `rows_labels (List[str])`: _(optional)_ List of masks (aliases)
for row names.
2. `columns_labels (List[str])`: _(optional)_ List of masks (aliases)
for column names.
3. `rows_help_text (List[str])`: _(optional)_ List of help texts for each row.
4. `columns_help_text (List[str])`: _(optional)_ List of help texts for each
column.
5. `excel_append_labels (bool)`: _(optional)_ If True, one row and
column is added on the beginning of the sheet as an offset for labels.
6. `warning_logger (Callable[[str], None]])`: Function that logs the warnings
(or `None` if logging should be skipped).

First two are the most important because they define labels for the columns
and rows indices. The warnings mention above occurs when the slices are
exported (which can lead to data losses).

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
logic as the parameters of `Spreadsheet.create_new_sheet`.

### Shape of the Spreadsheet object
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

### Variables
Variable represents an imaginary entity that can be used for computation if 
you want to refer to something that is common for the whole spreadsheet. 
Technically it is similar to variables in programming languages.

Variables are encapsulated in the property `var` of the class `Spreadsheet`. 

It provides the following functionality:

1. **Setting the variable**, method `set_variable` with parameters: `name` 
(a lowercase alphanumeric string with underscores), `value` 
(number or string), and `description` (optional) that serves as a help text.
2. **Get the variable dictionary**, property `variables_dict`, returns 
a dictionary with variable names as keys and variable values and descriptions
as values → following the logic: `{'VARIABLE_NAME': {'description':
'String value or None', 'value': 'VALUE'}}`.
3. **Check if the variable exists in a system**, method `variable_exist` with
a parameter `name` representing the name of the variable. 
Return true if the variable exists, false otherwise.
4. **Get the variable as a Cell object**, method `get_variable`, with
parameter `name` (required as positional only) that returns the variable as a
Cell object (for computations in a sheet).
5. **Check if there is any variable in the system**: using the property `empty`
that returns true if there is no variable in the system, false otherwise. 

To get (and set similarly) the variable as a cell object, you can also use
the following approach with square brackets:
```
sheet.iloc[i, j] = sheet.var['VARIABLE_NAME']
```
Same approach can be used for setting the value of variable:
```
sheet.var['VARIABLE_NAME'] = some_value
```
Getting/setting the variables values should be done preferably by this logic.

#### Example
Following example multiply some cell with value of
PI constant stored as a variable `pi`:
```
sheet.set_variable(pi, 3.14159265359)
sheet.iloc[i,j] = sheet.var['pi'] * sheet.iloc[x,y]
```

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
Technically the slice is the instance of `CellSlice` class.

#### Aggregate functions
The slice itself can be used for computations using aggregate functions.

1. **Sum**: return the sum of the cells in the slice. 
    For example: SUM(7, 8, 9) = 25.
    Available as the function `sum` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].sum()`
2. **Product**: return the product of the cells in the slice. 
    For example: PROD(7, 8, 9) = 504.
    Available as the function `product` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].product()`
3. **Minimum**: return the minimum of the cells in the slice. 
    For example: MIN(7, 8, 9) = 7.
    Available as the function `min` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].min()`
4. **Maximum**: return the maximum of the cells in the slice. 
    For example: MAX(7, 8, 9) = 9.
    Available as the function `max` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].max()`
5. **Mean-average**: return the arithmetic mean of the cells in the slice. 
    For example: MEAN(7, 8, 9) = 8.
    Available as the function `mean` and `average` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].mean()` or 
    `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].average()` 
6. **Standard deviation**: return the standard deviation of the cells in the
slice. 
    For example: STDEV(7, 8, 9) = 1.
    Available as the function `stdev` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].stdev()`
7. **Median**: return the median of the cells in the slice. 
    For example: MEDIAN(7, 8, 9) = 8.
    Available as the function `median` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].median()`
7. **Count**: return the number of the cells in the slice. 
    For example: COUNT(7, 8, 9) = 3.
    Available as the function `count` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].count()`

Aggregate functions always return the cell with the result.

### Conditional
There is a support for the conditional statement (aka if-then-else statement).
Functionality is implemented in the property `fn` of the `Spreadsheet`
instance in the method `conditional`. It takes three parameters (positional)
in precisely this order:

1. **Condition**: the cell with a boolean value that is evaluated (typically
achieved using operators ==, !=, >, <, etc.).
2. **Consequent**: the cell that is taken when the condition is evaluated as
true.
3. **Alternative**:  the cell that is taken when the condition is evaluated as
false.

All the parameters are the instance of `Cell` class.

#### Example of conditional
Consider the following example that compares whether two cells are equals,
if yes, it takes some value in a cell, if not, another value in the
different cell:
```
sheet.iloc[i,j] = sheet.fn.conditional(
    # Condition is the first parameter:
    sheet.iloc[1,2] == sheet.iloc[2,2],
    # Consequent (value if condition is true) is the second parameter:
    sheet.iloc[3,1],
    # Alternative (value if condition is false) is the third parameter:
    sheet.iloc[4,1]
)
```

### Offset function
The offset function represents the possibility of reading the value
that is shifted by some number rows left, and some number of columns
down from some referential cells.

It is accessible from the Spreadsheet instance using `fn`
property and `offset` method. Parameters are following (only
positional, in exactly this order):
* **Reference cell**: Reference cell from that the position is computed.
* **Cell defining a number of rows to be skipped**: How many rows (down)
should be skipped.
* **Cell defining a number of columns to be skipped**: How many columns (left)
should be skipped.

#### Example:
Following example assign the value of the cell that is on the third row and 
second column to the cell that is on the second row and second column.
```
sheet.iloc[1,1] = sheet.fn.offset(
    sheet.iloc[0,0], sheet.fn.const(2), sheet.fn.const(1)
)
```

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
There are the following unary operations (in the following the `OPERAND`
is the instance of the Cell class): 

1. **Ceiling function**: returns the ceil of the input value.
    For example ceil(4.1) = 5.
    Available in the `fn` property of the `sheet` object.
    Usage: `sheet.iloc[i,j] = sheet.fn.ceil(OPERAND)`
2. **Floor function**: returns the floor of the input value.
    For example floor(4.1) = 4.
    Available in the `fn` property of the `sheet` object.
    Usage: `sheet.iloc[i,j] = sheet.fn.floor(OPERAND)`
3. **Round function**: returns the round of the input value.
    For example round(4.5) = 5.
    Available in the `fn` property of the `sheet` object.
    Usage: `sheet.iloc[i,j] = sheet.fn.round(OPERAND)`
4. **Absolute value function**: returns the absolute value of the input value.
    For example abs(-4.5) = 4.5.
    Available in the `fn` property of the `sheet` object.
    Usage: `sheet.iloc[i,j] = sheet.fn.abs(OPERAND)`
5. **Square root function**: returns the square root of the input value.
    For example sqrt(16) = 4.
    Available in the `fn` property of the `sheet` object.
    Usage: `sheet.iloc[i,j] = sheet.fn.sqrt(OPERAND)`
6. **Logarithm function**: returns the natural logarithm of the input value.
    For example ln(11) = 2.3978952728.
    Available in the `fn` property of the `sheet` object.
    Usage: `sheet.iloc[i,j] = sheet.fn.ln(OPERAND)`
7. **Exponential function**: returns the exponential of the input value.
    For example exp(1) = _e_ power to 1 = 2.71828182846.
    Available in the `fn` property of the `sheet` object.
    Usage: `sheet.iloc[i,j] = sheet.fn.exp(OPERAND)`
8. **Logical negation**: returns the logical negation of the input value.
    For example neg(false) = true.
    Available as the overloaded operator `~`.
    Usage: `sheet.iloc[i,j] = ~OPERAND`.
    _Also available in the `fn` property of the `sheet` object.
    Usage: `sheet.iloc[i,j] = sheet.fn.neg(OPERAND)`_
    
All unary operators are defined in the `fn` property of the Spreadsheet
object (together with brackets, that works exactly the same - see bellow).

#### Binary operations
There are the following binary operations (in the following the `OPERAND_1`
and `OPERAND_2` are the instances of the Cell class):

1. **Addition**: return the sum of two numbers. 
    For example: 5 + 2 = 7.
    Available as the overloaded operator `+`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 + OPERAND_2`
2. **Subtraction**: return the difference of two numbers. 
    For example: 5 - 2 = 3.
    Available as the overloaded operator `-`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 - OPERAND_2`
3. **Multiplication**: return the product of two numbers. 
    For example: 5 * 2 = 10.
    Available as the overloaded operator `*`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 * OPERAND_2`
4. **Division**: return the quotient of two numbers. 
    For example: 5 / 2 = 2.5.
    Available as the overloaded operator `/`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 / OPERAND_2`
5. **Exponentiation**: return the power of two numbers. 
    For example: 5 ** 2 = 25.
    Available as the overloaded operator `**`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 ** OPERAND_2`
6. **Logical equality**: return true if inputs are equals, false otherwise. 
    For example: 5 = 2 <=> false.
    Available as the overloaded operator `==`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 == OPERAND_2`
7. **Logical inequality**: return true if inputs are not equals,
false otherwise. 
    For example: 5 ≠ 2 <=> true.
    Available as the overloaded operator `!=`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 != OPERAND_2`
8. **Relational greater than operator**: return true if the first operand is
greater than another operand, false otherwise. 
    For example: 5 > 2 <=> true.
    Available as the overloaded operator `>`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 > OPERAND_2`
9. **Relational greater than or equal to operator**: return true if the first
operand is greater than or equal to another operand, false otherwise. 
    For example: 5 ≥ 2 <=> true.
    Available as the overloaded operator `>=`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 >= OPERAND_2`
10. **Relational less than operator**: return true if the first operand is
less than another operand, false otherwise. 
    For example: 5 < 2 <=> false.
    Available as the overloaded operator `<`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 < OPERAND_2`
11. **Relational less than or equal to operator**: return true if the first
operand is less than or equal to another operand, false otherwise. 
    For example: 5 ≤ 2 <=> false.
    Available as the overloaded operator `<=`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 <= OPERAND_2`
12. **Logical conjunction operator**: return true if the first
operand is true and another operand is true, false otherwise. 
    For example: true ∧ false <=> false.
    Available as the overloaded operator `&`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 & OPERAND_2`.
    **_BEWARE that operator `and` IS NOT OVERLOADED! Because it is not
    technically possible._**
13. **Logical disjunction operator**: return true if the first
operand is true or another operand is true, false otherwise. 
    For example: true ∨ false <=> true.
    Available as the overloaded operator `|`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 | OPERAND_2`.
    **_BEWARE that operator `or` IS NOT OVERLOADED! Because it is not
    technically possible._**

Operations can be chained in the string:
```
sheet.iloc[i,j] = OPERAND_1 + OPERAND_2 * OPERAND_3 ** OPERAND_4
```
The priority of the operators is the same as in normal mathematics. If
you need to modify priority, you need to use brackets, for example:
```
sheet.iloc[i,j] = sheet.fn.brackets(OPERAND_1 + OPERAND_2) \
    * OPERAND_3 ** OPERAND_4
```
#### Brackets for computation
Brackets are technically speaking just another unary operator. They are
defined in the `fn` property. They can be used like:
```
sheet.iloc[i,j] = sheet.fn.brackets(OPERAND_1 + OPERAND_2) \ 
    * OPERAND_3 ** OPERAND_4
```
#### Example
For example
```
# Equivalent of: value at [1,0] * (value at [2,1] + value at [3,1]) * exp(9)
sheet.iloc[0,0] = sheet.iloc[1,0] * sheet.fn.brackets(
        sheet.iloc[2,1] + sheet.iloc[3,1]
    ) * sheet.fn.exp(sheet.fn.const(9))
```
### Accessing the computed values
You can access either to the actual numerical value of the cell or to the
word that is created in all the languages. The numerical value is accessible
using the `value` property, whereas the words are accessible using
the `parse` property (it returns a dictionary with languages as keys
and word as values).
```
# Access the value of the cell
value_of_cell: float = sheet.iloc[i, j].value
# Access all the words in the cell
word: dict = sheet.iloc[i, j].parse
# Access the word in language 'lang'
word_in_language_lang = word['lang']
```

### Exporting the results
There are various methods available for exporting the results. All these
methods can be used either to a whole sheet (instance of Spreadsheet)
or to any slice (CellSlice instance):

1. **Excel format**, method `to_excel`:
Export the sheet to the Excel-compatible file.
2. **Dictionary of values**, method `to_dictionary`:
Export the sheet to the dictionary (`dict` type) that can be used for
creating of JSON.
3. **2D array as a string**, method: `to_string_of_values`:
Export values to the string that looks like Python array definition string.
4. **CSV**, method `to_csv`:
Export the values to the CSV compatible string (that can be saved to the file)
5. **Markdown (MD)**, method `to_markdown`:
Export the values to MD (Markdown) file format string.
Defined as a table.
6. **NumPy ndarray**, method `to_numpy`:
Export the sheet as a `numpy.ndarray` object.
7. **Python 2D list**, method `to_2d_list`: 
Export values 2 dimensional Python array (list of the list of the values).
8. **HTML table**, method `to_html_table`:
Export values to HTML table.

#### Description field
There is a possibility to add a description to a cell in the sheet
(or to the whole slice of the sheet). It can be done using the property
`description` on the cell or slice object. It should be done just before
the export is done (together with defining Excel styles, see below)
because once you rewrite the value of the cell on a given location,
the description is lost.

Example of using the description field:
```
# Setting the description of a single cell
sheet.iloc[i, j].description = "Some text describing a cell"
# Seting the description to a slice (propagate its value to each cell)
sheet.iloc[i:j, k:l].description = "Text describing each cell in the slice"
```
#### Exporting to Excel
It can be done using the interface:
```
sheet.to_excel(file_path: str, /, *, sheet_name: str = "Results", 
               spaces_replacement: str = ' ', 
               label_format: dict = {'bold': True})
```
The only required argument is the path to the destination file (positional
only parameter). Other parameters are passed as keywords (non-positional only). 
* `file_path (str)`: Path to the target .xlsx file. (**REQUIRED**, only
positional)
* `sheet_name (str)`: The name of the sheet inside the file.
* `spaces_replacement (str)`: All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* `label_row_format (dict)`: Excel styles for the label of rows,
documentation: https://xlsxwriter.readthedocs.io/format.html
* `label_column_format (dict)`: Excel styles for the label of columns,
documentation: https://xlsxwriter.readthedocs.io/format.html
* `variables_sheet_name (Optional[str])`: If set, creates the new
sheet with variables and their description and possibility
to set them up (directly from the sheet).
* `variables_sheet_header (Dict[str, str])`: Define the labels (header)
for the sheet with variables (first row in the sheet). Dictionary should look
like: `{"name": "Name", "value": "Value", "description": "Description"}`.

##### Setting the format/style for Excel cells
There is a possibility to set the style/format of each cell in the grid
or the slice of the gird using property `excel_format`. Style assignment
should be done just before the export to the file because each new
assignment of values to the cell overrides its style. Format/style can
be set for both slice and single value. 

Example of setting Excel format/style for cells and slices:
```
# Set the format of the cell on the position [i, j] (use bold value)
sheet.iloc[i, j].excel_format = {'bold': True}
# Set the format of the cell slice (use bold value and red color)
sheet.iloc[i:j, k:l].excel_format = {'bold': True, 'color': 'red'}
```

#### Exporting to the dictionary
It can be done using the interface:
```
sheet.to_excel(languages: List[str] = None, /, *, 
               by_row: bool = True,
               languages_pseudonyms: List[str] = None,
               spaces_replacement: str = ' ',
               skip_nan_cell: bool = False)
```
Parameters are (all optional):

* `languages (List[str])`: List of languages that should be exported.
* `by_row (bool)`: If True, rows are the first indices and columns are the
second in the order. If False it is vice-versa.
* `languages_pseudonyms (List[str])`: Rename languages to the strings inside
this list.
* `spaces_replacement (str)`: All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* `skip_nan_cell (bool)`: If true, `None` (NaN, empty cells) values are
skipped, default value is false (NaN values are included).
* `nan_replacement (object)`: Replacement for the `None` (NaN) value

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

* `spaces_replacement (str)`: All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* `sep (str)`: Separator of values in a row.
* `line_terminator (str)`: Ending sequence (character) of a row.
* `na_rep (str)`: Replacement for the missing data.

**The return value is:** 

CSV of the values as a string.

#### Exporting to Markdown (MD) format
It can be done using the interface:
```
sheet.to_markdown(*, spaces_replacement: str = ' ', 
                  top_right_corner_text: str = "Sheet", na_rep: str = '')
```
Parameters are (all optional):

* `spaces_replacement (str)`: All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* `top_right_corner_text (str)`: Text in the top right corner.
* `na_rep (str)`: Replacement for the missing data.

**The return value is:** 

Markdown (MD) compatible table of the values as a string.

#### Exporting to HTML table format
It can be done using the interface:
```
sheet.to_html_table(*,
                    spaces_replacement: str = ' ',
                    top_right_corner_text: str = "Sheet",
                    na_rep: str = '',
                    language_for_description: str = None)
```
Parameters are (all optional):

* `spaces_replacement (str)`: All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* `top_right_corner_text (str)`: Text in the top right corner.
* `na_rep (str)`: Replacement for the missing data.
* `language_for_description (str)`: If not `None`, the description
of each computational cell is inserted as word of this language
(if the property description is not set).

**The return value is:** 

HTML table of the values as a string. Table is usable mainly for debugging
purposes.

## Remarks and definitions
* **Anchored cell** is a cell that is located in the sheet and can be
accessed using position.
* **Un-anchored cell** is a cell that is the result of some computation or
a constant defined by the user for some computation (and does not have
any position in the sheet grid yet).

**Example:**
```
anchored_cell = sheet.iloc[4,2]
unanchored_cell_1 = sheet.iloc[4,2] * sheet.iloc[5,2]
unanchored_cell_2 = sheet.fn.const(9)
```


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

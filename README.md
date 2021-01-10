# Simple Portable Python Spreadsheet Generator
Author: David Salac <https://github.com/david-salac>

Project: Portable Spreadsheet <https://portable-spreadsheet.com/>

A simple spreadsheet that keeps tracks of each operation of each cell
in defined languages. Logic allows exporting sheets to Excel files (and
see how each cell is computed), to the JSON strings with a description
of computation of each cell (e. g. in the native language). Other
formats, like HTML, CSV and Markdown (MD), are also implemented (user
can define own format). It also allows reconstructing behaviours in
native Python with NumPy. The sheets can be easily created and handled
in a way similar to Pandas DataFrame.

## Key components of the library
There are five main objects in the library:

1. **_Grammar_**: the set of rule that defines language.
2. **_Cell_**: single cell inside the spreadsheet.
3. **_Word_**: the word describing how the cell is created in each language.
4. **_Sheet_**: a set of cells with a defined shape.
5. **_Cell slice_**: a subset of the spreadsheet. 
6. **_Work book_**: a set of multiple sheets.

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
```python
is_valid: bool = GrammarUtils.validate_grammar(grammar)
```
To add the grammar describing some language (in the variable `language`)
to the system (in the variable `grammar`) use: 
```python
GrammarUtils.add_grammar(grammar, language)
```

User can also check what languages are currently available using the
static method `get_languages`:
```python
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
```python
B2*(C1+C2)
```
The equivalent word in the language Python:
```python
values[1,1]*(values[0,2]+values[1,2])
```
Words are constructed using prefixes and suffixes defined by the grammar.
Each language also has some special features that are also described in
the grammar (like whether the first index represents column or a row).

Words are important later when the output is exported to some file in given
format or to JSON.
Operations with words (and word as a data structure) are located in the
class `WordConstructor`. It should not be used directly.

### Sheet class
The Sheet is the most important class of the whole package. It is
located in the file `spreadsheet.py`. It encapsulates the functionality
related to accessing cells and modifying them as well as the functionality
for exporting of the computed results to various formats.

Class is strongly motivated by the API of the Pandas DataFrame. 

The functionality of Sheet class is documented in a special section below.

### Cell slice
Represents the special object that is created when some part slice of the
spreadsheet is created. Basically, it encapsulates the set of cells and
aggregating operations (sum, product, minimum, maximum, average). For example:
```python
some_slice = spreadsheet_instance.iloc[1,:]
average_of_slice = some_slice.mean()
```
selected the second row in the spreadsheet and compute the average (mean)
of values in the slice.

Cell slice is represented in the class `CellSlice` in the
file `cell_slice.py`.

If you want to assign some value to a `CellSlice` object, you can use
overloaded operator `<<=`
```python
some_slice = spreadsheet_instance.iloc[1,:]
average_of_slice <<= 55.6  # Some assigned value
```
However, it is strongly recommended to use standard assigning through
the Sheet object described below.

#### Functionality of the CellSlice class
Cell slice is mainly related to the aggregating functions described in
the subsection _Aggregate functions_ bellow.

There is also a functionality related to setting the values to some
constant or reference to another cell. This functionality should not
be used directly.

Cell slices can be exported in the same way as a whole spreadsheet (methods
are discussed below).

## Sheet functionality
All following examples expect that user has already imported package.
```python
import portable_spreadsheet as ps
```
The default (or system) languages are Excel and Python. There is also
a language called 'native' ready to be used.

### How to create a spreadsheet
The easiest function is to use the built-in static method `create_new_sheet`:

```python
sheet = ps.Sheet.create_new_sheet(
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

```python
sheet = ps.Sheet.create_new_sheet(
    number_of_rows, number_of_columns,
    {
        "native": cell_indices_generators['native'](number_of_rows,
                                                    number_of_columns),
    },
    name='Sheet Name'
)
```

Other (keywords) arguments:
1. `name (str)`: Name of the sheet.
2. `rows_labels (List[Union[str, SkippedLabel]])`: _(optional)_ List of masks
(aliases) for row names.
3. `columns_labels (List[Union[str, SkippedLabel]])`: _(optional)_ List of
masks (aliases) for column names. If the instance of SkippedLabel is
used, the export skips this label.
4. `rows_help_text (List[str])`: _(optional)_ List of help texts for each row.
5. `columns_help_text (List[str])`: _(optional)_ List of help texts for each
column. If the instance of SkippedLabel is used, the export skips this label.
6. `excel_append_row_labels (bool)`: _(optional)_ If True, one column is added
on the beginning of the sheet as a offset for labels.
7. `excel_append_column_labels (bool)`: _(optional)_ If True, one row is
added on the beginning of the sheet as a offset for labels.
8. `warning_logger (Callable[[str], None]])`: Function that logs the warnings
(or `None` if logging should be skipped).

First two are the most important because they define labels for the columns
and rows indices. The warnings mention above occurs when the slices are
exported (which can lead to data losses).

#### How to change the size of the spreadsheet
You can only expand the size of the spreadsheet (it's because of the
built-in behaviour of language construction). We, however, strongly recommend
not to do so. Simplified logic looks like:
```python
# Append 7 rows and 8 columns to existing sheet:
sheet.expand(
    7, 8,  
    {
        "native": ([...], [...])  # Fill 8 new values for rows, columns here
    }
)
```
Parameters of the `Sheet.expand` method are of the same
logic and order as the parameters of `Sheet.create_new_sheet`.

### Column and row labels
Labels are set once when a sheet is created (or expanded in size). If you
want to read them as a tuple of labels, you can use the following properties:

* `columns`: property that returns labels of columns as a tuple of strings.
It can be called on both slices or directly on `Sheet` class instances.
* `index`: property that returns the labels of rows as a tuple of strings.
It can be called on both slices or directly on `Sheet` class instances.

Example:
```python
column_labels: Tuple[str] = sheet.columns  # Get the column labels
row_labels: Tuple[str] = sheet.index  # Get the row labels
```

### Shape of the Sheet object
If you want to know what is the actual size of the spreadsheet, you can
use the property `shape` that behaves as in Pandas. It returns you the
tuple with a number of rows and number of columns (on the second position).

### Accessing/setting the cells in the spreadsheet
You to access the value in the position you can use either the integer
position (indexed from 0) or the label of the row/column.
```python
# Returns the value at second row and third column:
value = sheet.iloc[1,2]
# Returns the value by the name of the row, column
value = sheet.loc['super the label of row', 'even better label of column']
```
As you can see, there are build-in properties `loc` and `iloc` for accessing
the values (the `loc` access based on the label, and `iloc` access the cell
based on the integer position).

The same logic can be used for setting-up the values:
```python
# Set the value at second row and third column:
sheet.iloc[1,2] = value
# Set the value by the name of the row, column
sheet.loc['super the label of row', 'even better label of column'] = value
```
where the variable `value` can be either some constant (string, float or
created by the `fn` method described below) or the result of some
operations with cells:
```python
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

Variables are encapsulated in the property `var` of the class `Sheet`. 

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
```python
sheet.iloc[i, j] = sheet.var['VARIABLE_NAME']
```
Same approach can be used for setting the value of variable:
```python
sheet.var['VARIABLE_NAME'] = some_value
```
Getting/setting the variables values should be done preferably by this logic.

For defining Excel format/style of the variable value, use the attribute
`excel_format` of the `var` property in the following logic:
```python
sheet.var['VARIABLE_NAME'].excel_format = {'num_format': '#,##0'} 
```

#### Example
Following example multiply some cell with value of
PI constant stored as a variable `pi`:
```python
sheet.set_variable(pi, 3.14159265359)
sheet.iloc[i,j] = sheet.var['pi'] * sheet.iloc[x,y]
```

### Working with slices
Similarly, like in NumPy or Pandas DataFrame, there is a possibility
how to work with slices (e. g. if you want to select a whole row, column
or set of rows and columns). Following code, select the third column:
```python
sheet.iloc[:,2]
```
On the other hand
```python
sheet.loc[:,'Handy column']
``` 
selects all the rows in the columns with the label _'Handy column'_. 

You can again set the values in the slice to some constant, or the array
of constants, or to another cell, or to the result of some computation.
```python
sheet.iloc[:,2] = constant  # Constant (float, string)
sheet.iloc[:,2] = sheet.iloc[1,3] + sheet.iloc[1,4]  # Computation result
sheet.iloc[:,2] = sheet.iloc[1,3]  # Just a reference to a cell
```
Technically the slice is the instance of `CellSlice` class.

There are two ways how to slice, either using `.loc` or `.iloc` attribute.
Where `iloc` uses integer position and `loc` uses label of the position
(as a string).

By default the right-most value is excluded when defining slices. If you want
to use right-most value indexing, use one of the methods described below.

#### Slicing using method (with the right-most value included option)
Sometimes, it is quite helpful to use a slice that includes the right-most
value. There are two functions for this purpose:
1. `sheet.iloc.get_slice(ROW_INDEX, COLUMN_INDEX, include_right=[True/False])`:
This way is equivalent to the one presented above with square brackets `[]`.
The difference is the key-value attribute `include_right` that enables the
possibility of including the right-most value of the slice (default value is
False). If you want to use slice as your index, you need to pass some `slice`
object to one (or both) of the indices. For example: 
`sheet.iloc.get_slice(slice(0, 7), 3, include_right=True])` selects first nine
rows (because 8th row - right-most one - is included) from the fourth column
of the sheet _(remember, all is indexed from zero)_.

2. `sheet.iloc.set_slice(ROW_INDEX, COLUMN_INDEX, VALUE, 
include_right=[True/False])`: this command set slice to _VALUE_ in the similar
logic as when you call `get_slice` method (see the first point).

There are again two possibilities, either to use `iloc` with integer position
or to use `loc` with labels.

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
8. **Count**: return the number of the cells in the slice. 
    For example: COUNT(7, 8, 9) = 3.
    Available as the function `count` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].count()`
9. **IRR**: return the Internal Rate of Return (IRR) of the cells in the slice. 
    For example: IRR(-100, 0, 0, 74) = -0.0955.
    Available as the function `irr` called on the slice object.
    Usage: `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].irr()`
10. **Match negative before positive**: return the position of the last
    negative number in a series of negative numbers in the row or column
    series.
    For example:
    MNBP(-100, -90, -80, 5, -500) = 3 _(equals to position of the number -80)_.
    Available as the function `match_negative_before_positive` called on the
    slice object.
    Usage:
    `sheet.iloc[i,j] = sheet.iloc[p:q,x:y].match_negative_before_positive()`

Aggregate functions always return the cell with the result.

All aggregate functions have parameters:

1. `skip_none_cell (bool)`: If true, skips all the cells with `None` as
a value (and does not raise an exception), if false an exception is raised
if the slice contains a cell with `None` value (empty cell).

### Conditional
There is a support for the conditional statement (aka if-then-else statement).
Functionality is implemented in the property `fn` of the `Sheet`
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
```python
sheet.iloc[i,j] = sheet.fn.conditional(
    # Condition is the first parameter:
    sheet.iloc[1,2] == sheet.iloc[2,2],
    # Consequent (value if condition is true) is the second parameter:
    sheet.iloc[3,1],
    # Alternative (value if condition is false) is the third parameter:
    sheet.iloc[4,1]
)
```

### Raw statement
The raw statement represents the extreme way how to set-up value and
computation string of the cell. It should be used only to circumvent
issues with missing or defective functionality.

The raw statement is accessible using `fn` property of the Sheet class
object.

The raw statement should never be used unless you really have to.

#### Example of raw statement
Consider that you need to compute an arccosine value of some cell:
```python
sheet.iloc[i,j] = sheet.fn.raw(
    # Value that should be used as the result (as a Cell instance):
    sheet.fn.const(numpy.arccos(0.7)),
    # Definition of words in each language:
    {
        'python_numpy': "numpy.arccos(0.7)",
        'excel': "ACOS(0.7)"
        # Potentialy some other languages, like 'native', etc.
    }
)
```

### Offset function
The offset function represents the possibility of reading the value
that is shifted by some number rows left, and some number of columns
down from some referential cells.

It is accessible from the Sheet instance using `fn`
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
```python
sheet.iloc[1,1] = sheet.fn.offset(
    sheet.iloc[0,0], sheet.fn.const(2), sheet.fn.const(1)
)
```

### Computations
All operations have to be done using the objects of type Cell. 

#### Constants
If you want to use a constant value, you need to create an un-anchored cell
with this value. The easiest way of doing so is:
```python
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
9. **Signum function**: returns the signum of the input value.
    For example sign(-4.5) = -1, sign(5) = 1, sign(0) = 0.
    Available in the `fn` property of the `sheet` object.
    Usage: `sheet.iloc[i,j] = sheet.fn.sign(OPERAND)`
    
All unary operators are defined in the `fn` property of the Sheet
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
14. **Concatenate strings**: return string concatenation of inputs.
    For example: CONCATENATE(7, "Hello") <=> "7Hello".
    Available as the overloaded operator `<<`.
    Usage: `sheet.iloc[i,j] = OPERAND_1 << OPERAND_2`

Operations can be chained in the string:
```python
sheet.iloc[i,j] = OPERAND_1 + OPERAND_2 * OPERAND_3 ** OPERAND_4
```
The priority of the operators is the same as in normal mathematics. If
you need to modify priority, you need to use brackets, for example:
```python
sheet.iloc[i,j] = sheet.fn.brackets(OPERAND_1 + OPERAND_2) \
    * OPERAND_3 ** OPERAND_4
```
#### Brackets for computation
Brackets are technically speaking just another unary operator. They are
defined in the `fn` property. They can be used like:
```python
sheet.iloc[i,j] = sheet.fn.brackets(OPERAND_1 + OPERAND_2) \ 
    * OPERAND_3 ** OPERAND_4
```
#### Example
For example
```python
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
```python
# Access the value of the cell
value_of_cell: float = sheet.iloc[i, j].value
# Access all the words in the cell
word: dict = sheet.iloc[i, j].parse
# Access the word in language 'lang'
word_in_language_lang = word['lang']
```

### Exporting the results
There are various methods available for exporting the results. All these
methods can be used either to a whole sheet (instance of Sheet)
or to any slice (CellSlice instance):

1. **Excel format**, method `to_excel`:
Export the sheet to the Excel-compatible file.
2. **Dictionary of values**, method `to_dictionary`:
Export the sheet to the dictionary (`dict` type).
3. **JSON format**, method `to_json`:
Export the sheet to the JSON format (serialize output of `to_dictionary`).
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
```python
# Setting the description of a single cell
sheet.iloc[i, j].description = "Some text describing a cell"
# Seting the description to a slice (propagate its value to each cell)
sheet.iloc[i:j, k:l].description = "Text describing each cell in the slice"
```
#### Exporting to Excel
It can be done using the interface:
```python
sheet.to_excel(
    file_path: str,
    /, *,
    spaces_replacement: str = ' ',
    label_row_format: dict = {'bold': True},
    label_column_format: dict = {'bold': True},
    variables_sheet_name: Optional[str] = None,
    variables_sheet_header: Dict[str, str] = MappingProxyType(
    {
        "name": "Name",
        "value": "Value",
        "description": "Description"
    }),
    values_only: bool = False,
    skipped_label_replacement: str = '',
    row_height: List[float] = [],
    column_width: List[float] = [],
    top_left_corner_text: str = ""
)
```
The only required argument is the path to the destination file (positional
only parameter). Other parameters are passed as keywords (non-positional only). 
* `file_path (str)`: Path to the target .xlsx file. (**REQUIRED**, only
positional)
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
* `values_only (bool)`: If true, only values (and not formulas) are
exported.
* `skipped_label_replacement (str)`: Replacement for the SkippedLabel
instances.
* `row_height (List[float])`: List of row heights, or empty for the
default height (or `None` for default height in the series).
If row labels are included, there is a label row height on the
first position in array.
* `column_width (List[float])`: List of column widths, or empty for the
default widths (or `None` for the default width in the series).
If column labels are included, there is a label column width
on the first position in array.
* `top_left_corner_text (str)`: Text in the top left corner. Apply
only when the row and column labels are included.

##### Setting the format/style for Excel cells
There is a possibility to set the style/format of each cell in the grid
or the slice of the gird using property `excel_format`. Style assignment
should be done just before the export to the file because each new
assignment of values to the cell overrides its style. Format/style can
be set for both slice and single value. 

Example of setting Excel format/style for cells and slices:
```python
# Set the format of the cell on the position [i, j] (use bold value)
sheet.iloc[i, j].excel_format = {'bold': True}
# Set the format of the cell slice (use bold value and red color)
sheet.iloc[i:j, k:l].excel_format = {'bold': True, 'color': 'red'}
```
##### Appending to existing Excel file
Appending to existing Excel (`.xlsx`) format **is currently not supported** due
to the missing functionality of the package XlsxWriter on which this
library relies.

#### Exporting to the dictionary (and JSON)
It can be done using the interface:
```python
sheet.to_dictionary(languages: List[str] = None,
                    use_language_for_description: Optional[str] = None, 
                    /, *, 
                    by_row: bool = True,
                    languages_pseudonyms: List[str] = None,
                    spaces_replacement: str = ' ',
                    skip_nan_cell: bool = False,
                    nan_replacement: object = None,
                    append_dict: dict = {})
```
**Parameters are (all optional):**

_Positional only:_
* `languages (List[str])`: List of languages that should be exported.
* `use_language_for_description (Optional[str])`: If set-up (using the language
name), description field is set to be either the description value 
(if defined) or the value of this language. 

_Key-value only:_
* `by_row (bool)`: If True, rows are the first indices and columns are the
second in the order. If False it is vice-versa.
* `languages_pseudonyms (List[str])`: Rename languages to the strings inside
this list.
* `spaces_replacement (str)`: All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* `skip_nan_cell (bool)`: If true, `None` (NaN, empty cells) values are
skipped, default value is false (NaN values are included).
* `nan_replacement (object)`: Replacement for the `None` (NaN) value.
* `error_replacement (object)`: Replacement for the error value.
* `append_dict (dict)`: Append this dictionary to output.
* `generate_schema (bool)`: If true, returns the JSON schema.

All the rows and columns with labels that are instances of SkippedLabel are
entirely skipped. 

**The return value is:** 

Dictionary with keys: 1. column/row, 2. row/column, 3. language or
language pseudonym or 'value' keyword for values -> value as a value or
as a cell building string.

##### Exporting to JSON
Exporting to JSON string is available using `to_json` method with exactly the
same interface. The return value is the string.

The reason why this method is separate is because of some values inserted
from NumPy arrays cannot be serialized using native serializer.

To get JSON schema you can use either `generate_schema (bool)` parameter or
directly use static method `generate_json_schema` of the `Sheet` class.

##### Output example
Output of the JSON format
```json
{
   "table":{
      "data":{
         "rows":{
            "R_0":{
               "columns":{
                  "NL_C_0":{
                     "excel":"1",
                     "python_numpy":"1",
                     "native":"1",
                     "value":1,
                     "description":"DescFor0,0"
                  },
                  "NL_C_1":{
                     "excel":"2",
                     "python_numpy":"2",
                     "native":"2",
                     "value":2,
                     "description":"DescFor0,1"
                  },
                  "NL_C_2":{
                     "excel":"3",
                     "python_numpy":"3",
                     "native":"3",
                     "value":3,
                     "description":"DescFor0,2"
                  },
                  "NL_C_3":{
                     "excel":"4",
                     "python_numpy":"4",
                     "native":"4",
                     "value":4,
                     "description":"DescFor0,3"
                  }
               }
            },
            "R_1":{
               "columns":{
                  "NL_C_0":{
                     "excel":"5",
                     "python_numpy":"5",
                     "native":"5",
                     "value":5,
                     "description":"DescFor1,0"
                  },
                  "NL_C_1":{
                     "excel":"6",
                     "python_numpy":"6",
                     "native":"6",
                     "value":6,
                     "description":"DescFor1,1"
                  },
                  "NL_C_2":{
                     "excel":"7",
                     "python_numpy":"7",
                     "native":"7",
                     "value":7,
                     "description":"DescFor1,2"
                  },
                  "NL_C_3":{
                     "excel":"8",
                     "python_numpy":"8",
                     "native":"8",
                     "value":8,
                     "description":"DescFor1,3"
                  }
               }
            },
            "R_2":{
               "columns":{
                  "NL_C_0":{
                     "excel":"9",
                     "python_numpy":"9",
                     "native":"9",
                     "value":9,
                     "description":"DescFor2,0"
                  },
                  "NL_C_1":{
                     "excel":"10",
                     "python_numpy":"10",
                     "native":"10",
                     "value":10,
                     "description":"DescFor2,1"
                  },
                  "NL_C_2":{
                     "excel":"11",
                     "python_numpy":"11",
                     "native":"11",
                     "value":11,
                     "description":"DescFor2,2"
                  },
                  "NL_C_3":{
                     "excel":"12",
                     "python_numpy":"12",
                     "native":"12",
                     "value":12,
                     "description":"DescFor2,3"
                  }
               }
            },
            "R_3":{
               "columns":{
                  "NL_C_0":{
                     "excel":"13",
                     "python_numpy":"13",
                     "native":"13",
                     "value":13,
                     "description":"DescFor3,0"
                  },
                  "NL_C_1":{
                     "excel":"14",
                     "python_numpy":"14",
                     "native":"14",
                     "value":14,
                     "description":"DescFor3,1"
                  },
                  "NL_C_2":{
                     "excel":"15",
                     "python_numpy":"15",
                     "native":"15",
                     "value":15,
                     "description":"DescFor3,2"
                  },
                  "NL_C_3":{
                     "excel":"16",
                     "python_numpy":"16",
                     "native":"16",
                     "value":16,
                     "description":"DescFor3,3"
                  }
               }
            },
            "R_4":{
               "columns":{
                  "NL_C_0":{
                     "excel":"17",
                     "python_numpy":"17",
                     "native":"17",
                     "value":17,
                     "description":"DescFor4,0"
                  },
                  "NL_C_1":{
                     "excel":"18",
                     "python_numpy":"18",
                     "native":"18",
                     "value":18,
                     "description":"DescFor4,1"
                  },
                  "NL_C_2":{
                     "excel":"19",
                     "python_numpy":"19",
                     "native":"19",
                     "value":19,
                     "description":"DescFor4,2"
                  },
                  "NL_C_3":{
                     "excel":"20",
                     "python_numpy":"20",
                     "native":"20",
                     "value":20,
                     "description":"DescFor4,3"
                  }
               }
            }
         }
      },
      "variables":{

      },
      "rows":[
         {
            "name":"R_0",
            "description":"HT_R_0"
         },
         {
            "name":"R_1",
            "description":"HT_R_1"
         },
         {
            "name":"R_2",
            "description":"HT_R_2"
         },
         {
            "name":"R_3",
            "description":"HT_R_3"
         },
         {
            "name":"R_4",
            "description":"HT_R_4"
         }
      ],
      "columns":[
         {
            "name":"NL_C_0",
            "description":"HT_C_0"
         },
         {
            "name":"NL_C_1",
            "description":"HT_C_1"
         },
         {
            "name":"NL_C_2",
            "description":"HT_C_2"
         },
         {
            "name":"NL_C_3",
            "description":"HT_C_3"
         }
      ]
   }
}
```

#### Exporting to the CSV
It can be done using the interface:
```python
sheet.to_csv(*,
    language: Optional[str] = None,
    spaces_replacement: str = ' ',
    top_left_corner_text: str = "Sheet",
    sep: str = ',',
    line_terminator: str = '\n',
    na_rep: str = '',
    skip_labels: bool = False,
    skipped_label_replacement: str = ''
) -> str
```
Parameters are (all optional and key-value only):

* `language (Optional[str])`: If set-up, export the word in this
language in each cell instead of values.
* `spaces_replacement (str)`: All the spaces in the rows and columns
 descriptions (labels) are replaced with this string.
* `top_left_corner_text (str)`: Text in the top left corner.
* `sep (str)`: Separator of values in a row.
* `line_terminator (str)`: Ending sequence (character) of a row.
* `na_rep (str)`: Replacement for the missing data.
* `skip_labels (bool)`: If true, first row and column with labels is
 skipped
* `skipped_label_replacement (str)`: Replacement for the SkippedLabel
instances.

**The return value is:** 

CSV of the values as a string.

##### Output example
```text
Sheet,NL_C_0,NL_C_1,NL_C_2,NL_C_3
R_0,1,2,3,4
R_1,5,6,7,8
R_2,9,10,11,12
R_3,13,14,15,16
R_4,17,18,19,20
```

#### Exporting to Markdown (MD) format
It can be done using the interface:
```python
sheet.to_markdown(*,
    language: Optional[str] = None,
    spaces_replacement: str = ' ',
    top_left_corner_text: str = "Sheet",
    na_rep: str = '',
    skip_labels: bool = False,
    skipped_label_replacement: str = ''
)
```
Parameters are (all optional, all key-value only):

* `language (Optional[str])`: If set-up, export the word in this
language in each cell instead of values.
* `spaces_replacement (str)`: All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* `top_left_corner_text (str)`: Text in the top left corner.
* `na_rep (str)`: Replacement for the missing data.
* `skip_labels (bool)`: If true, first row and column with labels is
skipped
* `skipped_label_replacement (str)`: Replacement for the SkippedLabel
instances.
                
**The return value is:** 

Markdown (MD) compatible table of the values as a string.

##### Output example
```markdown
| Sheet |*NL_C_0* | *NL_C_1* | *NL_C_2* | *NL_C_3* |
|----|----|----|----|----|
| *R_0* | 1 | 2 | 3 | 4 |
| *R_1* | 5 | 6 | 7 | 8 |
| *R_2* | 9 | 10 | 11 | 12 |
| *R_3* | 13 | 14 | 15 | 16 |
| *R_4* | 17 | 18 | 19 | 20 |
```

#### Exporting to HTML table format
It can be done using the interface:
```python
sheet.to_html_table(*,
    spaces_replacement: str = ' ',
    top_left_corner_text: str = "Sheet",
    na_rep: str = '',
    language_for_description: str = None,
    skip_labels: bool = False,
    skipped_label_replacement: str = ''
)
```
Parameters are (all optional, all key-value only):

* `spaces_replacement (str)`: All the spaces in the rows and columns
descriptions (labels) are replaced with this string.
* `top_left_corner_text (str)`: Text in the top left corner.
* `na_rep (str)`: Replacement for the missing data.
* `language_for_description (str)`: If not `None`, the description
of each computational cell is inserted as word of this language
(if the property description is not set).
* `skip_labels (bool)`: If true, first row and column with labels is
skipped
* `skipped_label_replacement (str)`: Replacement for the SkippedLabel
instances.

**The return value is:** 

HTML table of the values as a string. Table is usable mainly for debugging
purposes.

##### Output example
```html
<table>
   <tr>
      <th>Sheet</th>
      <th><a href="javascript:;"  title="HT_C_0">NL_C_0</a></th>
      <th><a href="javascript:;"  title="HT_C_1">NL_C_1</a></th>
      <th><a href="javascript:;"  title="HT_C_2">NL_C_2</a></th>
      <th><a href="javascript:;"  title="HT_C_3">NL_C_3</a></th>
   </tr>
   <tr>
      <td><a href="javascript:;"  title="HT_R_0">R_0</a></td>
      <td><a href="javascript:;"  title="DescFor0,0">1</a></td>
      <td><a href="javascript:;"  title="DescFor0,1">2</a></td>
      <td><a href="javascript:;"  title="DescFor0,2">3</a></td>
      <td><a href="javascript:;"  title="DescFor0,3">4</a></td>
   </tr>
   <tr>
      <td><a href="javascript:;"  title="HT_R_1">R_1</a></td>
      <td><a href="javascript:;"  title="DescFor1,0">5</a></td>
      <td><a href="javascript:;"  title="DescFor1,1">6</a></td>
      <td><a href="javascript:;"  title="DescFor1,2">7</a></td>
      <td><a href="javascript:;"  title="DescFor1,3">8</a></td>
   </tr>
   <tr>
      <td><a href="javascript:;"  title="HT_R_2">R_2</a></td>
      <td><a href="javascript:;"  title="DescFor2,0">9</a></td>
      <td><a href="javascript:;"  title="DescFor2,1">10</a></td>
      <td><a href="javascript:;"  title="DescFor2,2">11</a></td>
      <td><a href="javascript:;"  title="DescFor2,3">12</a></td>
   </tr>
   <tr>
      <td><a href="javascript:;"  title="HT_R_3">R_3</a></td>
      <td><a href="javascript:;"  title="DescFor3,0">13</a></td>
      <td><a href="javascript:;"  title="DescFor3,1">14</a></td>
      <td><a href="javascript:;"  title="DescFor3,2">15</a></td>
      <td><a href="javascript:;"  title="DescFor3,3">16</a></td>
   </tr>
   <tr>
      <td><a href="javascript:;"  title="HT_R_4">R_4</a></td>
      <td><a href="javascript:;"  title="DescFor4,0">17</a></td>
      <td><a href="javascript:;"  title="DescFor4,1">18</a></td>
      <td><a href="javascript:;"  title="DescFor4,2">19</a></td>
      <td><a href="javascript:;"  title="DescFor4,3">20</a></td>
   </tr>
</table>
```

## Remarks and definitions
* **Anchored cell** is a cell that is located in the sheet and can be
accessed using position.
* **Un-anchored cell** is a cell that is the result of some computation or
a constant defined by the user for some computation (and does not have
any position in the sheet grid yet).

**Example:**
```python
anchored_cell = sheet.iloc[4,2]
unanchored_cell_1 = sheet.iloc[4,2] * sheet.iloc[5,2]
unanchored_cell_2 = sheet.fn.const(9)
```

## Software User Manual (SUM), how to use it?
### Installation
To install the most actual package, use the command:
```commandline
git clone https://github.com/david-salac/Portable-spreadsheet-generator
cd Portable-spreadsheet-generator/
python setup.py install
```
or simply install using PIP:
```commandline
pip install portable-spreadsheet
```
#### Running of the unit-tests
For running package unit-tests, use command:
```commandline
python setup.py test
```
In order to run package unit-tests you need to clone package first.
### Demo
The following demo contains a simple example with aggregations.

```python
import portable_spreadsheet as ps
import numpy as np

# This is a simple demo that represents the possibilities of the package
#   The purpose of this demo is to create a class rooms and monitor students

sheet = ps.Sheet.create_new_sheet(
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

## Multiple sheets
If you need to have an application that uses multiple sheets
simultaneously - there is a special class for these purposes
called WorkBook. It allows you to create multiple sheets, have
references from one sheet to another and export to various formats.

### Creation of the WorkBook
To create a new workbook, you need to have all sheets prepared. The
constructor accepts just a list of all sheets (Sheet instance).
```python
def __init__(self, *sheets: Iterable[Sheet])
```

### Special sheet for variables
There is a way how to create a customized sheet for variables. 
To do so, use the function `create_variable_sheet`. It
has the following syntax:
```python
def create_variable_sheet(self,
                          *,
                          nr_rows_prefix: int = 0,
                          nr_rows_suffix: int = 0,
                          nr_columns_prefix: int = 0,
                          nr_columns_suffix: int = 0,
                          sheet_name: str = "config",
                          position: int = 0
                          ) -> Sheet
```
parameters have the following logic:
 * `nr_rows_prefix (int)`: defines the number of rows that are prefix
for variables definition segment.
 * `nr_rows_suffix (int)`: defines the number of rows that are suffix
for variables definition segment.
 * `nr_columns_prefix (int)`: defines the number of columns that are
prefix for variables definition segment.
 * `nr_columns_suffix (int)`: defines the number of columns that are
suffix for variables definition segment.
 * `sheet_name (str)`: Name of the sheet for variables.
 * `position (int)`: Relative position in the workbook (indexed from 0).

### Exporting to Excel (xlsx) format
For exporting to Excel (.xlsx) format, there is a function called
`to_excel`. It takes two parameters. The first one is the path to
the file; another is the set of parameters for exporting each sheet.
```python
def to_excel(self,
             file_path: Union[str, pathlib.Path],
             /, *,  # noqa: E225
             export_parameters: Tuple[ExcelParameters]
             ) -> None
```
the first parameter is always positional; another is keyword type.

Data class `ExcelParameters` has the structure motivated by the
parameters required by `Sheet.to_excel`:
```python
class ExcelParameters(ClassVarsToDict):
    spaces_replacement: str = ' '
    label_row_format: dict = MappingProxyType({'bold': True})
    label_column_format: dict = MappingProxyType({'bold': True})
    values_only: bool = False
    skipped_label_replacement: str = ''
    row_height: Tuple[float] = tuple([])
    column_width: Tuple[float] = tuple([])
    top_left_corner_text: str = ""
```

### Exporting to dictionary
It is possible to export sheets to the dictionary
by using `to_dictionary` function:
```python
def to_dictionary(self,
                  *,
                  export_parameters: Tuple[DictionaryParameters]
                  ) -> dict:
```
the second parameter is keyword type.

Data class `DictionaryParameters` has the structure motivated by the
parameters required by `Sheet.to_dictionary`:
```python
class DictionaryParameters(ClassVarsToDict):
    languages: List[str] = None
    use_language_for_description: Optional[str] = None
    by_row: bool = True
    languages_pseudonyms: List[str] = None
    spaces_replacement: str = ' '
    skip_nan_cell: bool = False
    nan_replacement: object = None
    error_replacement: object = None
    append_dict: dict = MappingProxyType({})
    generate_schema: bool = False
```

### Export to JSON
Exporting to JSON has the same logic as exporting to dictionary.
```python
def to_json(self,
            *,
            export_parameters: Tuple[DictionaryParameters]) -> str:
```
The logic is the same as above.

The JSON schema can be generated using the static `generate_json_schema`
function.

### Export to list
It is possible to export sheets to the 3D list
by using `to_list` function:
```python
def to_list(self,
            *,
            export_parameters: Tuple[ListParameters]) -> list:
```
the second parameter is keyword type.

Data class `ListParameters` has the structure motivated by the
parameters required by `Sheet.to_list`:
```python
class ListParameters(ClassVarsToDict):
    language: Optional[str] = None
    skip_labels: bool = False
    na_rep: Optional[object] = None
    spaces_replacement: str = ' '
    skipped_label_replacement: str = ''
```

### Export to string
There is a simple way how to export to string by using 
`to_string_of_values` function (no parameters are required).

### Accessing sheet in workbook
Each sheet in the workbook can be accessed by using `[]` operator:
```python
sheet = workbook[NAME_OF_THE_SHEET]
```
where `NAME_OF_THE_SHEET` is the string representing the name of the sheet.

### Cross-referencing
In order to access the value in a different sheet, you have to use:
```python
sheet_a.iloc[x1, y1] = sheet.fn.cross_reference(sheet.iloc[x2, y2],
                                                sheet_b)
```
The function `cross_reference` takes two parameters, the first one is the
cell that is the target, the second one is the whole target sheet.

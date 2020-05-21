# TODO:
## BUGS

## IMPORTANT FEATURES
1. Possibly the cell style inside cell (for Excel) (also for slide)
1. New function: binary: mod (%), aggregate: stdev, modus, median,
    unary: ceil, floor
1. Independent styles for cols and rows
1. New property of cell 'excel_style' (and export it to excel)
1. Exporting formulas to CSV, MD (option selecting of languages)
1. Appending to the same Excel file (sheet)
1. Show outputs in README.md
---
1. Unittest for everything
---
# DONE:
1. Help texts for column/row indicies
1. Indices generator rather as a parameter (not global parameter)
1. Offset for label (at least for excel) and add labels to file
1. Expanding:
    Dow we want to expand at all? Very partially
    We just want to add row and column, nothing else
    Nothing can be deleted
1. Slicing + _aggregation_ + _brackets for aggregations_ (sorted natively)
1. Add passing the lists to the slice
1. Fix logarithm and exponential
1. Check the word construction
1. Update grammar to accept right-open slices statement in some languages
1. Replace of spaces in to_dictionary (new parameter), maybe also regexp what
    to pass, this for keys of columns, rows
1. To CSV (Values)
1. possibility to add some text to spreadsheet (?)
1. markdown export
1. Functionality shortcuts
1. shortcuts for everything (unary functions)
1. Styles for excel labels
1. docstrings for everything
1. Initialise directly using static method of CellIndex in
    the sheet (simply without creating instance of CellIndex)
1. Sheet as a grammar controller (No!, Independent utils)
1. Add grammar (from Sheet as a grammar controller - some 
    static method) (No!, Independent utils)
1. Check grammars that are added
1. method to_numpy() - behaving like in Pandas
1. add comprehensive README.md + demo ``
1. demo
1. Independent package with setup
1. simple test to avoid write to itself(? probably not realistic)
1. Description of export methods in README.md
1. Migrate to PyPi.org
1. To numpy does not work
1. Mention to README.md that aggregate functions does not work with identities.
    And mention reference to identities as a general problem.
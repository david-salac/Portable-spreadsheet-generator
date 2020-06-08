EXCEL = {
    "rows": {
        # like 1, 2, 3...
        "name-regexp": "[0-9]+",
        "maximal-number": 65535
    },
    "cols": {
        # like A, B, C...
        "name-regexp": "[A-Z]+",
        "maximal-number": 65535
    },
    "cells": {
        # like 7
        "constant": {
            "prefix": "",
            "suffix": "",
        },
        "variable": {
            "prefix": "",
            "suffix": "",
            "value": {
                'include': False,
                "prefix": "",
                "suffix": ""
            }
        },
        "empty": {
            "content": ""
        },
        # Like A1, A2
        "reference": {
            "prefix": "",
            "suffix": "",
            "separator": "",
            "row_first": False
        },
        # like =7+A2
        "operation": {
            "prefix": "=",
            "suffix": "",
        },
        # like A1:A50
        "aggregation": {
            "prefix": "",
            "separator": ":",
            "suffix": "",
            "start_cell": {
                "prefix": "",
                "suffix": "",
                "separator": "",
                "rows_only": False,
                "cols_only": False,
                "row_first": False,
            },
            "end_cell": {
                "prefix": "",
                "suffix": "",
                "separator": "",
                "rows_only": False,
                "cols_only": False,
                "row_first": False,
            },
            # For example, Python exclude last cell when slicing
            "include_last_cell": False
        },
        "offset": {
            "order": ('reference-cell-column', 'reference-cell-row',
                      'skip-of-rows', 'skip-of-columns'),
            "prefix": "OFFSET(",
            "suffix": ")",
            'reference-cell-column': {
                "prefix": "",
                "suffix": "",
            },
            'reference-cell-row': {
                "prefix": "",
                "suffix": ",",
            },
            'skip-of-rows': {
                "prefix": "",
                "suffix": ",",
            },
            'skip-of-columns': {
                "prefix": "",
                "suffix": "",
            },
        }
    },
    "operations": {
        # BASIC OPERATIONS
        # like 7+3
        "add": {
            "prefix": "",
            "suffix": "",
            "separator": "+",
        },
        # like 7-3
        "subtract": {
            "prefix": "",
            "suffix": "",
            "separator": "-",
        },
        # like 7*3
        "multiply": {
            "prefix": "",
            "suffix": "",
            "separator": "*",
        },
        # like 7/3
        "divide": {
            "prefix": "",
            "suffix": "",
            "separator": "/",
        },
        # like 7%3
        "modulo": {
            "prefix": "MOD(",
            "suffix": ")",
            "separator": ",",
        },
        # like 7^3
        "power": {
            "prefix": "",
            "suffix": "",
            "separator": "^",
        },
        # Merge two strings
        'concatenate': {
            "prefix": "CONCATENATE(",
            "suffix": ")",
            "separator": ",",
            # Context of string
            "string-value": {
                "prefix": '"',
                "suffix": '"',
            },
            # Context of numbers
            "numeric-value": {
                "prefix": '',
                "suffix": '',
            },
        },
        # AGGREGATE FUNCTIONS
        "sum": {
            "prefix": "SUM(",
            "suffix": ")",
        },
        "product": {
            "prefix": "PRODUCT(",
            "suffix": ")",
        },
        "mean": {
            "prefix": "AVERAGE(",
            "suffix": ")",
        },
        "minimum": {
            "prefix": "MIN(",
            "suffix": ")",
        },
        "maximum": {
            "prefix": "MAX(",
            "suffix": ")",
        },
        "stdev": {
            "prefix": "STDEV(",
            "suffix": ")",
        },
        "median": {
            "prefix": "MEDIAN(",
            "suffix": ")",
        },
        "count": {
            "prefix": "COUNT(",
            "suffix": ")",
        },
        "irr": {
            "prefix": "IRR(",
            "suffix": ")",
        },
        "match-negative-before-positive": {
            "prefix": "MATCH(0,",
            "suffix": ")",
        },
        # BASIC OPERATIONS
        "exponential": {
            "prefix": "EXP(",
            "suffix": ")",
        },
        "logarithm": {
            "prefix": "LN(",
            "suffix": ")",
        },
        "ceil": {
            "prefix": "CEILING(",
            "suffix": ")",
        },
        "floor": {
            "prefix": "FLOOR(",
            "suffix": ")",
        },
        "round": {
            "prefix": "ROUND(",
            "suffix": ")",
        },
        "abs": {
            "prefix": "ABS(",
            "suffix": ")",
        },
        "sqrt": {
            "prefix": "SQRT(",
            "suffix": ")",
        },
        "signum": {
            "prefix": "SIGN(",
            "suffix": ")",
        },
        # LOGICAL OPERATIONS
        "equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": "=",
        },
        "not-equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": "<>",
        },
        "greater-than": {
            "prefix": "",
            "suffix": "",
            "separator": ">",
        },
        "greater-than-or-equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": ">=",
        },
        "less-than": {
            "prefix": "",
            "suffix": "",
            "separator": "<",
        },
        "less-than-or-equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": "<=",
        },
        "logical-conjunction": {
            "prefix": "AND(",
            "suffix": ")",
            "separator": ", ",
        },
        "logical-disjunction": {
            "prefix": "OR(",
            "suffix": ")",
            "separator": ", ",
        },
        "logical-negation": {
            "prefix": "NOT(",
            "suffix": ")",
        },
    },
    "brackets": {
        "prefix": "(",
        "suffix": ")"
    },
    "conditional": {
        "order": ('condition', 'consequent', 'alternative'),
        "prefix": "IF(",
        "suffix": ")",
        'condition': {
            "prefix": "",
            "suffix": ","
        },
        'consequent': {
            "prefix": "",
            "suffix": ","
        },
        'alternative': {
            "prefix": "",
            "suffix": ""
        }
    }
}
NATIVE = {
    "rows": {
        # like date...
        "name-regexp": "[0-9]+",
        "maximal-number": 65535
    },
    "cols": {
        # like discount...
        "name-regexp": "[0-9]+",
        "maximal-number": 65535
    },
    "cells": {
        # like 7
        "constant": {
            "prefix": "",
            "suffix": "",
        },
        "variable": {
            "prefix": "value of variable '",
            "suffix": "'",
            "value": {
                'include': True,
                "prefix": " (=",
                "suffix": ")"
            }
        },
        "empty": {
            "content": ""
        },
        # Like value at (1.1.2015, 25%)
        "reference": {
            "prefix": "value at (",
            "suffix": ")",
            "separator": ", ",
            "row_first": True
        },
        # like 7 + value at (1.1.2015, 25%)
        "operation": {
            "prefix": "",
            "suffix": "",
        },
        # like values from (1.1.2015, 25%) to (1.1.2015, 50%)
        "aggregation": {
            "prefix": "values from ",
            "separator": " and ",
            "suffix": "",
            "start_cell": {
                "prefix": "row ",
                "suffix": "",
                "separator": " to row ",
                "rows_only": True,
                "cols_only": False,
                "row_first": True,
            },
            "end_cell": {
                "prefix": "from column ",
                "suffix": "",
                "separator": " to column ",
                "rows_only": False,
                "cols_only": True,
                "row_first": True,
            },
            # For example, Python exclude last cell when slicing
            "include_last_cell": False
        },
        "offset": {
            "order": ('reference-cell-row', 'skip-of-rows',
                      'reference-cell-column', 'skip-of-columns'),
            "prefix": "skip from ",
            "suffix": "",
            'reference-cell-column': {
                "prefix": "and from the column at position ",
                "suffix": " exactly ",
            },
            'reference-cell-row': {
                "prefix": "the row at position ",
                "suffix": " exactly ",
            },
            'skip-of-rows': {
                "prefix": "",
                "suffix": " items down, ",
            },
            'skip-of-columns': {
                "prefix": "",
                "suffix": " items left",
            },
        }
    },
    "operations": {
        # BASIC OPERATIONS
        # like 7+3
        "add": {
            "prefix": "",
            "suffix": "",
            "separator": " + ",
        },
        # like 7 - 3
        "subtract": {
            "prefix": "",
            "suffix": "",
            "separator": " - ",
        },
        # like 7*3
        "multiply": {
            "prefix": "",
            "suffix": "",
            "separator": " * ",
        },
        # like 7/3
        "divide": {
            "prefix": "",
            "suffix": "",
            "separator": " / ",
        },
        # like 7%3
        "modulo": {
            "prefix": "",
            "suffix": "",
            "separator": " mod ",
        },
        # Merge two strings
        'concatenate': {
            "prefix": "concatenate string ",
            "suffix": " and ",
            "separator": "",
            # Context of string
            "string-value": {
                "prefix": "'",
                "suffix": "'",
            },
            # Context of numbers
            "numeric-value": {
                "prefix": "'",
                "suffix": "'",
            },
        },
        # like 7^3
        "power": {
            "prefix": "",
            "suffix": "",
            "separator": " power to ",
        },
        # AGGREGATE FUNCTIONS
        "sum": {
            "prefix": "sum of ",
            "suffix": "",
        },
        "product": {
            "prefix": "product of ",
            "suffix": "",
        },
        "mean": {
            "prefix": "mean-average of ",
            "suffix": "",
        },
        "minimum": {
            "prefix": "minimum of ",
            "suffix": "",
        },
        "maximum": {
            "prefix": "maximum of ",
            "suffix": "",
        },
        "stdev": {
            "prefix": "standard deviation of ",
            "suffix": "",
        },
        "median": {
            "prefix": "median of ",
            "suffix": "",
        },
        "count": {
            "prefix": "number of items in the slice ",
            "suffix": "",
        },
        "irr": {
            "prefix": "Internal Rate of Return of ",
            "suffix": "",
        },
        "match-negative-before-positive": {
            "prefix": "position of the step where numbers "
                      "become to be positive of ",
            "suffix": "",
        },
        # BASIC OPERATIONS
        "exponential": {
            "prefix": "exponential function of ",
            "suffix": "",
        },
        "logarithm": {
            "prefix": "logarithm of ",
            "suffix": "",
        },
        "ceil": {
            "prefix": "ceiling function of ",
            "suffix": "",
        },
        "floor": {
            "prefix": "floor function of ",
            "suffix": "",
        },
        "round": {
            "prefix": "round of ",
            "suffix": "",
        },
        "abs": {
            "prefix": "absolute value of ",
            "suffix": "",
        },
        "sqrt": {
            "prefix": "square root of ",
            "suffix": "",
        },
        "signum": {
            "prefix": "signum of ",
            "suffix": "",
        },
        # LOGICAL OPERATIONS
        "equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": " equal to ",
        },
        "not-equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": " not equal to ",
        },
        "greater-than": {
            "prefix": "",
            "suffix": "",
            "separator": " greater than ",
        },
        "greater-than-or-equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": " greater than or equal to ",
        },
        "less-than": {
            "prefix": "",
            "suffix": "",
            "separator": " less than ",
        },
        "less-than-or-equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": " less than or equal to ",
        },
        "logical-conjunction": {
            "prefix": "",
            "suffix": "",
            "separator": " and ",
        },
        "logical-disjunction": {
            "prefix": "",
            "suffix": "",
            "separator": " or ",
        },
        "logical-negation": {
            "prefix": "negation (",
            "suffix": ")",
        },
    },
    "brackets": {
        "prefix": "(",
        "suffix": ")"
    },
    "conditional": {
        "order": ('condition', 'consequent', 'alternative'),
        "prefix": "(",
        "suffix": ")",
        'condition': {
            "prefix": "if ",
            "suffix": ""
        },
        'consequent': {
            "prefix": " then ",
            "suffix": ""
        },
        'alternative': {
            "prefix": " else ",
            "suffix": ""
        }
    }
}
PYTHON_NUMPY = {
    "rows": {
        # like 0,1,2...
        "name-regexp": "[0-9]+",
        "maximal-number": 65535
    },
    "cols": {
        # like 0,1,2...
        "name-regexp": "[0-9]+",
        "maximal-number": 65535
    },
    "cells": {
        # like 7
        "constant": {
            "prefix": "",
            "suffix": "",
        },
        "empty": {
            "content": ""
        },
        "variable": {
            "prefix": "",
            "suffix": "",
            "value": {
                'include': False,
                "prefix": "",
                "suffix": ""
            }
        },
        # Like [row,column]
        "reference": {
            "prefix": "values[",
            "suffix": "]",
            "separator": ",",
            "row_first": True
        },
        # like 7+values[1,2] (in Python case do nothing)
        "operation": {
            "prefix": "",
            "suffix": "",
        },
        # like values[1:2,3:7]
        "aggregation": {
            "prefix": "values[",
            "separator": ",",
            "suffix": "]",
            "start_cell": {
                "prefix": "",
                "suffix": "",
                "separator": ":",
                "rows_only": True,
                "cols_only": False,
                "row_first": True
            },
            "end_cell": {
                "prefix": "",
                "suffix": "",
                "separator": ":",
                "rows_only": False,
                "cols_only": True,
                "row_first": True
            },
            # For example, Python exclude last cell when slicing
            "include_last_cell": True
        },
        "offset": {
            "order": ('reference-cell-row', 'skip-of-rows',
                      'reference-cell-column', 'skip-of-columns'),
            "prefix": "values[",
            "suffix": "]",
            'reference-cell-column': {
                "prefix": "",
                "suffix": "+",
            },
            'reference-cell-row': {
                "prefix": "",
                "suffix": "+",
            },
            'skip-of-rows': {
                "prefix": "",
                "suffix": ",",
            },
            'skip-of-columns': {
                "prefix": "",
                "suffix": "",
            },
        }
    },
    "operations": {
        # BASIC OPERATIONS
        # like 7+3
        "add": {
            "prefix": "",
            "suffix": "",
            "separator": "+",
        },
        # like 7-3
        "subtract": {
            "prefix": "",
            "suffix": "",
            "separator": "-",
        },
        # like 7*3
        "multiply": {
            "prefix": "",
            "suffix": "",
            "separator": "*",
        },
        # like 7/3
        "divide": {
            "prefix": "",
            "suffix": "",
            "separator": "/",
        },
        # like 7%3
        "modulo": {
            "prefix": "",
            "suffix": "",
            "separator": "%",
        },
        # like 7^3
        "power": {
            "prefix": "",
            "suffix": "",
            "separator": "**",
        },
        # Merge two strings
        'concatenate': {
            "prefix": "",
            "suffix": "",
            "separator": "+",
            # Context of string
            "string-value": {
                "prefix": '',
                "suffix": '',
            },
            # Context of numbers
            "numeric-value": {
                "prefix": '"',
                "suffix": '"',
            },
        },
        # AGGREGATE FUNCTIONS
        "sum": {
            "prefix": "np.sum(",
            "suffix": ")",
        },
        "product": {
            "prefix": "np.prod(",
            "suffix": ")",
        },
        "mean": {
            "prefix": "np.mean(",
            "suffix": ")",
        },
        "minimum": {
            "prefix": "np.min(",
            "suffix": ")",
        },
        "maximum": {
            "prefix": "np.max(",
            "suffix": ")",
        },
        "stdev": {
            "prefix": "np.std(",
            "suffix": ")",
        },
        "median": {
            "prefix": "np.median(",
            "suffix": ")",
        },
        "count": {
            "prefix": "((lambda var=",
            "suffix": ": var.shape[0] * var.shape[1])())",
        },
        "irr": {
            "prefix": "npf.irr(",
            "suffix": ")",
        },
        "match-negative-before-positive": {
            "prefix": "np.argmin(",
            "suffix": "<0)",
        },
        # BASIC OPERATIONS
        "exponential": {
            "prefix": "np.exp(",
            "suffix": ")",
        },
        "logarithm": {
            "prefix": "np.log(",
            "suffix": ")",
        },
        "ceil": {
            "prefix": "np.ceil(",
            "suffix": ")",
        },
        "floor": {
            "prefix": "np.floor(",
            "suffix": ")",
        },
        "round": {
            "prefix": "np.round(",
            "suffix": ")",
        },
        "abs": {
            "prefix": "np.abs(",
            "suffix": ")",
        },
        "sqrt": {
            "prefix": "np.sqrt(",
            "suffix": ")",
        },
        "signum": {
            "prefix": "np.sign(",
            "suffix": ")",
        },
        # LOGICAL OPERATIONS
        "equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": "==",
        },
        "not-equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": "!=",
        },
        "greater-than": {
            "prefix": "",
            "suffix": "",
            "separator": ">",
        },
        "greater-than-or-equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": ">=",
        },
        "less-than": {
            "prefix": "",
            "suffix": "",
            "separator": "<",
        },
        "less-than-or-equal-to": {
            "prefix": "",
            "suffix": "",
            "separator": "<=",
        },
        "logical-conjunction": {
            "prefix": "",
            "suffix": "",
            "separator": " and ",
        },
        "logical-disjunction": {
            "prefix": "",
            "suffix": "",
            "separator": " or ",
        },
        "logical-negation": {
            "prefix": "not (",
            "suffix": ")",
        },
    },
    "brackets": {
        "prefix": "(",
        "suffix": ")"
    },
    "conditional": {
        "order": ('consequent', 'condition', 'alternative'),
        "prefix": "(",
        "suffix": ")",
        'condition': {
            "prefix": " if (",
            "suffix": ") "
        },
        'consequent': {
            "prefix": "(",
            "suffix": ")"
        },
        'alternative': {
            "prefix": "else (",
            "suffix": ")"
        }
    }
}

GRAMMARS = {
    # System grammars:
    "excel": EXCEL,
    "python_numpy": PYTHON_NUMPY,
    # User defined grammars goes here:
    "native": NATIVE,
    # --------------------------
}

"""General pattern of a grammar defining some language and with data types
    of each feature (and with description).

Generally a PREFIX is what is inserted before the word when it is created,
    a SUFFIX is what is inserted after the word when created, a SEPARATOR
    is what is inserted between two words where needed. A CONTENT is what
    is inserted instead of any word.
"""
GRAMMAR_PATTERN: dict = {
    "rows": {
        # Define the RegExp pattern that name of rows should pass
        "name-regexp": str,
        # Define the maximal number of rows
        "maximal-number": int
    },
    "cols": {
        # Define the RegExp pattern that name of colmn should pass
        "name-regexp": str,
        # Define the maximal number of rows
        "maximal-number": int
    },
    "cells": {
        # Define the basic words related to a cell

        # Constant definition (like 7):
        "constant": {
            "prefix": str,
            "suffix": str,
        },

        # Variable definition (e.g. pi)
        "variable": {
            "prefix": str,
            "suffix": str,
            # If is included (parameter include), also add the value inside
            #   the variable as a suffix (always) after variable name
            "value": {
                'include': bool,
                "prefix": str,
                "suffix": str
            }
        },

        # Empty cell definition
        "empty": {
            "content": str
        },

        # Reference to a cell (like =A7 in Excel)
        "reference": {
            "prefix": str,
            "suffix": str,
            "separator": str,
            # If True, the row is on the first position and column on the
            # second position. (e. g. it is False for Excel)
            "row_first": bool
        },

        # Operation (like =CELL + CELL)
        "operation": {
            "prefix": str,
            "suffix": str,
        },

        # Aggregation of cells (e. g. C1:C5 in Excel)
        "aggregation": {
            "prefix": str,
            "separator": str,
            "suffix": str,
            # Word defining the starting cell
            "start_cell": {
                "prefix": str,
                "suffix": str,
                "separator": str,
                # If True, cell contains only reference to rows (mutually
                # exclusive with cols_only.
                "rows_only": bool,
                # If True, cell contains only reference to columns (mutually
                # exclusive with rows_only.
                "cols_only": bool,
                "row_first": bool,
            },
            # Word defining the last cell
            "end_cell": {
                "prefix": str,
                "suffix": str,
                "separator": str,
                # If True, cell contains only reference to rows (mutually
                # exclusive with cols_only.
                "rows_only": bool,
                # If True, cell contains only reference to columns (mutually
                # exclusive with rows_only.
                "cols_only": bool,
                "row_first": bool,
            },
            # For example, Python exclude last cell when slicing (it has a
            # close-left logic), but Excel does include it. If True the last
            # cell is included, if False, the last cell is the previous plus
            # one in the index.
            "include_last_cell": bool
        },
        # Return the reference to the cell n-down top and m-columns left
        "offset": {
            # Some ordered subset of ('reference-cell-row', 'skip-of-rows',
            # 'reference-cell-column', 'skip-of-columns') defining in what
            # order the offset is computed.
            "order": tuple,
            "prefix": str,
            "suffix": str,
            # Label (index) for the column of the reference cell
            'reference-cell-column': {
                "prefix": str,
                "suffix": str,
            },
            # Label (index) for the row of the reference cell
            'reference-cell-row': {
                "prefix": str,
                "suffix": str,
            },
            # How many rows are skipped down (reference to the cell, or value)
            'skip-of-rows': {
                "prefix": str,
                "suffix": str,
            },
            # How many columns are skipped left (reference to cell, or value)
            'skip-of-columns': {
                "prefix": str,
                "suffix": str,
            },
        }
    },
    "operations": {
        # === BASIC BINARY OPERATIONS ===
        # Adding, like 7+3
        "add": {
            "prefix": str,
            "suffix": str,
            "separator": str,  # Typically +
        },
        # Subtracting, like 7-3
        "subtract": {
            "prefix": str,
            "suffix": str,
            "separator": str,  # Typically -
        },
        # Multiplying, like 7*3
        "multiply": {
            "prefix": str,
            "suffix": str,
            "separator": str,  # Typically *
        },
        # Dividing, like 7/3
        "divide": {
            "prefix": str,
            "suffix": str,
            "separator": str,  # Typically /
        },
        # Modulo, like 7%3
        "modulo": {
            "prefix": str,
            "suffix": str,
            "separator": str,  # Typically %
        },
        # Power to, like 7^3
        "power": {
            "prefix": str,
            "suffix": str,
            "separator": str,  # Typically '^' (in Python '**')
        },
        # Merge two strings, like "a" + "b" = "ab"
        'concatenate': {
            "prefix": str,
            "suffix": str,
            "separator": str,
            # Context of the string constant
            "string-value": {
                "prefix": str,
                "suffix": str,
            },
            # Context of the numbers constant
            "numeric-value": {
                "prefix": str,
                "suffix": str,
            },
        },

        # === AGGREGATE FUNCTIONS (functions for aggregated cells) ===
        # Sum of aggregated cells.
        "sum": {
            "prefix": str,  # Like SUM(
            "suffix": str,  # Like )
        },
        # Sum of aggregated cells.
        "product": {
            "prefix": str,  # Like PRODUCT(
            "suffix": str,  # Like )
        },
        # Mean-average of aggregated cells.
        "mean": {
            "prefix": str,  # Like AVERAGE(
            "suffix": str,  # Like )
        },
        # Minimum of aggregated cells.
        "minimum": {
            "prefix": str,  # Like MIN(
            "suffix": str,  # Like )
        },
        # Standard deviation of aggregated cells.
        "stdev": {
            "prefix": str,
            "suffix": str,
        },
        # Median of aggregated cells.
        "median": {
            "prefix": str,
            "suffix": str,
        },
        # Maximum of aggregated cells.
        "maximum": {
            "prefix": str,  # Like MAX(
            "suffix": str,  # Like )
        },
        # Number of aggregated cells.
        "count": {
            "prefix": str,
            "suffix": str,
        },
        # Internal Rate of Return (IRR) of aggregated cells.
        "irr": {
            "prefix": str,
            "suffix": str,
        },
        # Match the position of the last negative number before first
        #   negative number in a sequence (works only for single row/column).
        "match-negative-before-positive": {
            "prefix": str,
            "suffix": str,
        },

        # === BASIC UNARY OPERATIONS (that takes only one operand) ===
        # Exponential (natural) of the argument
        "exponential": {
            "prefix": str,  # Like EXP(
            "suffix": str,  # Like )
        },
        # Natural logarithm of the argument
        "logarithm": {
            "prefix": str,  # Like LN(
            "suffix": str,  # Like )
        },
        # Ceiling function
        "ceil": {
            "prefix": str,
            "suffix": str,
        },
        # Floor function
        "floor": {
            "prefix": str,
            "suffix": str,
        },
        # Round the number
        "round": {
            "prefix": str,
            "suffix": str,
        },
        # Absolute value
        "abs": {
            "prefix": str,
            "suffix": str,
        },
        # Absolute value
        "sqrt": {
            "prefix": str,
            "suffix": str,
        },
        # Signum function (-1 if value is < 0, 0 if val == 0, 1 if val > 0)
        "signum": {
            "prefix": str,
            "suffix": str,
        },

        # === LOGICAL OPERATIONS (returns true or false) ===
        # Equal to
        "equal-to": {
            "prefix": str,
            "suffix": str,
            "separator": str,
        },
        # Not equal to
        "not-equal-to": {
            "prefix": str,
            "suffix": str,
            "separator": str,
        },
        # Greater than
        "greater-than": {
            "prefix": str,
            "suffix": str,
            "separator": str,
        },
        # Greater than or equal to
        "greater-than-or-equal-to": {
            "prefix": str,
            "suffix": str,
            "separator": str,
        },
        # Less than
        "less-than": {
            "prefix": str,
            "suffix": str,
            "separator": str,
        },
        # Less than or equal to
        "less-than-or-equal-to": {
            "prefix": str,
            "suffix": str,
            "separator": str,
        },
        # Logical conjunction
        "logical-conjunction": {
            "prefix": str,
            "suffix": str,
            "separator": str,
        },
        # Logical disjunction
        "logical-disjunction": {
            "prefix": str,
            "suffix": str,
            "separator": str,
        },
        # Logical negation
        "logical-negation": {
            "prefix": str,
            "suffix": str,
        },
    },
    # Brackets around the statement
    "brackets": {
        "prefix": str,  # Almost always just '('
        "suffix": str,  # Almost always just ')'
    },
    # Conditional: standard if-then-else statement
    "conditional": {
        # Defines order of clausules ('consequent', 'condition', 'alternative')
        "order": tuple,
        # Defines prefix of the whole conditional
        "prefix": str,
        # Defines suffix of the whole conditional
        "suffix": str,
        # Conditional statement (e. g. 'A > 5 or C < 5')
        'condition': {
            "prefix": str,
            "suffix": str
        },
        # Consequent (then part): part that occurs if the condition is true.
        'consequent': {
            "prefix": str,
            "suffix": str
        },
        # Alternative (else part): part that occurs if the condition is false.
        'alternative': {
            "prefix": str,
            "suffix": str
        }
    }
}

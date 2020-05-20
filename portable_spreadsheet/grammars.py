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
        # like 7^3
        "power": {
            "prefix": "",
            "suffix": "",
            "separator": "^",
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
        # BASIC OPERATIONS
        "exponential": {
            "prefix": "EXP(",
            "suffix": ")",
        },
        "logarithm": {
            "prefix": "LN(",
            "suffix": ")",
        },
    },
    "brackets": {
        "prefix": "(",
        "suffix": ")"
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
            "separator": " to ",
            "suffix": "",
            "start_cell": {
                "prefix": "(",
                "suffix": ")",
                "separator": ", ",
                "rows_only": False,
                "cols_only": False,
                "row_first": True,
            },
            "end_cell": {
                "prefix": "(",
                "suffix": ")",
                "separator": ", ",
                "rows_only": False,
                "cols_only": False,
                "row_first": True,
            },
            # For example, Python exclude last cell when slicing
            "include_last_cell": True
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
        # BASIC OPERATIONS
        "exponential": {
            "prefix": "exponential function of ",
            "suffix": "",
        },
        "logarithm": {
            "prefix": "logarithm of ",
            "suffix": "",
        },
    },
    "brackets": {
        "prefix": "(",
        "suffix": ")"
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
        # Like [row,column]
        "reference": {
            "prefix": "values[",
            "suffix": "]",
            "separator": ",",
            "row_first": True
        },
        # like =7+values[1,2]
        "operation": {
            "prefix": "=",
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
        # like 7^3
        "power": {
            "prefix": "",
            "suffix": "",
            "separator": "^",
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
        # BASIC OPERATIONS
        "exponential": {
            "prefix": "np.exp(",
            "suffix": ")",
        },
        "logarithm": {
            "prefix": "np.log(",
            "suffix": ")",
        },
    },
    "brackets": {
        "prefix": "(",
        "suffix": ")"
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
        # Power to, like 7^3
        "power": {
            "prefix": str,
            "suffix": str,
            "separator": str,  # Typically '^' (in Python '**')
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
        # Maximum of aggregated cells.
        "maximum": {
            "prefix": str,  # Like MAX(
            "suffix": str,  # Like )
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
    },
    # Brackets around the statement
    "brackets": {
        "prefix": str,  # Almost always just '('
        "suffix": str,  # Almost always just ')'
    }
}

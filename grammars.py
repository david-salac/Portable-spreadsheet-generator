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
            }
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
            }
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
            }
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

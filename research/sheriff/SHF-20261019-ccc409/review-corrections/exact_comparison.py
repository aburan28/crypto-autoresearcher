"""Compare parsed JSON results exactly, except explicitly reviewed leaf paths.

No subprocess, file mutation, metadata-name guessing or numeric rounding occurs.
Callers must bind their artifact pair and reviewed metadata paths separately.
This helper does not certify that all required artifacts were retained.
"""
from __future__ import annotations

import math


def _validate(value):
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise ValueError("JSON object keys must be strings")
        for item in value.values():
            _validate(item)
    elif type(value) is list:
        for item in value:
            _validate(item)
    elif type(value) is float:
        if not math.isfinite(value):
            raise ValueError("Nonfinite numbers cannot be compared as JSON results")
    elif type(value) not in (str, int, bool, type(None)):
        raise ValueError("Unsupported JSON value")


def _leaf(value, path):
    if not path:
        raise ValueError("Ignoring the entire result is not allowed")
    for part in path:
        if type(value) is dict and type(part) is str and part in value:
            value = value[part]
        elif (type(value) is list and type(part) is int
              and 0 <= part < len(value)):
            value = value[part]
        else:
            raise ValueError(f"Metadata path does not resolve: {path!r}")
    if type(value) in (dict, list):
        raise ValueError("Only individual metadata leaves may be ignored")


def compare_results(expected, actual, *, ignored_metadata_paths=()):
    """Return exact differences and the exact ignored leaf paths.

    Paths are tuples of object keys or list indices. The empty default ignores
    nothing. Missing metadata and container exclusions are refused, so an
    allowlist cannot silently hide a missing field or an entire output object.
    """
    _validate(expected)
    _validate(actual)
    ignored = set()
    for path in ignored_metadata_paths:
        if type(path) is not tuple:
            raise ValueError("Each metadata path must be a tuple")
        _leaf(expected, path)
        _leaf(actual, path)
        ignored.add(path)
    differences = []

    def walk(left, right, path):
        if path in ignored:
            return
        if type(left) is not type(right):
            differences.append({"path": list(path), "reason": "type_mismatch"})
        elif type(left) is dict:
            for key in sorted(left.keys() | right.keys()):
                if key not in left or key not in right:
                    differences.append({"path": [*path, key], "reason": "missing_key"})
                else:
                    walk(left[key], right[key], (*path, key))
        elif type(left) is list:
            if len(left) != len(right):
                differences.append({"path": list(path), "reason": "length_mismatch"})
            for index, (a, b) in enumerate(zip(left, right)):
                walk(a, b, (*path, index))
        elif left != right:
            differences.append({"path": list(path), "reason": "value_mismatch"})

    walk(expected, actual, ())
    return {"equal": not differences, "differences": differences,
            "ignored_metadata_paths": [list(p) for p in sorted(ignored, key=repr)]}

"""TASK-20261008-e2830e B0 input: KEY PATHS ONLY of the first census row of one archived
EXP-PFDR-011cd0 job file. Read-only. Standard library only.

It reads only the FIRST line of the gzip file, parses it as JSON, and prints
the key path of every key reachable through JSON objects. No value is printed:

* an object is printed as "path/" and descended into;
* an array is printed as "path[]" and NOT descended into (its elements are values);
* a scalar is printed as "path" with no value and no type;
* an object whose keys are themselves data values (multiplicity_histogram:
  its keys are observed multiplicities) is printed as "path/{data-valued keys, not listed}"
  and NOT descended into.

Usage: python -I keypaths_first_census_row.py ROWS_JSONL_GZ
"""
import gzip
import json
import sys

DATA_VALUED_KEY_OBJECTS = {"multiplicity_histogram"}


def walk(obj, path, out):
    for k in obj:  # insertion order of the row as written
        p = f"{path}.{k}" if path else k
        v = obj[k]
        if k in DATA_VALUED_KEY_OBJECTS and isinstance(v, dict):
            out.append(p + "/{data-valued keys, not listed}")
        elif isinstance(v, dict):
            out.append(p + "/")
            walk(v, p, out)
        elif isinstance(v, list):
            out.append(p + "[]")
        else:
            out.append(p)


def main(argv):
    path = argv[1]
    with gzip.open(path, "rt") as fh:
        line = fh.readline()
    row = json.loads(line)
    out = []
    walk(row, "", out)
    print(f"# key paths of line 1 of {path} (no values); {len(out)} paths")
    for p in out:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

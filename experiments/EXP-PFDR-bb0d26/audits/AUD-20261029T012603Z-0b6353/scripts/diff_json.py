#!/usr/bin/env python3
"""Field-by-field diff of two JSON files (recorded vs replay). Read-only.

Usage: diff_json.py RECORDED REPLAY
Prints every leaf that differs with its JSON pointer, both values, and for floats the
absolute and relative difference and the distance in ULPs. Ends with a tally that
separates float-only differences from differences in any non-float leaf (ints, strings,
bools, None, list lengths, key sets), which would be material.
"""
import json
import math
import struct
import sys


def ulps(a: float, b: float) -> int:
    def key(x):
        i = struct.unpack("<q", struct.pack("<d", x))[0]
        return i if i >= 0 else -(i & 0x7FFFFFFFFFFFFFFF)
    return abs(key(a) - key(b))


def walk(a, b, ptr, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(("keyset", ptr + "/" + str(k), k in a, k in b))
            else:
                walk(a[k], b[k], ptr + "/" + str(k), out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(("length", ptr, len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{ptr}/{i}", out)
    elif isinstance(a, float) and isinstance(b, float):
        if a != b:
            out.append(("float", ptr, a, b))
    elif type(a) is not type(b) or a != b:
        out.append(("other", ptr, a, b))


def main():
    a, b = (json.load(open(p)) for p in sys.argv[1:3])
    out = []
    walk(a, b, "", out)
    floats = [d for d in out if d[0] == "float"]
    other = [d for d in out if d[0] != "float"]
    for kind, ptr, x, y in out:
        if kind == "float":
            rel = abs(x - y) / max(abs(x), abs(y)) if max(abs(x), abs(y)) else 0.0
            print(f"float  {ptr}: rec={x!r} rep={y!r} abs={abs(x - y):.3e} rel={rel:.3e} ulps={ulps(x, y)}")
        else:
            print(f"{kind:6s} {ptr}: rec={x!r} rep={y!r}")
    max_rel = max((abs(x - y) / max(abs(x), abs(y)) for _, _, x, y in floats), default=0.0)
    max_ulp = max((ulps(x, y) for _, _, x, y in floats), default=0)
    print(json.dumps({"differing_leaves": len(out), "float_leaves": len(floats),
                      "non_float_leaves": len(other), "max_rel_diff": max_rel, "max_ulps": max_ulp,
                      "byte_identical_after_parse": a == b}))


if __name__ == "__main__":
    main()

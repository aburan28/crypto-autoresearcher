#!/usr/bin/env python3
"""N3(6): my own recursive numeric diff of the two driver executions.
Claim under test: 'zero numeric differences between executions across 42,650
compared values'."""
import json
import math

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/"


def walk(a, b, path, nums, diffs, struct, bools, strs):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k not in a or k not in b:
                struct.append((path + "/" + str(k), "only in " + ("exec-2" if k in a else "exec-1")))
            else:
                walk(a[k], b[k], path + "/" + str(k), nums, diffs, struct, bools, strs)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            struct.append((path, f"list length {len(a)} vs {len(b)}"))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", nums, diffs, struct, bools, strs)
    elif isinstance(a, bool) or isinstance(b, bool):
        bools[0] += 1
        if a != b:
            diffs.append((path, a, b, "bool"))
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        nums[0] += 1
        if a is None or b is None:
            return
        d = abs(a - b)
        if d > 0:
            diffs.append((path, a, b, d))
    elif isinstance(a, str) and isinstance(b, str):
        strs[0] += 1
        if a != b:
            strs[1] += 1
            if len(strs) < 40:
                strs.append((path, a[:90], b[:90]))
    elif a is None and b is None:
        pass
    else:
        if a != b:
            struct.append((path, f"type/value {type(a).__name__} vs {type(b).__name__}"))


for pair in [("raw-result.json", "raw-result.driver-exec-1.json"),
             ("reproduction.json", "reproduction.driver-exec-1.json")]:
    a = json.load(open(RUN + pair[0]))
    b = json.load(open(RUN + pair[1]))
    nums, diffs, struct, bools, strs = [0], [], [], [0], [0, 0]
    walk(a, b, "", nums, diffs, struct, bools, strs)
    print(f"=== {pair[0]} vs {pair[1]} ===")
    print(f"  numeric values compared: {nums[0]}   booleans: {bools[0]}   strings: {strs[0]}")
    print(f"  NUMERIC/BOOLEAN DIFFERENCES: {len(diffs)}")
    for d in diffs[:20]:
        print("   ", d)
    print(f"  structural differences (keys/lengths/types): {len(struct)}")
    for s in struct[:20]:
        print("   ", s)
    print(f"  string differences: {strs[1]}")
    for s in strs[2:8]:
        print("    PATH", s[0], "\n      exec-2:", s[1], "\n      exec-1:", s[2])

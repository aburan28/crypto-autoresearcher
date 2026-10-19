#!/usr/bin/env python3
"""Regression check: every leaf of the pre-#942 baselines.json must be unchanged in the post-#942 file, except listed ones.
Usage: python3 -I -B numdiff.py <old.json> <new.json>"""
import json, sys
old = json.load(open(sys.argv[1])); new = json.load(open(sys.argv[2]))
def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from leaves(v, f"{p}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from leaves(v, f"{p}[{i}]")
    else: yield p, o
lo = dict(leaves(old)); ln = dict(leaves(new))
changed = [(p, lo[p], ln.get(p, "<removed>")) for p in lo if ln.get(p, "<removed>") != lo[p]]
added = [p for p in ln if p not in lo]
print(f"old leaves {len(lo)}, new leaves {len(ln)}, changed or removed {len(changed)}, added {len(added)}")
for p, a, b in changed:
    if isinstance(a, (int, float)) or isinstance(b, (int, float)):
        print("NUMERIC CHANGE", p, a, "->", b)
    else:
        print("TEXT CHANGE", p, "| old:", str(a)[:160], "| new:", str(b)[:160])
print("added top-level paths:", sorted({p.split("[")[0].split(".")[1] if p.count(".") else p for p in added}))
print("added leaves (first 40):"); [print("  ", p) for p in added[:40]]

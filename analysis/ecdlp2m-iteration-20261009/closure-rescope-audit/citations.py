#!/usr/bin/env python3
"""Count repository files citing each audited record id (deterministic; stdlib only).
Usage: python3 citations.py <repo-root> > citations.md"""
import os, sys, re
root = sys.argv[1] if len(sys.argv) > 1 else "."
IDS = ["KN-FIND-aa2efc", "KR-IC-1fcdbc", "KR-IC-5ea2f8", "KR-IC-46d822"]
EXT = (".yaml", ".yml", ".md", ".json")
hits = {i: {"files": 0, "by_top": {}} for i in IDS}
for dp, dn, fn in os.walk(root):
    dn[:] = sorted(d for d in dn if d not in (".git", "node_modules", ".index", "__pycache__"))
    for f in sorted(fn):
        if not f.endswith(EXT):
            continue
        p = os.path.join(dp, f)
        try:
            s = open(p, errors="replace").read()
        except OSError:
            continue
        top = os.path.relpath(p, root).split(os.sep)[0]
        for i in IDS:
            if i in s and not os.path.basename(p).startswith(i):
                hits[i]["files"] += 1
                hits[i]["by_top"][top] = hits[i]["by_top"].get(top, 0) + 1
print("| record | citing files (excluding itself) | by top-level directory |")
print("|---|---|---|")
for i in IDS:
    bt = ", ".join(f"{k} {v}" for k, v in sorted(hits[i]["by_top"].items(), key=lambda kv: -kv[1]))
    print(f"| {i} | {hits[i]['files']} | {bt} |")

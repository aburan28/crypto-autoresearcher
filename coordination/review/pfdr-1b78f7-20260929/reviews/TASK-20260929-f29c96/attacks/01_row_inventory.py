"""Inventory of the retained harvest rows: rows per (file, m, bits, curve, arm, mode, class),
min/max attempt, and whether instances are contiguous in each file.  Streams every file.
No randomness.  Output: attacks/out/01_row_inventory.json
"""
import glob
import gzip
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import RUNS, P, OUT  # noqa: E402

PAT = re.compile(r'^\{"bits": (\d+), "curve": (\d+), "m": (\d+), "arm": "([a-z0-9_]+)", '
                 r'"mode": "([a-z]+)", "class": "([A-Z]+)", "attempt": (-?\d+)')


def files():
    out = [os.path.join(RUNS, P + "census-m3", "harvest-rows.jsonl.gz"),
           os.path.join(RUNS, P + "census-m4", "harvest-rows.jsonl.gz")]
    out += sorted(glob.glob(os.path.join(RUNS, P + "census-m4", "attempt-2", "jobs", "*", "harvest-rows.jsonl.gz")))
    out += sorted(glob.glob(os.path.join(RUNS, P + "census-m5", "attempt-1", "jobs", "*", "harvest-rows.jsonl.gz")))
    out += sorted(glob.glob(os.path.join(RUNS, P + "stage-r", "attempt-1", "jobs", "*", "harvest-rows.jsonl.gz")))
    out += sorted(glob.glob(os.path.join(RUNS, P + "j0", "attempt-1", "jobs", "*", "harvest-rows.jsonl.gz")))
    return out


def main():
    inv = {}
    noncontig = []
    for f in files():
        rel = os.path.relpath(f, RUNS)
        per = defaultdict(lambda: [0, 10**9, -10**9])
        seen_done, cur = set(), None
        bad = 0
        with gzip.open(f, "rt") as fh:
            for line in fh:
                mt = PAT.match(line)
                if not mt:
                    bad += 1
                    continue
                b, c, m, arm, mode, cl, att = mt.groups()
                key = (int(m), int(b), int(c), arm, mode)
                if key != cur:
                    if key in seen_done:
                        noncontig.append([rel, list(key)])
                    if cur is not None:
                        seen_done.add(cur)
                    cur = key
                rec = per[key + (cl,)]
                rec[0] += 1
                rec[1] = min(rec[1], int(att))
                rec[2] = max(rec[2], int(att))
        inv[rel] = {"unparsed_prefix_lines": bad,
                    "instances": {"|".join(map(str, k)): v for k, v in sorted(per.items())}}
        print(rel, sum(v[0] for v in per.values()), "rows", len({k[:5] for k in per}), "instances", file=sys.stderr)
    os.makedirs(os.path.join(OUT, "out"), exist_ok=True)
    with open(os.path.join(OUT, "out", "01_row_inventory.json"), "w") as fh:
        json.dump({"files": inv, "noncontiguous_instances": noncontig}, fh, indent=0, sort_keys=True)
    print("noncontiguous:", len(noncontig), file=sys.stderr)


if __name__ == "__main__":
    main()

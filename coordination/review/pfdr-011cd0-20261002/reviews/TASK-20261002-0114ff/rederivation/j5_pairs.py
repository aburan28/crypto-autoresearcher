#!/usr/bin/env python3
"""J5 (c): the harvester's pair counters against the pairs reconstructed from rows.

TASK-20261002-0114ff. For every R12 instance (TT, TB at_stop) and R13 instance
(SS at_X_fix), compares the census row's pairs_raw (and relation_pairs) with the
validator's own pair count from the retained rows (rederivation/outputs/
relcount.jsonl.gz 'pairs' = sum over x-groups of C(k', 2) for TT and SS; the star
pairs for TB). Equality on every instance means no pair-counter residual exists in
the panel data that H1a/H1b could read. Standard library only.
"""
import collections
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
RUNS = WT + "/experiments/EXP-PFDR-011cd0/runs/"


def main():
    own = {}
    with gzip.open(os.path.join(HERE, "outputs", "relcount.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            own[tuple(r["key"])] = r
    res = collections.Counter()
    ex = []
    for rd, mode in (("RUN-PFDR-011cd0-table", "table"), ("RUN-PFDR-011cd0-search", "search")):
        with gzip.open(RUNS + rd + "/rows.jsonl.gz", "rt") as fh:
            for line in fh:
                r = json.loads(line)
                k = (r["bits"], r["curve"], int(r["method"].replace("ic_m", "")), r["arm"], r["mode"])
                o = own[k]
                h = r["harvest"]
                for cls, scope in ((("TT", "at_stop"), ("TB", "at_stop")) if mode == "table" else (("SS", "at_X_fix"),)):
                    hb = h[cls][scope]
                    a = hb["pairs_raw"] == o[cls]["pairs"]
                    b = hb["relation_pairs"] == o[cls]["pairs"]
                    res[f"{mode}|{cls}|pairs_raw=={'own' if a else 'DIFF'}"] += 1
                    res[f"{mode}|{cls}|relation_pairs=={'own' if b else 'DIFF'}"] += 1
                    if not (a and b) and len(ex) < 30:
                        ex.append({"key": list(k), "class": cls, "pairs_raw": hb["pairs_raw"],
                                   "relation_pairs": hb["relation_pairs"], "own_pairs": o[cls]["pairs"]})
    out = {"counts": dict(sorted(res.items())), "examples": ex}
    json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
    print(json.dumps(out, indent=1)[:3000])


if __name__ == "__main__":
    main()

"""J2 (5): decode 20 archived curve-algebra E_hex with the validator's own codec and compare, at ALL 2^20
assignments, the 19 decoded Boolean equations with the bits of S_3(x_1, x_2, x_R) evaluated directly in
F_{2^19}. Systems: the 10 lowest-index S3-U400, 5 lowest-index S3-SAT100, 5 lowest-index F-RANDX19.
usage: python3 decode_vs_direct.py <run_dir>
"""
import gzip
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gf219 as G  # noqa: E402

RUN = sys.argv[1]
inst = [json.loads(l) for l in gzip.open(os.path.join(RUN, "instances.jsonl.gz"), "rt")]
sel = ([r for r in inst if r["arm"] == "S3-U400"][:10] + [r for r in inst if r["arm"] == "S3-SAT100"][:5]
       + [r for r in inst if r["arm"] == "F-RANDX19"][:5])
TT = G._build_truth_tables()
out = []
for r in sel:
    E = G.hex_to_E(r["E_hex"])
    direct = G.s3_grid(r["x_R"])  # int per v = x1 + 1024 x2
    bad = 0
    for k in range(19):
        cols = np.flatnonzero(E[k])
        val = np.bitwise_xor.reduce(TT[cols], axis=0) if cols.size else np.zeros(TT.shape[1], np.uint64)
        bits = np.unpackbits(val.view(np.uint8), bitorder="little").astype(np.int64)
        want = (direct >> k) & 1
        bad += int((bits != want).sum())
    out.append({"key": r["key"], "x_R": r["x_R"], "assignments": 1 << 20, "bit_mismatches": bad})
res = {"systems": out, "all_equal": all(o["bit_mismatches"] == 0 for o in out)}
json.dump(res, open(os.path.join(HERE, "decode-vs-direct.json"), "w"), indent=1)
print(res["all_equal"], [o["bit_mismatches"] for o in out])

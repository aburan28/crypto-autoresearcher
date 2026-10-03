"""Consistency check (no simulation): this reviewer's CC-8 from the extract against the archived
R16 cells.jsonl for every FAM-1 band and per-rung cell, known-null band/per-rung cell, planted cell
and CARRY-1 (exact equality of C_A, C_R, V expected; z to 1e-9).
Command: nice -n 19 $PY attacks/common/check_cells.py --out attacks/common/out/check_cells.json"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "j4"))
import j4lib as L

ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
design = L.load_design(); rows = L.load_extract()
groups, rho1, drops = L.build_groups(rows, design)
cells = [json.loads(l) for l in open(os.path.join(L.EXP, "runs", "RUN-PFDR-011cd0-analysis", "cells.jsonl"))]
mism = []
for c in cells:
    rungs = tuple(c["rungs"])
    o = L.observed_cell(rows, groups, c["arm"], c["class"], c["m"], rungs)
    for k in ("C_A", "C_R", "V"):
        if abs(o[k] - c[k]) > 1e-6 * max(1, abs(c[k])):
            mism.append([c["id"], c["kind"], k, o[k], c[k]])
    if c["z"] is not None and isinstance(c["z"], (int, float)) and abs(o["z"] - c["z"]) > 1e-9:
        mism.append([c["id"], c["kind"], "z", o["z"], c["z"]])
json.dump({"cells_checked": len(cells), "mismatches": mism, "cc6_drops": drops}, open(a.out, "w"), indent=1)
print(len(cells), "mismatches", len(mism), mism[:5], "drops", len(drops))

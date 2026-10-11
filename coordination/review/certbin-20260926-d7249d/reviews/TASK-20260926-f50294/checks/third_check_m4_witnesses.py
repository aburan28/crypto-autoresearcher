#!/usr/bin/env python3
"""DECLARED THIRD CHECK (CP-7 budget: 20 archived systems) of
TASK-20260926-f50294, for J8's certificate-backed table: re-verify J1's VC-6
M_4 non-refutation witnesses (m4-witnesses.jsonl.gz of TASK-20260926-401771)
on the 20 lowest-index S3-U400 systems, with the comparator's own code
(checks/mini.py): own S_3 descent from the run's x_R, own M_4 rows (4009), own
ann-v1 coordinate order. A witness is valid iff lambda vanishes on every M_4
row and lambda(1) = 1 (then 1 is not in rowspace(M_4), hence not in
rowspace(M_3) either). Also checked: the run's E_hex equals the own descent.

Usage: python3 third_check_m4_witnesses.py <worktree_root> <out_json>
"""
import gzip
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mini  # noqa: E402

J1 = "coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-401771"
RUN = "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60"


def main():
    root, outp = sys.argv[1:3]
    os.chdir(root)
    with gzip.open(f"{RUN}/instances.jsonl.gz", "rt") as fh:
        inst = {r["key"]: r for r in map(json.loads, fh)}
    with gzip.open(f"{J1}/m4-witnesses.jsonl.gz", "rt") as fh:
        wit = {r["key"]: r for r in map(json.loads, fh)}
    res = {}
    for i in range(20):
        k = f"S3-U400:{i}"
        fs = mini.descend_s3(inst[k]["x_R"], 306147)
        ehex_ok = mini.decode_ehex(inst[k]["E_hex"]) == fs
        M4 = mini.m4_rows(fs)
        lam = mini.hex_to_bits(wit[k]["lambda_hex"])
        vals = mini.matmul2(lam[None, :], M4.T)[0]
        res[k] = {"E_hex_equals_own_descent": ehex_ok, "rows_nonzero_under_lambda": int(vals.sum()),
                  "lambda_of_1": int(lam[6195]), "valid_witness": bool(vals.sum() == 0 and lam[6195] == 1)}
        print(k, res[k], flush=True)
    out = {"task": "TASK-20260926-f50294", "kind": "declared third check (CP-7), 20 archived systems",
           "systems": res, "all_valid": all(v["valid_witness"] and v["E_hex_equals_own_descent"] for v in res.values())}
    json.dump(out, open(outp, "w"), indent=1)
    print("all_valid", out["all_valid"])


if __name__ == "__main__":
    main()

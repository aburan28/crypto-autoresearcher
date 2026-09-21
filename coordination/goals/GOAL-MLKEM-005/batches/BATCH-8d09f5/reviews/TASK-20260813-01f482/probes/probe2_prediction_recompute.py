#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATOR PROBE 2 -- TASK-20260813-01f482 / BATCH-8d09f5 / GOAL-MLKEM-005

Independently recomputes PREREG-6 section 2.3's frozen prediction directly
from results_relvar.json's own G_REL1.hkz.L7/L11 per-basis arrays. Written
from scratch by the Validator -- does not import measure_hkz_mutation6.py
or trust its R_MC_OUT_0b_prediction_recomputation block.

Also recomputes, independently, s_c^fib(hkz, L7_b5) and s_c^fib(hkz, L11_b30)
from results_relvar.json's own G_VAR.per_candidate.hkz.per_cell block, since
those values are cited by PREREG-6 section 2.1 and used as the comparison
threshold.
"""
import hashlib
import json
import os

REPO_ROOT = "/home/user/crypto-autoresearcher"
RELVAR_PATH = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
               "tasks/TASK-20260809-cda2f6/results_relvar.json")

EXPECTED_SHA256 = "c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d"


def cyclic_maxdiff(vals):
    n = len(vals)
    diffs = [abs(vals[i] - vals[(i + 1) % n]) for i in range(n)]
    mx = max(diffs)
    idx = diffs.index(mx)
    return diffs, mx, idx


def main():
    full_path = os.path.join(REPO_ROOT, RELVAR_PATH)
    with open(full_path, "rb") as fh:
        raw = fh.read()
    sha = hashlib.sha256(raw).hexdigest()
    relvar = json.loads(raw)

    g = relvar["G_REL1"]["hkz"]
    Xa = [row["X_a"] for row in g["L7"]["per_basis"]]
    Xb = [row["X_b"] for row in g["L11"]["per_basis"]]

    diffs_a, max_a, idx_a = cyclic_maxdiff(Xa)
    diffs_b, max_b, idx_b = cyclic_maxdiff(Xb)

    s_c_fib_l7 = relvar["G_VAR"]["per_candidate"]["hkz"]["per_cell"]["L7_b5"]["float_sd"]
    s_c_fib_l11 = relvar["G_VAR"]["per_candidate"]["hkz"]["per_cell"]["L11_b30"]["float_sd"]

    out = {
        "relvar_path": RELVAR_PATH,
        "relvar_sha256_computed": sha,
        "relvar_sha256_matches_declared": sha == EXPECTED_SHA256,
        "L7": {
            "X_a_values": Xa,
            "n_bases": len(Xa),
            "cyclic_adjacent_diffs": diffs_a,
            "max_diff": max_a,
            "argmax_i": idx_a,
            "prereg6_stated_prediction": 0.0665893489077094,
            "matches_prereg6_stated": max_a == 0.0665893489077094,
        },
        "L11": {
            "X_b_values": Xb,
            "n_bases": len(Xb),
            "cyclic_adjacent_diffs": diffs_b,
            "max_diff": max_b,
            "argmax_i": idx_b,
            "prereg6_stated_prediction": 0.00948000985335451,
            "matches_prereg6_stated": max_b == 0.00948000985335451,
        },
        "s_c_fib": {
            "hkz/L7_b5": {
                "recomputed": s_c_fib_l7,
                "prereg6_stated": 0.023888,
                "matches_to_stated_precision": round(s_c_fib_l7, 6) == 0.023888,
            },
            "hkz/L11_b30": {
                "recomputed": s_c_fib_l11,
                "prereg6_stated": 0.003818,
                "matches_to_stated_precision": round(s_c_fib_l11, 6) == 0.003818,
            },
        },
        "predicted_margin": {
            "hkz/L7_b5": max_a / s_c_fib_l7,
            "hkz/L11_b30": max_b / s_c_fib_l11,
        },
    }
    out_path = os.path.join(
        REPO_ROOT,
        "coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/"
        "TASK-20260813-01f482/probes/probe2_prediction_recompute_output.json")
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

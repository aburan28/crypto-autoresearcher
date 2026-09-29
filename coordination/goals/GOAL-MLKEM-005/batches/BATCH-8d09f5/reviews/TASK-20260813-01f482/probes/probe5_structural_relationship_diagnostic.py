#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATOR PROBE 5 -- TASK-20260813-01f482 / BATCH-8d09f5 / GOAL-MLKEM-005

ADDITIONAL VALIDATOR-ONLY DIAGNOSTIC. NOT part of PREREG-6's frozen
measurement, computes NOTHING new about any lattice, injects no new defect,
runs no new reduction, and asserts no claim about T-MUTCTRL-* firing for any
shift other than the one PREREG-6 actually specifies ((i+1) % 8). This is a
cheap, closed-form diagnostic computed entirely from already-archived,
already-reviewed results_relvar.json data (the SAME data source PREREG-6
section 2.3 itself uses to state its own prediction), addressing the
dispatcher's checklist item 5: is the predicted D_route_mut structurally
related to s_c^fib in a way that could make "detection" close to guaranteed
regardless of the SPECIFIC injected defect's connection to a real
shared-code bug?

Two checks:

(1) For hkz/L7_b5 and hkz/L11_b30 (the 2 cells PREREG-6 actually covers),
    compute what D_route_shift(k) WOULD be predicted to be (by the same
    HEURISTIC-M1 logic PREREG-6 section 2.3 uses) for EVERY possible cyclic
    shift k=1..7, not just the k=1 PREREG-6 chose, and check whether
    detection (predicted D > s_c^fib) would hold for every one of them.
    This tests whether "detection" is a generic property of ANY
    basis-mislabeling shift at this cell, not specific to k=1.

(2) Confirm the closed-form identity: s_c^fib IS LITERALLY
    np.std(same 8-point per-basis array, ddof=1) -- the same array whose
    cyclic-adjacent max difference is PREREG-6's own predicted
    D_route_mut -- by direct comparison against measure_relvar.py's own
    source computation (line ~609: "float_sd": float(np.std(vals,
    ddof=1))), confirming this is not a coincidental resemblance but the
    literal same computation applied to the same sample.
"""
import json
import numpy as np

RELVAR_PATH = ("/home/user/crypto-autoresearcher/coordination/goals/"
               "GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/"
               "TASK-20260809-cda2f6/results_relvar.json")


def cyclic_shift_maxdiff(vals, k):
    n = len(vals)
    return max(abs(vals[i] - vals[(i + k) % n]) for i in range(n))


def main():
    relvar = json.load(open(RELVAR_PATH))
    g = relvar["G_REL1"]["hkz"]
    gvar = relvar["G_VAR"]["per_candidate"]["hkz"]["per_cell"]

    out = {}
    for cell, lat, field, beta in [
        ("hkz/L7_b5", "L7", "X_a", 5),
        ("hkz/L11_b30", "L11", "X_b", 30),
    ]:
        vals = [row[field] for row in g[lat]["per_basis"]]
        s_c_fib = gvar["%s_b%d" % (lat, beta)]["float_sd"]
        sd_direct = float(np.std(vals, ddof=1))

        per_shift = {}
        for k in range(1, 8):
            d_pred = cyclic_shift_maxdiff(vals, k)
            per_shift[k] = {
                "predicted_D_route_shift_k": d_pred,
                "margin_vs_s_c_fib": d_pred / s_c_fib,
                "would_be_DETECTED": d_pred > s_c_fib,
            }
        n_detected = sum(1 for v in per_shift.values() if v["would_be_DETECTED"])

        out[cell] = {
            "s_c_fib_declared": s_c_fib,
            "s_c_fib_recomputed_as_np_std_ddof1_of_same_8pt_sample": sd_direct,
            "identity_confirmed": abs(s_c_fib - sd_direct) < 1e-15,
            "sample_range_max_minus_min": max(vals) - min(vals),
            "per_shift_k_1_to_7": per_shift,
            "n_of_7_possible_shifts_that_would_be_DETECTED": n_detected,
            "prereg6_chosen_shift": 1,
            "prereg6_chosen_shift_would_be_DETECTED":
                per_shift[1]["would_be_DETECTED"],
        }

    out["diagnostic_conclusion"] = (
        "This diagnostic is NOT part of PREREG-6's frozen measurement and "
        "asserts no T-MUTCTRL-* branch for any shift other than k=1 (the "
        "one PREREG-6 actually specifies and the lead actually ran). It is "
        "offered only to characterize, using already-archived data and no "
        "new reduction, how GENERIC the predicted-detection outcome is "
        "across the full space of possible index-shift defects at these 2 "
        "cells, bearing on whether 'detection' reflects something specific "
        "to the chosen defect's interaction with shared code, or a generic "
        "property of comparing an 8-point sample's own dispersion (range-"
        "like statistic) against that SAME sample's own standard "
        "deviation."
    )

    out_path = (
        "/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/"
        "batches/BATCH-8d09f5/reviews/TASK-20260813-01f482/probes/"
        "probe5_structural_relationship_diagnostic_output.json")
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

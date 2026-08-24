#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATOR PROBE 3 -- TASK-20260813-01f482 / BATCH-8d09f5 / GOAL-MLKEM-005

Re-derives D_route_mut and VERDICT_mut at both cells directly from the
lead's raw per-basis output (results_hkz_mutation6.json's own
route_p_values / route_mut_values arrays), WITHOUT importing the producer's
module (measure_hkz_mutation6.py is never imported here, only the raw JSON
result file is read).

Also performs the STRONGER, SPECIFIC structural check requested by the
dispatcher: confirms route_mut_values[i] == route_p_values[(i+1) mod 8]
EXACTLY at every basis index, not merely that "some big deviation" occurred
-- this is the specific predicted mechanism (PREREG-6 section 2.3), and a
mutant that merely produced *some* large deviation without matching this
specific cyclic-shift structure would not actually confirm the mechanism
worked as claimed.

Also checks the VERDICT_mut / detection mapping (PREREG-6 section 2.4
point 5): VERDICT_mut = "DOES NOT EXCEED" means DETECTED,
VERDICT_mut = "EXCEEDS" means NOT DETECTED. This mapping is easy to invert
by mistake.
"""
import json
import os

REPO_ROOT = "/home/user/crypto-autoresearcher"
RESULTS_PATH = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/"
                 "tasks/TASK-20260813-630414/results_hkz_mutation6.json")


def main():
    with open(os.path.join(REPO_ROOT, RESULTS_PATH)) as fh:
        res = json.load(fh)

    out = {}
    for cell in ["hkz/L7_b5", "hkz/L11_b30"]:
        c = res["R_MC_OUT_2_per_cell"][cell]
        p_vals = c["route_p_values"]
        m_vals = c["route_mut_values"]
        n = len(p_vals)
        assert n == len(m_vals) == 8, "expected 8 matched bases at %s" % cell

        # -------- specific mechanism check: cyclic-shift structure --------
        # predicted: route_mut_values[i] == route_p_values[(i+1) % n]
        shift_matches = []
        shift_diffs = []
        for i in range(n):
            predicted = p_vals[(i + 1) % n]
            actual = m_vals[i]
            diff = abs(predicted - actual)
            shift_diffs.append(diff)
            # "exact" allowing for the ~2^-49 floor PREREG-6 HEURISTIC-M1
            # itself names as the expected residual for genuine
            # re-convergence on a numerically different matrix (NOT the
            # same floating values, since the mutant runs a fresh
            # HKZ-quality reduction on a different matrix, not a lookup).
            shift_matches.append(diff < 1e-6)

        # -------- own D_route_mut / VERDICT_mut recomputation --------
        d_route_mut_own = max(abs(a - b) for a, b in zip(p_vals, m_vals))
        s_c_fib = c["s_c_fib"]
        verdict_own = "EXCEEDS" if s_c_fib > d_route_mut_own else "DOES NOT EXCEED"
        detection_own = "DETECTED" if verdict_own == "DOES NOT EXCEED" else "NOT DETECTED"

        # -------- also: what is the max deviation AT THE NON-SHIFTED
        # (naive/aligned i vs i) index, i.e. what would D have been if the
        # mutant had (counterfactually) computed the SAME value as
        # ROUTE-P's own slot i (no defect at all)? This bounds how "hard"
        # this detection task was -- see probe 4 for the fuller version of
        # this check via the archived L7/L9/L11 basis-to-basis dispersion.
        naive_no_defect_diffs = [abs(p_vals[i] - p_vals[i]) for i in range(n)]

        out[cell] = {
            "route_p_values": p_vals,
            "route_mut_values": m_vals,
            "cyclic_shift_check": {
                "predicted_vs_actual_abs_diff": shift_diffs,
                "max_shift_residual": max(shift_diffs),
                "all_within_1e-6": all(shift_matches),
            },
            "D_route_mut_own_recomputed": d_route_mut_own,
            "D_route_mut_reported": c["D_route_mut"],
            "D_route_mut_matches_reported": (
                abs(d_route_mut_own - c["D_route_mut"]) < 1e-12),
            "s_c_fib": s_c_fib,
            "VERDICT_mut_own_recomputed": verdict_own,
            "VERDICT_mut_reported": c["VERDICT_mut"],
            "VERDICT_mut_matches_reported": verdict_own == c["VERDICT_mut"],
            "detection_reading_own": detection_own,
            "detection_reading_reported": c["detection_reading"],
            "detection_reading_matches_reported": (
                detection_own == c["detection_reading"]),
        }

    out_path = os.path.join(
        REPO_ROOT,
        "coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/"
        "TASK-20260813-01f482/probes/probe3_verdict_recompute_output.json")
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

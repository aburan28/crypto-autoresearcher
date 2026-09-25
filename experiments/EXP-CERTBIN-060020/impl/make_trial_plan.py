#!/usr/bin/env python3
"""Write experiments/EXP-CERTBIN-060020/trial-plan-v1.json from the frozen
specification alone (execution.trial_plan_rule): input paths, literal
parameters, arms, seeds, slot orders, keep rules, quotas and caps, phases,
output paths and the exact power table. No closure value and no draw.

    python3 make_trial_plan.py --spec SPEC --out PLAN
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os

import yaml

import common as C
import stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if os.path.exists(args.out):
        raise SystemExit(f"refusing to overwrite {args.out}")
    spec_bytes = open(args.spec, "rb").read()
    spec = yaml.safe_load(spec_bytes)["experiment"]
    assert spec["status"] == "approved" and spec["approved_by"] and spec["version"] == 1
    lp = spec["inputs"]["literal_parameters"]
    seeds = spec["replication"]["seeds"]
    assert seeds == list(C.SEEDS.values()), "seed order differs from impl constants"
    for k, v in [("A", C.A), ("B", C.B), ("order", C.ORDER), ("h", C.H), ("q", C.Q), ("k_Q", C.K_Q)]:
        assert int(lp[k]) == v, k
    assert list(lp["P"]) == list(C.P_PT) and list(lp["Q"]) == list(C.Q_PT)
    plan = {
        "experiment_id": C.EXPERIMENT_ID,
        "plan_version": 1,
        "written_from": {"specification": os.path.relpath(args.spec, C.ROOT),
                         "specification_sha256": hashlib.sha256(spec_bytes).hexdigest(),
                         "specification_version": spec["version"]},
        "written_utc": C.utc_now(),
        "rule": spec["execution"]["trial_plan_rule"],
        "inputs": {"files": spec["inputs"]["files"], "code_inputs": spec["inputs"]["code_inputs"],
                   "reference_text_inputs": spec["inputs"]["reference_text_inputs"]},
        "literal_parameters": {"n": 19, "modulus": "t^19 + t^5 + t^2 + t + 1", "modulus_int": C.MODULUS,
                               "l": 10, "nv": 20, "neq": 19, "A": C.A, "B": C.B, "order": C.ORDER, "h": C.H,
                               "q": C.Q, "P": list(C.P_PT), "Q": list(C.Q_PT), "k_Q": C.K_Q, "Tr_A": C.TR_A,
                               "tau_reading": C.TAU_READING},
        "seeds": {k: v for k, v in C.SEEDS.items()},
        "generator_rule": spec["instance_sets"]["generator_rule"],
        "arms": {
            "S3-PRIMARY": {"seed": C.SEEDS["S3-PRIMARY"], "quota": {"S3-U400": 400, "S3-SAT100": 100},
                           "cap_attempts": 5000, "draw_rule": spec["instance_sets"]["S3-PRIMARY"]["draw_rule"],
                           "keep_rule": spec["instance_sets"]["S3-PRIMARY"]["keep_rule"]},
            "N-CONV19": {"seed": C.SEEDS["N-CONV19"], "slots": "the 200 lowest-draw-order S3-U400 systems, slot i = S3-U400:i",
                         "satisfiable_slots": "0..49", "attempts_per_slot": 256,
                         "draw_rule": spec["instance_sets"]["N-CONV19"]["drawn_part"],
                         "keep_rule": spec["instance_sets"]["N-CONV19"]["keep_rule"]},
            "N-ELL19": {"seed": C.SEEDS["N-ELL19"], "quota": {"unsat": 200, "sat": 50}, "cap_draws": 20000,
                        "draw_rule": spec["instance_sets"]["N-ELL19"]["draw_rule"],
                        "keep_rule": spec["instance_sets"]["N-ELL19"]["keep_rule"]},
            "N-F219": {"seed": C.SEEDS["N-F219"], "quota": {"unsat": 200, "sat": 50}, "cap_draws": 20000,
                       "draw_rule": spec["instance_sets"]["N-F219"]["draw_rule"],
                       "keep_rule": spec["instance_sets"]["N-F219"]["keep_rule"]},
            "N-AFF19": {"seed": C.SEEDS["N-AFF19"], "families": 5, "quota_per_family": {"unsat": 40, "sat": 10},
                        "draw_rule": spec["instance_sets"]["N-AFF19"]["draw_rule"],
                        "keep_rule": spec["instance_sets"]["N-AFF19"]["keep_rule"]},
            "F-RANDX19": {"seed": C.SEEDS["F-RANDX19"], "strata": ["X2E", "XE-NOT-2E", "TWIST"],
                          "quota_per_stratum": 200, "cap_attempts": 30000,
                          "draw_rule": spec["instance_sets"]["F-RANDX19"]["draw_rule"],
                          "keep_rule": spec["instance_sets"]["F-RANDX19"]["keep_rule"]},
        },
        "sizes_expected": spec["instance_sets"]["sizes_expected"],
        "sizes_expected_arithmetic_note": ("400 + 100 + 4 x (200 + 50) + 3 x 200 = 2100; the specification text "
                                           "says 2150. Recorded as an observation about the text; the quotas above "
                                           "are the binding per-arm values."),
        "executor_interpretations": [
            "E_sha256 = sha256 of the compact JSON list of the 19 lowercase E_hex strings.",
            "S3-PRIMARY duplicate = x_R equal to that of an earlier classified attempt; the loop stops when both quotas are full (checked before each attempt).",
            "N-CONV19 duplicate = equal to an already-kept N-CONV19 system; the generator is consumed slot by slot.",
            "N-ELL19 / N-F219 duplicate = equal to an earlier non-duplicate draw of the same stream.",
            "N-AFF19 'non-degenerate S3-PRIMARY attempts' = the classified attempts (R != O, x_R >= 1024, not a duplicate), in draw order; duplicates are per family.",
            "F-RANDX19 rejection order: degenerate, duplicate (of any earlier non-degenerate draw), S3-PRIMARY collision (any primary attempt with R != O).",
            "Instance key = '<ARM>:<i>' with i the running index of the kept system within the arm in keep order (pooled over roles, families and strata); role, slot, family and stratum are separate fields.",
            "C-NONREF control set = the first 5 (by key order) unsatisfiable systems W_4 does not refute in each of N-CONV19, N-ELL19, N-F219, N-AFF19 and F-RANDX19.",
            "C-BACKEND / C-LIT 'every arm' = S3-U400, N-CONV19, N-ELL19, N-F219, N-AFF19 and each F-RANDX19 stratum.",
        ],
        "phases": spec["execution"]["phases"],
        "closures": {"M_3": "Closure(20, 3, 19).macaulay_closure", "M_4": "Closure(20, 4, 19).macaulay_closure",
                     "W_4": "Closure(20, 4, 19).w_closure", "R'_3": "Closure(19, 3, 19).macaulay_closure",
                     "R'_4": "Closure(19, 4, 19).macaulay_closure", "W'_4": "Closure(19, 4, 19).w_closure",
                     "dimensions_C-FIX": {"M_3": [399, 1351], "M_4": [4009, 6196], "R'_3": [380, 1160], "R'_4": [3629, 5036]}},
        "watchdogs": {"run_seconds": 172800, "per_system_closure_seconds": 3600},
        "resources": {"memory_cap_gb": 3, "CRYPTO_AR_GF2_THREADS": "2 (dispatch note; <= 3)", "OPENBLAS_NUM_THREADS": 2,
                      "processes": 1},
        "output_paths": spec["required_artifacts"],
        "power_table": stats.power_table(),
    }
    with open(args.out, "w") as f:
        json.dump(plan, f, indent=1, sort_keys=True)
        f.write("\n")
    print(hashlib.sha256(open(args.out, "rb").read()).hexdigest())


if __name__ == "__main__":
    main()

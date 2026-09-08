#!/usr/bin/env python3
"""C2 calibration run (amendment v2 C1/C2/C3; v3 two-part C2 = C2a + C2b;
combination_rule_for_C2).  A NEW run record: T4 and comparator and POS-A,
six rungs, pre-shuffle plus 8 NULL-2 shuffles each, reusing the stage-cache
enumeration.

Gates (stated BEFORE scoring, per combination_rule_for_C2):
  C1  : rho_T4 = max(8 NULL-2 post A_noDC(T4)) / pre A_noDC(T4) in
        [0.70, 1.10] at every rung.  NON-BLOCKING qualitative floor.
  C2a : max(8 NULL-2 post A_noDC(comparator)) / pre A_noDC(comparator)
        <= 0.5 at every rung.  DIAGNOSTIC ONLY (NOT blocking) -- the V3-RA-2
        synthetic power check (power_check_results.yaml) showed C2a's power
        is not achieved (separation 0/20 at every rung), so per the
        combination rule C2a is reported but does not gate C2.
  C2b : max(8 NULL-2 post A_noDC(POS-A)) / pre A(POS-A) (= 2/pi exactly)
        <= 0.10 at every rung.  BLOCKING.  C2 passes iff C2b passes.

POS-A = (-1)^k: the stage-cache arrays are indexed by the discrete-log
coordinate k (the k-th subgroup point), so POS-A[k] = (-1)^k.  POS-A reads k
BY DESIGN (specification.yaml licenses POS-A/POS-B/NULL-1 to read k).

Run (from the experiment root):
    EXP_RUN_ID=RUN-ECDLP-56ee42-CAL PYTHONPATH=implementation \
        python3 implementation/calibration_c2.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
import estimator as E

_RUN_ID = os.environ.get("EXP_RUN_ID", "RUN-ECDLP-56ee42-CAL")
BASE_SEED = 0x56EE42
NULL2_SHUFFLES = 8
ARM_INDEX = {"T4": 3, "COMPARATOR": 4, "POS-A": 5}
LADDER = [
    {"T": 17, "p": 131101, "N": 131113},
    {"T": 19, "p": 524309, "N": 525361},
    {"T": 21, "p": 2097169, "N": 2098321},
    {"T": 23, "p": 8388617, "N": 8391797},
    {"T": 25, "p": 33554473, "N": 33557891},
    {"T": 27, "p": 134217757, "N": 134234689},
]


def main() -> None:
    t_start = time.time()
    out = {
        "stage": "C2-calibration",
        "description": ("C2 calibration: T4 (C1), comparator (C2a, diagnostic "
                        "only), POS-A (C2b, blocking); six rungs, pre-shuffle "
                        "+ 8 NULL-2 shuffles each, stage-cache reuse"),
        "combination_rule_regime": ("C2a is DIAGNOSTIC ONLY (NOT blocking): "
                                    "the V3-RA-2 synthetic power check "
                                    "(power_check_results.yaml) showed "
                                    "separation 0/20 at every rung, so per "
                                    "combination_rule_for_C2 C2's pass/fail "
                                    "rests on C2b alone.  Stated BEFORE any "
                                    "gate is scored."),
        "steps": {},
    }

    c1_results, c2a_results, c2b_results = [], [], []
    for rung in LADDER:
        T, p, n = rung["T"], rung["p"], rung["N"]
        xs = np.load(f"runs/stage-cache/rung_T{T}_x.npy")
        # The three statistics (all length-n arrays indexed by k).
        v_t4 = E.popcount_mod4_array(xs).astype(np.float64)
        v_comp = E.top_bit_fiber_array(xs, p).astype(np.float64)
        k = np.arange(n, dtype=np.int64)
        v_posa = (1 - 2 * (k % 2)).astype(np.float64)  # (-1)^k

        rung_out = {}
        for name, v, arm in [("T4", v_t4, "T4"),
                             ("COMPARATOR", v_comp, "COMPARATOR"),
                             ("POS-A", v_posa, "POS-A")]:
            A_pre = E.A_noDC_of_v(v, n)
            posts, seeds = [], []
            for s in range(NULL2_SHUFFLES):
                seed = BASE_SEED + 1000 + 10 * ARM_INDEX[arm] + s
                seeds.append(seed)
                v_sh = E.null2_shuffle(v, n, seed)
                posts.append(E.A_noDC_of_v(v_sh, n))
            ratio = max(posts) / A_pre
            rung_out[name] = {
                "A_noDC_pre": A_pre,
                "A_noDC_post_all": posts,
                "A_noDC_post_max": max(posts),
                "ratio": ratio,
                "null2_seeds_applied": seeds,
            }
            print(f"T={T} {name}: pre={A_pre:.6g} post_max={max(posts):.6g} "
                  f"ratio={ratio:.6g}", file=sys.stderr)
        out["steps"][f"T{T}"] = rung_out

        c1_results.append({"T": T, "rho_T4": rung_out["T4"]["ratio"]})
        c2a_results.append({"T": T, "ratio": rung_out["COMPARATOR"]["ratio"]})
        c2b_results.append({"T": T, "ratio": rung_out["POS-A"]["ratio"]})

    # Gates.
    c1_pass = all(0.70 <= r["rho_T4"] <= 1.10 for r in c1_results)
    c2a_pass = all(r["ratio"] <= 0.5 for r in c2a_results)  # diagnostic only
    c2b_pass = all(r["ratio"] <= 0.10 for r in c2b_results)  # BLOCKING
    c2_pass = c2b_pass  # combination rule: C2 passes iff C2b passes

    out["steps"]["C1"] = {"results": c1_results, "gate": "rho_T4 in [0.70,1.10]",
                          "blocking": False, "pass": c1_pass}
    out["steps"]["C2a"] = {"results": c2a_results, "gate": "ratio <= 0.5",
                           "blocking": False,
                           "status": "DIAGNOSTIC ONLY (power not achieved)",
                           "pass": c2a_pass}
    out["steps"]["C2b"] = {"results": c2b_results, "gate": "ratio <= 0.10",
                           "blocking": True, "pass": c2b_pass}
    out["gates"] = {"C1": c1_pass, "C2a_diagnostic": c2a_pass,
                    "C2b_blocking": c2b_pass, "C2_overall": c2_pass}
    out["validity"] = "valid" if c2_pass else "gate_failure"
    out["validity_reason"] = ("C2b (blocking) passed" if c2_pass else
                              f"C2b (blocking) failed: "
                              f"{[r for r in c2b_results if r['ratio'] > 0.10]}")
    out["seeds"] = {
        "base_seed": BASE_SEED,
        "base_seed_hex": hex(BASE_SEED),
        "arm_index": ARM_INDEX,
        "null2_shuffles": NULL2_SHUFFLES,
        "null2_mechanism": ("numpy default_rng (PCG64), seeded with the 64-bit "
                            "integer 0x56EE42 + 1000 + 10*arm_index + "
                            "shuffle_index masked to 64 bits"),
        "null2_seeds_per_arm": {
            arm: [BASE_SEED + 1000 + 10 * ARM_INDEX[arm] + s
                  for s in range(NULL2_SHUFFLES)]
            for arm in ARM_INDEX},
    }
    out["wall_clock_seconds"] = round(time.time() - t_start, 2)

    out_path = Path(f"runs/{_RUN_ID}/raw-result.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(f"C2 calibration complete in {out['wall_clock_seconds']}s",
          file=sys.stderr)
    print(json.dumps({"gates": out["gates"], "validity": out["validity"]},
                     indent=2))


if __name__ == "__main__":
    main()

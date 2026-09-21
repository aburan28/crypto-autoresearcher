#!/usr/bin/env python3
"""R6: augmentation scan + null objects (seed 760711).

Frozen protocol fields: per class d of the constructed instance's coset,
exact integer scan over u = num/den, |num| <= 10^3, 1 <= den <= 20,
gcd(num,den) = 1 (~4 x 10^4 points per class), test s(u) = d * square;
8 seeded random quartics of MATCHED height/coefficient bit-size (degree 3-4,
nonsingular), scanned with the identical box and test over the instance's 4
NON-FORCED class values; one-sided Fisher exact test (alpha = 0.05) on
4 constructed non-forced cells vs 32 null cells; single pass, no re-scan of
hits, no widening; the test is computed once on the frozen yield table.

If the arm-B run produced no constructed instance, there is no matched-shape
source and F6 has no inputs: the run reports not_evaluable honestly (the
null scan is not run against unmatched shapes).

Observations only; interprets nothing; changes no status.
"""

import json
import math
import os
import random
import sys
import traceback
from fractions import Fraction as Fr

import ecrank_engine as E
import run_common as RC

RUN_ID = "RUN-ECRANK-76a70d-R6-scan-null"
SEED = 760711
NMAX, DMAX = 1000, 20
ALPHA = 0.05
ARM_B_RAW = os.path.join(RC.EXP_DIR, "runs",
                         "RUN-ECRANK-76a70d-R3-armB", "raw-result.json")


def box_size():
    n = 0
    for dd in range(1, DMAX + 1):
        for num in range(-NMAX, NMAX + 1):
            if num != 0 and math.gcd(abs(num), dd) == 1:
                n += 1
    return n


def bits(x):
    return max(abs(Fr(x).numerator).bit_length(),
               Fr(x).denominator.bit_length())


def make_null_quartic(rng, s_ref):
    """Seeded random quartic with coefficient bit-sizes matched to s_ref
    (Fraction coefficient list); degree matched; nonsingular (exact disc)."""
    deg = len(s_ref) - 1
    for _attempt in range(2000):
        coefs = []
        for j, c in enumerate(s_ref):
            bj = bits(c) if j < deg else bits(s_ref[deg])
            hi = max(2, 1 << bj)
            num = rng.choice([1, -1]) * rng.randint(1, hi)
            den = rng.randint(1, hi)
            coefs.append(Fr(num, den))
        if coefs[deg] == 0:
            continue
        if E.poly_disc(coefs) == 0:
            continue
        return coefs
    return None


def main():
    params = {"run_kind": "augmentation_scan_plus_null_objects",
              "seed": SEED, "box": {"nmax": NMAX, "dmax": DMAX},
              "alpha": ALPHA, "arm_b_raw": ARM_B_RAW,
              "cells": "4 constructed non-forced vs 32 null (8 quartics x 4)"}
    run_dir, header, t0 = RC.open_run(RUN_ID, sys.argv, params)
    E.start_counting()
    raw = {"parameters": params}
    try:
        arm_b_path = os.path.join(RC.REPO_ROOT, ARM_B_RAW)
        if not os.path.exists(arm_b_path):
            RC.finalize_run(run_dir, header, t0, "completed_not_evaluable",
                            "arm-B raw-result.json absent: no constructed "
                            "instance source for the matched-shape scan; F6 "
                            "inputs do not exist", raw)
            print(json.dumps({"run_id": RUN_ID,
                              "status": "completed_not_evaluable"}))
            return 0
        arm_b = json.load(open(arm_b_path))
        found = arm_b.get("found_instances", [])
        if not found:
            raw["arm_b_found"] = 0
            RC.finalize_run(run_dir, header, t0, "completed_not_evaluable",
                            "arm-B found zero constructed instances: no "
                            "matched-shape source; F6 not evaluable "
                            "(honest report, inert)", raw)
            print(json.dumps({"run_id": RUN_ID,
                              "status": "completed_not_evaluable"}))
            return 0
        rec0 = found[0]
        inst = rec0["instance"]
        s = [Fr(c) for c in inst["s"]]
        dpat = [int(d) for d in inst["d_pattern"]]
        forced_classes = sorted(set(dpat))
        # the instance's coset: recompute from the arm record
        coset_rec = arm_b["arm_cosets"][rec0["stream"]]
        member_values = sorted(coset_rec["values"])
        nonforced = [d for d in member_values if d not in forced_classes]
        raw["instance_source"] = {
            "stream": rec0["stream"], "b_index": rec0["b_index"],
            "draw_index": rec0["draw_index"], "H_level": rec0["H_level"],
            "deg_s": inst["deg_s"], "height_s": inst["height_s"],
            "coefficient_bits": [bits(c) for c in s]}
        raw["forced_classes"] = forced_classes
        raw["nonforced_classes"] = nonforced
        raw["coset_member_values"] = member_values

        nb = box_size()
        raw["box_points_per_cell"] = nb

        # constructed scan: every class of the coset (full record); Fisher
        # cells are the 4 non-forced ones.
        constructed_cells = {}
        for d in member_values:
            hits = E.scan_class(s, d, NMAX, DMAX)
            constructed_cells[str(d)] = {
                "n_hits": len(hits),
                "forced": d in forced_classes,
                "hits_sample": hits[:20]}
        raw["constructed_cells"] = constructed_cells
        a = sum(constructed_cells[str(d)]["n_hits"] for d in nonforced)

        # null objects: 8 seeded quartics of matched shape
        rng = random.Random(SEED)
        nulls = []
        for q in range(8):
            s_null = make_null_quartic(rng, s)
            if s_null is None:
                nulls.append({"quartic": None, "reason": "generation_failed"})
                continue
            cells = {}
            for d in nonforced:
                hits = E.scan_class(s_null, d, NMAX, DMAX)
                cells[str(d)] = {"n_hits": len(hits), "hits_sample": hits[:10]}
            nulls.append({
                "quartic": [str(c) for c in s_null],
                "deg": len(s_null) - 1,
                "disc": str(E.poly_disc(s_null)),
                "coefficient_bits": [bits(c) for c in s_null],
                "cells": cells,
                "total_hits": sum(c["n_hits"] for c in cells.values())})
        raw["null_objects"] = nulls
        c_hits = sum(x["total_hits"] for x in nulls if x.get("quartic"))
        n_null_cells = 4 * sum(1 for x in nulls if x.get("quartic"))

        fisher = None
        if n_null_cells:
            p_fr, p_fl = E.fisher_one_sided(a, 4 * nb, c_hits, n_null_cells * nb)
            fisher = {"a_constructed_hits": a, "n1_trials": 4 * nb,
                      "c_null_hits": c_hits, "n2_trials": n_null_cells * nb,
                      "p_value_exact": str(p_fr), "p_value_float": p_fl,
                      "alpha": ALPHA,
                      "F6_signal_p_below_alpha": bool(p_fl < ALPHA)}
        raw["fisher_one_sided"] = fisher
        RC.finalize_run(run_dir, header, t0, "completed",
                        "scan + null objects executed on the frozen yield "
                        "table (single pass, no widening)", raw)
        print(json.dumps({"run_id": RUN_ID, "status": "completed",
                          "constructed_nonforced_hits": a,
                          "null_hits": c_hits,
                          "fisher_p": (fisher or {}).get("p_value_float")},
                         indent=1))
        return 0
    except Exception:
        tb = traceback.format_exc()
        raw["exception_traceback"] = tb
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "exception during scan run (asserts nothing about "
                        "the hypothesis)", raw)
        print(tb)
        return 2


if __name__ == "__main__":
    sys.exit(main())

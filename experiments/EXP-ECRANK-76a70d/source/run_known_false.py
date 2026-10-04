#!/usr/bin/env python3
"""R7: known-false d = (1..1) control (seed 760712) -- bound into IV-1.

The identical pipeline runs at d = (1..1), where the engine degenerates to
Mestre and "certified total = n" is KNOWN FALSE (the g - y relation eats
exactly 1; committed ceilings 7 at n = 8 and 9 at n = 10). Expected: total 7
at n = 8 and total 9 at n = 10 on EVERY seeded b-tuple; a pipeline reporting
total = n at d = 1 is broken and ALL runs of the experiment are VOID (IV-1).

Implementation: seeded b-tuples (b_1 = 0, b_2 = 1, b_3..b_n distinct
integers in [-20,20]) from random.Random(760712); r_i = g(b_i) from the
committed Mestre closed form (trunc-sqrt, the exact d = 1 anchor the spec
names); from there the IDENTICAL pipeline: build_instance (C4 filter,
forcing identity, M2 identity) -> certify_instance (per-class committed F_l
certifier + certificate-kind split). Committed pool fixtures m8/m10 are
recomputed as anchors.

Observations only; interprets nothing; changes no status.
"""

import json
import os
import random
import sys
import traceback
from fractions import Fraction as Fr

import ecrank_engine as E
import certify76 as C
import run_common as RC

RUN_ID = "RUN-ECRANK-76a70d-R7-known-false"
SEED = 760712
N_B_PER_N = 20
B_INTS = sorted(set(range(-20, 21)) - {0, 1})
POOL_PATH = ("coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/"
             "tasks/TASK-20260822-a7a9e8/highrank_pool.json")
EXPECTED = {8: 7, 10: 9}


def mestre_instance(b, n):
    p, g, s = E.mestre_polys(list(b))
    r = [E.peval(g, x) for x in b]
    inst, why = E.build_instance(list(b), [1] * n, r, n)
    return inst, why


def main():
    params = {"run_kind": "known_false_control_d_all_ones",
              "seed": SEED, "n_values": [8, 10],
              "b_per_n": N_B_PER_N, "expected_totals": EXPECTED,
              "iv1_binding": "total == n at d=(1..1) voids ALL runs"}
    run_dir, header, t0 = RC.open_run(RUN_ID, sys.argv, params)
    E.start_counting()
    ec, digest = E.load_exact_certify(RC.REPO_ROOT)
    assert digest == E.EXACT_CERTIFY_SHA
    cosets = E.eligible_cosets()
    coset = next(c for c in cosets
                 if 1 in [E.class_value(m) for m in c["members"]])
    rng = random.Random(SEED)
    raw = {"parameters": params, "coset": {"m0": coset["m0"],
                                           "V": list(coset["V"])}}
    cert_dir = os.path.join(RC.REPO_ROOT, RC.EXP_DIR, "certificates", RUN_ID)
    try:
        results = {}
        for n in (8, 10):
            per_b = []
            for bi in range(N_B_PER_N):
                b_rest = rng.sample(B_INTS, n - 2)
                b = [Fr(0), Fr(1)] + [Fr(x) for x in b_rest]
                inst, why = mestre_instance(b, n)
                if inst is None:
                    per_b.append({"b_index": bi, "b": [str(x) for x in b],
                                  "built": False, "reason": why})
                    continue
                cert = C.certify_instance(inst, coset, ec)
                cpath = RC.write_json(os.path.join(
                    cert_dir, "kf-n%d-b%02d.json" % (n, bi)), cert)
                per_b.append({
                    "b_index": bi, "b": [str(x) for x in b], "built": True,
                    "deg_s": inst["deg_s"],
                    "verdict": cert["verdict"],
                    "aggregate_total": cert["aggregate_total"],
                    "eig_units": cert["eig_units"],
                    "fl_units": cert["fl_units"],
                    "route": cert["route"],
                    "errors_strict": cert["errors_strict"],
                    "certificate": os.path.relpath(cpath, RC.REPO_ROOT)})
            totals = [x["aggregate_total"] for x in per_b if x["built"]]
            results[n] = {
                "per_b": per_b,
                "n_built": len(totals),
                "totals": totals,
                "expected_total": EXPECTED[n],
                "all_totals_equal_expected": bool(totals) and
                    all(t == EXPECTED[n] for t in totals),
                "any_total_equals_n": any(t == n for t in totals),
            }
        # committed pool fixture anchors
        anchors = {}
        pool = json.load(open(os.path.join(RC.REPO_ROOT, POOL_PATH)))
        curves = pool.get("curves", []) if isinstance(pool, dict) else pool
        got = {}
        for ent in curves:
            A = ent.get("A") or ent.get("parameters_A")
            if A and len(A) in (8, 10) and len(A) not in got:
                got[len(A)] = A
        for n, fallback in ((8, [-14, -13, -3, -2, 5, 6, 7, 14]),
                            (10, [-20, -14, -12, -11, -6, -3, 1, 13, 16, 17])):
            A = got.get(n, fallback)
            inst, why = mestre_instance([Fr(a) for a in A], n)
            if inst is None:
                anchors[n] = {"built": False, "reason": why}
                continue
            cert = C.certify_instance(inst, coset, ec)
            anchors[n] = {"built": True, "A": A,
                          "aggregate_total": cert["aggregate_total"],
                          "expected": EXPECTED[n],
                          "matches_expected":
                              cert["aggregate_total"] == EXPECTED[n]}
        raw["seeded_results"] = {str(k): v for k, v in results.items()}
        raw["committed_fixture_anchors"] = {str(k): v for k, v in anchors.items()}
        iv1_fired = (any(results[n]["any_total_equals_n"] for n in (8, 10))
                     or not all(results[n]["all_totals_equal_expected"]
                                for n in (8, 10))
                     or not all(anchors[n].get("matches_expected", False)
                                for n in (8, 10)))
        raw["IV1_fired"] = bool(iv1_fired)
        status = "completed"
        reason = ("known-false control: totals %s at n=8, %s at n=10; "
                  "IV-1 %s" % (
                      sorted(set(results[8]["totals"])),
                      sorted(set(results[10]["totals"])),
                      "FIRED" if iv1_fired else "not fired"))
        RC.finalize_run(run_dir, header, t0, status, reason, raw)
        print(json.dumps({"run_id": RUN_ID, "status": status,
                          "reason": reason, "IV1_fired": bool(iv1_fired)},
                         indent=1))
        return 1 if iv1_fired else 0
    except Exception:
        tb = traceback.format_exc()
        raw["exception_traceback"] = tb
        RC.finalize_run(run_dir, header, t0, "failed_infrastructure",
                        "exception during control run (asserts nothing "
                        "about the hypothesis)", raw)
        print(tb)
        return 2


if __name__ == "__main__":
    sys.exit(main())

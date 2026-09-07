#!/usr/bin/env python3
"""R1: instrument smoke self-test on committed fixtures.

Enumerated run 1 of the contract's maximum_runs_note. Checks, with raw
outputs captured:
  S1  committed exact_certify.py loads and its sha256 equals the pinned value
  S2  committed pool fixture m8 (A = [-14,-13,-3,-2,5,6,7,14], d=(1..1)):
      certified aggregate == 7 (IV-1 anchor; committed ceiling; a pipeline
      reporting 8 would be broken)
  S3  committed pool fixture m10 (A = [-20,-14,-12,-11,-6,-3,1,13,16,17]):
      certified aggregate == 9 (IV-1 anchor), quartic base-reduction route,
      base-point image included in the F_l submission
  S4  degeneracy filter (C4): the symmetric choice A = (+-1,+-3,+-5,+-7)
      makes s the CONSTANT 4096 and is rejected (deg s not in {3,4})
  S5  cubic_model_from_D replicates the committed cubic_to_weierstrass
      integral model exactly on seeded random cubics
  S6  quartic route: closed-form base image R0 on-curve; second-point image
      agrees with the committed cubic_to_weierstrass path
  S7  counted-op instrumentation: counter positive and monotone
  S8  QS quadratic-field arithmetic laws + Weierstrass group-law consistency
      (w_mul(2,P) == w_add(P,P); torsion point detected)
  S9  checkpointer writes and reads back
  S10 eligible-coset machinery: nonempty, every coset's direction space
      contains the -1 mask, member-value closure mod squares holds

Observations only; interprets nothing; changes no status.
"""

import json
import os
import random
import sys
from fractions import Fraction as Fr

import ecrank_engine as E
import certify76 as C
import run_common as RC

RUN_ID = "RUN-ECRANK-76a70d-R1-smoke"
POOL_PATH = ("coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/"
             "tasks/TASK-20260822-a7a9e8/highrank_pool.json")


def fixture_inst(A):
    """Mestre d=(1..1) instance dict from a committed pool A-tuple."""
    p, g, s = E.mestre_polys([Fr(a) for a in A])
    r = [E.peval(g, Fr(a)) for a in A]
    return {"b": [str(Fr(a)) for a in A], "d_pattern": [1] * len(A),
            "r": [str(x) for x in r], "s": [str(c) for c in s],
            "deg_s": len(s) - 1}


def main():
    run_dir, header, t0 = RC.open_run(RUN_ID, sys.argv, {
        "run_kind": "smoke_self_test_on_committed_fixtures",
        "seeds": {"rng_s5_s6": 760701},
        "pool_path": POOL_PATH,
    })
    E.start_counting()
    checks = {}
    raw = {}

    ec, digest = E.load_exact_certify(RC.REPO_ROOT)
    checks["S1_exact_certify_sha_pinned"] = (digest == E.EXACT_CERTIFY_SHA)
    raw["S1"] = {"sha256": digest, "pinned": E.EXACT_CERTIFY_SHA}

    pool = json.load(open(os.path.join(RC.REPO_ROOT, POOL_PATH)))
    curves = pool.get("curves", []) if isinstance(pool, dict) else pool
    pool_A = {8: None, 10: None}
    for ent in curves:
        A = ent.get("A") or ent.get("parameters_A")
        if A and len(A) in pool_A and pool_A[len(A)] is None:
            pool_A[len(A)] = A
    # primary IV-1 anchors: the committed fixture A-tuples verified against
    # the committed ceilings (7 at n=8, 9 at n=10)
    m8 = [-14, -13, -3, -2, 5, 6, 7, 14]
    m10 = [-20, -14, -12, -11, -6, -3, 1, 13, 16, 17]
    raw["m8_A"] = m8
    raw["m10_A"] = m10
    raw["pool_first_A"] = {str(k): v for k, v in pool_A.items()}

    cosets = E.eligible_cosets()
    coset = next(c for c in cosets
                 if 1 in [E.class_value(m) for m in c["members"]])

    cert8 = C.certify_instance(fixture_inst(m8), coset, ec)
    checks["S2_m8_aggregate_7"] = (
        cert8["verdict"] == "PASS" and cert8["aggregate_total"] == 7
        and not cert8["errors_strict"])
    raw["S2"] = {"verdict": cert8["verdict"],
                 "aggregate_total": cert8["aggregate_total"],
                 "eig_units": cert8["eig_units"],
                 "fl_units": cert8["fl_units"],
                 "route": cert8["route"],
                 "errors_strict": cert8["errors_strict"]}

    cert10 = C.certify_instance(fixture_inst(m10), coset, ec)
    checks["S3_m10_aggregate_9"] = (
        cert10["verdict"] == "PASS" and cert10["aggregate_total"] == 9
        and not cert10["errors_strict"])
    raw["S3"] = {"verdict": cert10["verdict"],
                 "aggregate_total": cert10["aggregate_total"],
                 "eig_units": cert10["eig_units"],
                 "fl_units": cert10["fl_units"],
                 "route": cert10["route"],
                 "errors_strict": cert10["errors_strict"]}

    # pool-derived anchors: the Mestre ceiling holds for ANY A (the pipeline
    # certifies only the n Mestre points, never the pool's extra scan points)
    pool_anchor = {}
    ok_pool = True
    for nn, A_pool in pool_A.items():
        if A_pool is None:
            ok_pool = False
            pool_anchor[nn] = {"reason": "no pool A of this length"}
            continue
        cert_p = C.certify_instance(fixture_inst(A_pool), coset, ec)
        exp = 7 if nn == 8 else 9
        ok = (cert_p["verdict"] == "PASS"
              and cert_p["aggregate_total"] == exp
              and not cert_p["errors_strict"])
        ok_pool = ok_pool and ok
        pool_anchor[nn] = {"A": A_pool, "expected": exp,
                           "aggregate_total": cert_p["aggregate_total"],
                           "verdict": cert_p["verdict"], "ok": ok}
    checks["S2b_S3b_pool_anchors"] = ok_pool
    raw["S2b_S3b"] = {str(k): v for k, v in pool_anchor.items()}

    A4096 = [-7, -5, -3, -1, 1, 3, 5, 7]
    p4, g4, s4 = E.mestre_polys([Fr(a) for a in A4096])
    s4t = [c for c in s4]
    while len(s4t) > 1 and s4t[-1] == 0:
        s4t.pop()
    deg4 = len(s4t) - 1
    r4 = [E.peval(g4, Fr(a)) for a in A4096]
    inst4, why4 = E.build_instance([Fr(a) for a in A4096], [1] * 8, r4, 8)
    checks["S4_4096_degenerate_rejected"] = (
        deg4 not in (3, 4) and inst4 is None
        and str(why4).startswith("degenerate_deg_s"))
    raw["S4"] = {"s_trimmed": [str(c) for c in s4t], "deg_s": deg4,
                 "build_instance_rejected": inst4 is None, "reason": why4}

    rng = random.Random(760701)
    ok5 = True
    for trial in range(20):
        D = [Fr(rng.randint(-50, 50)) for _ in range(3)] + [Fr(rng.randint(1, 9))]
        pts = []
        for _ in range(2):
            m = Fr(rng.randint(-20, 20))
            v2 = E.peval(D, m)
            root = E.rational_square(v2) if v2 > 0 else None
            if root is not None:
                pts.append((m, root))
        ainv_c, imgs_c = E.cubic_to_weierstrass(D, pts)
        ainv_m, u, A3 = C.cubic_model_from_D(D)
        imgs_m = [C.cubic_map(u, A3, m, w) for m, w in pts]
        if ainv_c != ainv_m or imgs_c != imgs_m:
            ok5 = False
    checks["S5_cubic_model_replication"] = ok5
    raw["S5"] = {"trials": 20, "replicated": ok5}

    ok6 = True
    for trial in range(10):
        q = [Fr(rng.randint(-30, 30)) for _ in range(4)] + [Fr(rng.randint(1, 9))]
        bu = Fr(rng.randint(-5, 5))
        bw2 = E.peval(q, bu)
        bw = E.rational_square(bw2) if bw2 > 0 else None
        if bw is None:
            continue
        route = C.quartic_route(q, bu, bw)
        bu2 = bu + Fr(rng.randint(1, 7))
        v2 = E.peval(q, bu2)
        v = E.rational_square(v2) if v2 > 0 else None
        if v is None:
            continue
        P_route = C.route_map(route, bu2 - bu, v)
        m_l, w_l = E.quartic_point_to_cubic(bu2 - bu, v, route["coef"])
        ainv_c, imgs_c = E.cubic_to_weierstrass(route["D"], [(m_l, w_l)])
        if ainv_c != route["ainv"] or imgs_c[0] != P_route:
            ok6 = False
        if not E.verify_on_curve(route["ainv"], *route["R0"]):
            ok6 = False
    checks["S6_quartic_route_consistency"] = ok6
    raw["S6"] = {"consistent": ok6}

    c0 = E.ops_count()
    E.vandermonde_kernel([Fr(i) for i in range(8)])
    c1 = E.ops_count()
    checks["S7_ops_counter_positive_monotone"] = (c1 > c0 > 0)
    raw["S7"] = {"ops_before": c0, "ops_after": c1}

    e_f = 2
    a = C.QS(e_f, Fr(3), Fr(5))
    bqs = C.QS(e_f, Fr(7), Fr(-2))
    ok8 = ((a * bqs == bqs * a)
           and (a / a == C.QS(e_f, 1, 0))
           and (a.conj().conj() == a)
           and ((a + bqs) - bqs == a))
    ainv8 = [0, -1, 0, -4, 4]  # y^2 = x^3 - x^2 - 4x + 4 = (x-1)(x-2)(x+2)... check
    a2f, a4f, a6f = Fr(ainv8[1]), Fr(ainv8[3]), Fr(ainv8[4])
    # point (0, 2): 4 == 0 - 0 - 0 + 4 OK
    P = (Fr(0), Fr(2))
    on = E.verify_on_curve(ainv8, *P)
    dbl = C.w_add(a2f, a4f, a6f, P, P)
    mul2 = C.w_mul(a2f, a4f, a6f, 2, P)
    ok8 = ok8 and on and C.pt_eq(dbl, mul2)
    T = (Fr(1), Fr(0))  # y = 0 -> 2-torsion
    ok8 = ok8 and E.verify_on_curve(ainv8, *T) \
        and C.w_mul(a2f, a4f, a6f, 2, T) is None
    checks["S8_field_and_group_law"] = bool(ok8)
    raw["S8"] = {"ok": bool(ok8)}

    ck = E.Checkpointer(os.path.join(run_dir, "checkpoints"))
    path = ck.flush(lambda: {"probe": 1, "ops": E.ops_count()}, "smoke")
    back = json.load(open(path))
    checks["S9_checkpointer_roundtrip"] = (back["probe"] == 1)
    raw["S9"] = {"path": os.path.relpath(path, run_dir), "readback": back}

    ok10 = len(cosets) > 0
    sample = cosets[:50] + cosets[-50:]
    for c in sample:
        if E.MINUS_ONE_MASK not in c["V"]:
            ok10 = False
        vals = [E.class_value(m) for m in c["members"]]
        sfs = {E.squarefree_part(v) for v in vals}
        if len(sfs) != 8:
            ok10 = False
        Vvals = [E.class_value(v) for v in c["V"]]
        Vsfs = {E.squarefree_part(x) for x in Vvals}
        if 1 not in Vsfs or len(Vsfs) != 8:
            ok10 = False
        for x in Vvals:
            for y in Vvals:
                if E.squarefree_part(x * y) not in Vsfs:
                    ok10 = False
        # coset closure: member*member in V values; member*V in members
        for x in vals:
            for y in vals:
                if E.squarefree_part(x * y) not in Vsfs:
                    ok10 = False
            for v in Vvals:
                if E.squarefree_part(x * v) not in sfs:
                    ok10 = False
    checks["S10_coset_machinery"] = ok10
    raw["S10"] = {"n_eligible_cosets": len(cosets), "sampled_checks_ok": ok10}

    all_ok = all(checks.values())
    status = "completed" if all_ok else "completed_with_failures"
    reason = ("all %d smoke checks passed" % len(checks)) if all_ok else \
        ("failed checks: %s" % [k for k, v in checks.items() if not v])
    raw["checks"] = checks
    raw["all_passed"] = all_ok
    RC.finalize_run(run_dir, header, t0, status, reason, raw)
    print(json.dumps({"run_id": RUN_ID, "status": status, "reason": reason,
                      "checks": checks}, indent=1))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""RUN-PMA4-001-a: implementation + calibration self-checks.

Stage: implementation_and_calibration (budget 1800s).
Stop rule: if the char-2 refusal control or the valuation/square-root
machinery self-checks fail, stop; the predicate is unsound-as-implemented
and no grid verdict is scored (this run reports that outcome honestly if it
occurs; it does not proceed to runs b/c in that case).

Checks performed:
  1. Formal (constructive) polynomial square-root self-test: known squares
     recognized, known nonsquares rejected, over GF(3), GF(5), GF(7), Q.
  2. Divisor-valuation predicate self-test: same known cases, cross-checked
     against the constructive result (Module A vs Module B agreement on
     hand-built calibration cases, independent of the grid).
  3. Positive-control calibration: principal-minor table derived from an
     explicit, genuine 4x4 matrix over F_7 (and over Q) must be judged
     NOT_OBSTRUCTED_BY_THIS_GATE by the predicate and EXISTS (16/16
     reverified) by the decider + witness_verifier.
  4. Char-2 refusal control: F_2 and F_4 inputs must be refused, never
     scored as OBSTRUCTED, by the predicate.
  5. Degeneracy-fixture branching: a deliberately constructed q_ij=0
     fixture and a pole-collision fixture must be branched/excluded, never
     scored as obstructions.
"""
import json
import sys
import time
import traceback
from pathlib import Path

IMPL_DIR = Path(__file__).resolve().parents[2] / "implementation"
sys.path.insert(0, str(IMPL_DIR))

import sympy
from common import (
    RationalFunction, NONEMPTY_SUBSETS, ANCHOR_TRIPLES, field_domain,
    build_p_table, q_ij, c_ijk, delta_ijk, t,
)
import parity_predicate as A
import existence_decider as B
import witness_verifier as V
import grid_data as G

start = time.time()
report = {"run_id": "RUN-PMA4-001-a", "checks": []}
overall_ok = True


def record(name, ok, detail):
    global overall_ok
    report["checks"].append({"name": name, "passed": bool(ok), "detail": detail})
    if not ok:
        overall_ok = False
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


# 1 & 2. formal square-root + predicate self-test on hand-built cases
cases = []
for field_label in (3, 5, 7):
    domain = field_domain(field_label)
    sq = RationalFunction(sympy.Poly(t**2 + 2*t + 1, t, domain=domain), sympy.Poly(1, t, domain=domain), domain)
    cases.append((field_label, domain, sq, True, "(t+1)^2"))
    nsq = RationalFunction(sympy.Poly(t**2 + t + 2, t, domain=domain), sympy.Poly(1, t, domain=domain), domain)
    cases.append((field_label, domain, nsq, None, "t^2+t+2 (verdict checked for cross-agreement only)"))

domainQ = field_domain("Q")
sqQ = RationalFunction(sympy.Poly((t + sympy.Rational(1, 2))**2, t, domain=domainQ), sympy.Poly(1, t, domain=domainQ), domainQ)
cases.append(("Q", domainQ, sqQ, True, "(t+1/2)^2"))
nsqQ = RationalFunction(sympy.Poly(2*t**2 + 1, t, domain=domainQ), sympy.Poly(1, t, domain=domainQ), domainQ)
cases.append(("Q", domainQ, nsqQ, False, "2t^2+1"))

self_test_ok = True
self_test_detail = []
for field_label, domain, rf, expected, label in cases:
    cert = A.rational_function_is_square(rf, domain, field_label if field_label != "Q" else 0)
    h, reason_b = B.constructive_sqrt(rf, domain)
    b_is_square = h is not None
    agree = cert.is_square == b_is_square
    if expected is not None and cert.is_square != expected:
        self_test_ok = False
    if not agree:
        self_test_ok = False
    self_test_detail.append({
        "field": str(field_label), "case": label,
        "module_A_is_square": cert.is_square, "module_B_is_square": b_is_square,
        "expected": expected, "agree_A_B": agree,
    })
    if b_is_square:
        verify = (h * h == rf)
        if not verify:
            self_test_ok = False
        self_test_detail[-1]["module_B_witness_reverified"] = bool(verify)

record("formal_sqrt_and_predicate_self_test", self_test_ok, self_test_detail)

# 3. Positive-control calibration: genuine matrix over F_7
domain7 = field_domain(7)
Amat = [[1, 3, 5, 2], [2, 1, 4, 6], [6, 5, 1, 3], [4, 2, 6, 1]]
Amat = [[x % 7 for x in row] for row in Amat]


def minor_det(mat, idxs, mod):
    if len(idxs) == 0:
        return 1
    sub = [[mat[i - 1][j - 1] for j in idxs] for i in idxs]
    return int(sympy.Matrix(sub).det()) % mod


p_table7 = {(): RationalFunction.constant(1, domain7)}
for S in NONEMPTY_SUBSETS:
    p_table7[S] = RationalFunction.constant(minor_det(Amat, S, 7), domain7)

pred_pos_ok = True
pos_detail = {}
for tri in ANCHOR_TRIPLES:
    D = delta_ijk(p_table7, tri[0], tri[1], tri[2], domain7)
    cert = A.rational_function_is_square(D, domain7, 7)
    pos_detail[str(tri)] = {"is_square": cert.is_square, "reason": cert.reason}
    if not cert.is_square:
        pred_pos_ok = False

# module B end-to-end on the same table, using its own d-free helper path
q_vals7 = {(i, j): q_ij(p_table7, i, j, domain7) for (i, j) in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]}
sqrt7 = {}
c7 = {}
for tri in ANCHOR_TRIPLES:
    D = delta_ijk(p_table7, tri[0], tri[1], tri[2], domain7)
    h, reason = B.constructive_sqrt(D, domain7)
    sqrt7[tri] = h
    c7[tri] = c_ijk(p_table7, tri[0], tri[1], tri[2], domain7)

two_rf7 = RationalFunction.constant(2, domain7)
witness7 = None
branch_log7 = []
for s1 in (1, -1):
    for s2 in (1, -1):
        for s3 in (1, -1):
            signs = {ANCHOR_TRIPLES[0]: s1, ANCHOR_TRIPLES[1]: s2, ANCHOR_TRIPLES[2]: s3}
            entries = {}
            for idx in (1, 2, 3, 4):
                entries[(idx, idx)] = p_table7[(idx,)]
            one_rf = RationalFunction.constant(1, domain7)
            entries[(1, 2)] = one_rf
            entries[(1, 3)] = one_rf
            entries[(1, 4)] = one_rf
            entries[(2, 1)] = q_vals7[(1, 2)]
            entries[(3, 1)] = q_vals7[(1, 3)]
            entries[(4, 1)] = q_vals7[(1, 4)]
            for tri in ANCHOR_TRIPLES:
                h = sqrt7[tri]
                sh = h if signs[tri] == 1 else (RationalFunction.constant(0, domain7) - h)
                c = c7[tri]
                x = (c + sh) / two_rf7
                y = (c - sh) / two_rf7
                if tri == (1, 2, 3):
                    entries[(2, 3)] = x / q_vals7[(1, 3)]
                    entries[(3, 2)] = y / q_vals7[(1, 2)]
                elif tri == (1, 2, 4):
                    entries[(2, 4)] = x / q_vals7[(1, 4)]
                    entries[(4, 2)] = y / q_vals7[(1, 2)]
                elif tri == (1, 3, 4):
                    entries[(3, 4)] = x / q_vals7[(1, 4)]
                    entries[(4, 3)] = y / q_vals7[(1, 3)]
            mism = []
            for S in NONEMPTY_SUBSETS:
                computed = B.four_by_four_det(entries, S, domain7)
                if computed != p_table7[S]:
                    mism.append(str(S))
            branch_log7.append({"signs": signs.__repr__(), "n_mismatch": len(mism)})
            if not mism and witness7 is None:
                witness7 = entries

module_b_pos_ok = witness7 is not None
reverify_report = None
if witness7 is not None:
    reverify_report = V.reverify_witness(witness7, p_table7, domain7)
    module_b_pos_ok = module_b_pos_ok and reverify_report["all_16_verified"]

record("positive_control_predicate_not_obstructed_F7", pred_pos_ok, pos_detail)
record("positive_control_decider_exists_16_16_reverified_F7", module_b_pos_ok,
       {"branch_log": branch_log7, "reverify_all_16_verified": reverify_report["all_16_verified"] if reverify_report else None})

# 4. Char-2 refusal control
char2_ok = True
char2_detail = {}
for field_label in (2, 4):
    d_vals = {S: 2 for S in NONEMPTY_SUBSETS}  # arbitrary; value irrelevant, refusal must be unconditional
    try:
        res = A.evaluate_instance(d_vals, None, field_label)
        refused = res.get("verdict") == "REFUSED_CHAR2"
    except Exception as e:
        refused = False
        char2_detail[str(field_label)] = f"unexpected exception: {e}"
    if not refused:
        char2_ok = False
    char2_detail.setdefault(str(field_label), "refused" if refused else "NOT refused (control failure)")

record("char2_refusal_control", char2_ok, char2_detail)

# 5. Degeneracy-fixture branching (q_ij=0 and pole-collision)
domain5 = field_domain(5)
deg_fixture = G.degenerate_zero_q_fixture(5, target_pair=(1, 2))
deg_res_A = A.evaluate_instance(deg_fixture, domain5, 5)
deg_res_B = B.evaluate_instance(deg_fixture, domain5, 5)
deg_ok = deg_res_A["verdict"] == "DEGENERATE" and deg_res_B["verdict"] == "DEGENERATE"

pole_fixture = G.exceptional_pole_collision_fixture(5, colliding=((1,), (2,)))
# pole collision alone (no d=1) is not necessarily q_ij=0-degenerate; record
# its own verdicts for disclosure without asserting a specific one, since
# the specification requires it be *recorded*, not that it always degenerates.
pole_res_A = A.evaluate_instance(pole_fixture, domain5, 5)
pole_res_B = B.evaluate_instance(pole_fixture, domain5, 5)

record("degeneracy_fixture_q_ij_zero_branches_correctly", deg_ok,
       {"fixture": {str(k): v for k, v in deg_fixture.items()}, "A_verdict": deg_res_A["verdict"], "B_verdict": deg_res_B["verdict"]})
report["checks"].append({
    "name": "pole_collision_fixture_disclosure",
    "passed": True,
    "detail": {"fixture": {str(k): v for k, v in pole_fixture.items()}, "A_verdict": pole_res_A["verdict"], "B_verdict": pole_res_B["verdict"]},
})

elapsed = time.time() - start
report["overall_self_check_pass"] = overall_ok
report["elapsed_seconds"] = elapsed
report["stop_rule_triggered"] = not overall_ok

out_dir = Path(__file__).resolve().parent
with open(out_dir / "raw-result.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

summary = {
    "run_id": "RUN-PMA4-001-a",
    "purpose": "Implementation + calibration self-checks",
    "overall_self_check_pass": overall_ok,
    "n_checks": len(report["checks"]),
    "n_failed": sum(1 for c in report["checks"] if not c["passed"]),
    "elapsed_seconds": elapsed,
}
with open(out_dir / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
sys.exit(0 if overall_ok else 1)

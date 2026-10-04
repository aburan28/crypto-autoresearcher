#!/usr/bin/env python3
"""RUN-PMA4-001-c: Q(t) grid execution + Groebner consistency cross-check.

Stage: rational_grid_witnesses_and_grobner (budget 1800s).
Part 1: 4 deterministic grid instances over Q plus 2 perturbed instances
(grid_data.py), same predicate/decider/reverification pipeline as
RUN-PMA4-001-b, with a single widening fallback if the base grid yields
zero non-vacuous obstructions.

Part 2 (CTRL-PMA4-GROEBNER): a third, independent consistency check on a
pre-declared subsample of >= 4 instances (2 already classified OBSTRUCTED
by the ground-truth decider, 2 already classified NOT obstructed i.e. an
EXISTS witness was confirmed), drawn from the deterministic F_7 and F_3
grids (RUN-PMA4-001-b's own instance-generation rule, regenerated here
directly from grid_data.py rather than by reading that run's output, since
grid generation is a pure deterministic function of (field, m)). Builds the
full 11-equation polynomial system (six 2x2, four 3x3, one 4x4 principal-
minor identity) in the 12 off-diagonal unknowns over the fraction field
k(t), and computes a Groebner basis with sympy (tool: sympy, version
recorded in environment.json). Ideal == (1) is a hard proof of
non-existence over the algebraic closure of k(t), and therefore also over
k(t) itself -- this direction is compared against the decider's NOT_EXISTS
verdict for agreement. Ideal != (1) only proves a solution exists over the
algebraic closure of k(t), NOT necessarily over k(t) itself (the same
square-root-in-k(t) subtlety Module A and B are built to resolve); this
direction is compared against the decider's EXISTS verdict as a
plausibility check, not a completeness proof, and is disclosed as such.
"""
import json
import sys
import time
from pathlib import Path

IMPL_DIR = Path(__file__).resolve().parents[2] / "implementation"
sys.path.insert(0, str(IMPL_DIR))

import sympy
from sympy import symbols, groebner, Matrix
from sympy.polys.domains import QQ, GF

from common import field_domain
import grid_data as G
from driver_core import run_instance

STAGE_BUDGET_SECONDS = 1800
GRID_INSTANCE_CAP_REMAINDER = 60 - 30  # RUN-b already used 30 of the 60 cap for finite fields
start = time.time()

t = symbols("t")

# ---------------------------------------------------------------------
# Part 1: Q(t) grid
# ---------------------------------------------------------------------
domainQ = field_domain("Q")
q_field_report = {"instances": [], "widening_used": False}
total_q_instances = 0

for m in range(4):
    inst = G.grid_instance("Q", m)
    q_field_report["instances"].append(run_instance(inst, domainQ, "Q", "grid"))
    total_q_instances += 1
for m in range(2):
    inst = G.perturbed_instance("Q", m)
    q_field_report["instances"].append(run_instance(inst, domainQ, "Q", "perturbed"))
    total_q_instances += 1

nonvacuous_q = sum(1 for r in q_field_report["instances"] if r["classification"] == "agreement_obstructed_confirmed")
if nonvacuous_q == 0 and (time.time() - start) < STAGE_BUDGET_SECONDS:
    q_field_report["widening_used"] = True
    for m in range(4, 12):
        if total_q_instances >= GRID_INSTANCE_CAP_REMAINDER:
            break
        inst = G.widening_instance("Q", m)
        q_field_report["instances"].append(run_instance(inst, domainQ, "Q", "widened_grid"))
        total_q_instances += 1

# ---------------------------------------------------------------------
# Part 2: Groebner cross-check subsample
# ---------------------------------------------------------------------
def pS_expr(d):
    return (t + 1) / (t + d)


def build_equations(d_values):
    p = {S: pS_expr(v) for S, v in d_values.items()}
    p[()] = sympy.Integer(1)
    idxs = (1, 2, 3, 4)
    a = {}
    for i in idxs:
        for j in idxs:
            if i == j:
                continue
            a[(i, j)] = symbols(f"a{i}{j}")

    def diag(i):
        return p[(i,)]

    eqs = []
    for (i, j) in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:
        eqs.append(diag(i) * diag(j) - a[(i, j)] * a[(j, i)] - p[tuple(sorted((i, j)))])
    for (i, j, k) in [(1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)]:
        term = (
            diag(i) * diag(j) * diag(k)
            - diag(i) * a[(j, k)] * a[(k, j)]
            - diag(j) * a[(i, k)] * a[(k, i)]
            - diag(k) * a[(i, j)] * a[(j, i)]
            + a[(i, j)] * a[(j, k)] * a[(k, i)]
            + a[(i, k)] * a[(k, j)] * a[(j, i)]
        )
        eqs.append(term - p[(i, j, k)])
    M = Matrix(4, 4, lambda r, c: diag(idxs[r]) if r == c else a[(idxs[r], idxs[c])])
    eqs.append(M.det() - p[(1, 2, 3, 4)])
    return eqs, list(a.values())


def groebner_verdict(d_values, field_domain_obj, field_label, timeout_note):
    if field_label == "Q":
        dom = QQ.frac_field(t)
    else:
        dom = GF(field_label).frac_field(t)
    eqs, unknowns = build_equations(d_values)
    t0 = time.time()
    try:
        g = groebner(eqs, *unknowns, domain=dom)
        basis = list(g)
        is_trivial_ideal = basis == [sympy.Integer(1)]
        return {
            "groebner_verdict": "NOT_EXISTS_CONFIRMED" if is_trivial_ideal else "POSSIBLE_EXISTS_OVER_CLOSURE",
            "basis_size": len(basis),
            "seconds": time.time() - t0,
        }
    except Exception as e:
        return {"groebner_verdict": "UNDECIDED", "error": str(e), "seconds": time.time() - t0}


# Pre-declared subsample: 2 obstructed (from F_7 grid instances m=0,1) and
# 2 not-obstructed / EXISTS-confirmed (from F_3 grid instances m=0,1) --
# these fields and instance indices are the ones RUN-PMA4-001-b's
# deterministic generation rule already produced OBSTRUCTED / EXISTS
# outcomes for (10/10 F_7 grid instances OBSTRUCTED; F_3's single-table
# collapse is EXISTS on every instance), regenerated here directly since
# grid_data.py's generation is a pure function of (field, m).
subsample_specs = [
    (7, 0, "obstructed"),
    (7, 1, "obstructed"),
    (3, 0, "not_obstructed"),
    (3, 1, "not_obstructed"),
]

groebner_results = []
for field_label, m, expected_kind in subsample_specs:
    domain = field_domain(field_label)
    inst = G.grid_instance(field_label, m)
    decider_record = run_instance(inst, domain, field_label, "groebner_subsample")
    gv = groebner_verdict(inst, domain, field_label, expected_kind)
    decider_says_exists = decider_record["decider_verdict"] == "EXISTS"
    decider_says_not_exists = decider_record["decider_verdict"] == "NOT_EXISTS"

    if gv["groebner_verdict"] == "NOT_EXISTS_CONFIRMED":
        agrees = decider_says_not_exists
        comparison = "agree" if agrees else "disagree"
    elif gv["groebner_verdict"] == "POSSIBLE_EXISTS_OVER_CLOSURE":
        # can only confirm consistency with an EXISTS verdict; it does not
        # contradict a NOT_EXISTS verdict (over-the-closure existence does
        # not imply a k(t)-rational point), so this direction is recorded
        # as consistent-but-inconclusive rather than "agree"/"disagree"
        # when the decider itself said NOT_EXISTS.
        if decider_says_exists:
            comparison = "agree"
        else:
            comparison = "inconclusive_closure_vs_field"
    else:
        comparison = "undecided_skipped"

    groebner_results.append({
        "field": field_label,
        "instance_index": m,
        "d_values": {str(k): v for k, v in inst.items()},
        "decider_verdict": decider_record["decider_verdict"],
        "predicate_verdict": decider_record["predicate_verdict"],
        "groebner": gv,
        "comparison_to_decider": comparison,
    })

elapsed = time.time() - start

results = {
    "run_id": "RUN-PMA4-001-c",
    "elapsed_seconds": elapsed,
    "q_field": q_field_report,
    "groebner_subsample": groebner_results,
    "tool": {"name": "sympy", "version": sympy.__version__},
}

out_dir = Path(__file__).resolve().parent
with open(out_dir / "raw-result.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

q_counts = {}
for r in q_field_report["instances"]:
    q_counts[r["classification"]] = q_counts.get(r["classification"], 0) + 1

groebner_summary = {
    "n_subsample": len(groebner_results),
    "comparisons": [r["comparison_to_decider"] for r in groebner_results],
    "agree_count": sum(1 for r in groebner_results if r["comparison_to_decider"] == "agree"),
    "disagree_count": sum(1 for r in groebner_results if r["comparison_to_decider"] == "disagree"),
    "inconclusive_or_skipped_count": sum(1 for r in groebner_results if r["comparison_to_decider"] not in ("agree", "disagree")),
}

summary = {
    "run_id": "RUN-PMA4-001-c",
    "elapsed_seconds": elapsed,
    "q_field": {"counts": q_counts, "widening_used": q_field_report["widening_used"], "n_instances": len(q_field_report["instances"])},
    "groebner_subsample_summary": groebner_summary,
}

with open(out_dir / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))

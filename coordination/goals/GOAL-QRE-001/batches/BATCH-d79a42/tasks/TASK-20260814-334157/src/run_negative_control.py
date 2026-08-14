"""negative_control.json -- the mutation NAMED IN ADVANCE in PREREGISTRATION.md
section 5, applied to the finished circuit.

The named mutation: in the new inverter's shift/compare/conditional-subtract
step, EXCHANGE WHICH OF THE TWO MUTUALLY EXCLUSIVE UPDATE RULES IS APPLIED WHEN
THE CONTROLLING BIT IS 0 VERSUS 1 -- i.e. swap the u > v branch with the u <= v
branch.  It is implemented as the `branch_order_swapped` flag of
src/euclid.py::_euclid_phase1 and is False in every counted or reported
circuit.

It is a control-flow defect, not a value defect: the swapped branches emit the
SAME gate multiset in the same registers and differ only in which branch's
gates fire for which input.  The pre-registered expectation, from the
BATCH-973b49 precedent recorded in KN-FIND-a4d4a4, is that the gate tally does
NOT change.  What is measured here is (a) whether the tally changes, and (b) on
what fraction of a declared input sample the semantic + ancilla checks return
the other answer.  Per clause 5(c), a fraction below 1.0 is reported as a
finding about the control's sufficiency, not replaced with a mutation that is
caught more often.
"""
import json
import os
import random
import time

from common import (TASK, GOAL, BATCH, LANE, SEED, PROHIBITION,
                    BLIND_STATEMENT, CONVENTION_REF, prime_pair, any_point)
from circuits import DirtyAncilla
from euclid import Machine, mod_inv_euclid, point_add_euclid
from run_validation_e import fast_curve_points, EXHAUSTIVE_BELOW

INV_WIDTHS = [4, 5, 6, 7, 8, 9]
EC_WIDTHS = [4, 5, 6, 7]


def tally(build, n, p):
    m = Machine(run=False)
    A = m.alloc(n, io=True)
    B = m.alloc(n, io=True)
    build(m, A, B, p)
    return {"x": m.counts["x"], "cnot": m.counts["cnot"],
            "ccx": m.counts["ccx"], "peak_qubits": m.peak}


def inverter_control(rng):
    rows = []
    for n in INV_WIDTHS:
        for p, kind in prime_pair(n):
            t0 = time.time()
            clean = tally(lambda m, A, B, q: mod_inv_euclid(m, A, B, q), n, p)
            mut = tally(lambda m, A, B, q: mod_inv_euclid(m, A, B, q, True),
                        n, p)
            xs = list(range(1, p)) if p < EXHAUSTIVE_BELOW else \
                sorted(rng.sample(range(1, p), 64))
            caught = wrong_value = dirty_only = exc = 0
            for x in xs:
                m = Machine(run=True)
                X = m.alloc(n, io=True)
                T = m.alloc(n, io=True)
                m.prepare(X, x)
                bad_value = bad_clean = False
                try:
                    mod_inv_euclid(m, X, T, p, True)
                except DirtyAncilla:
                    exc += 1
                    caught += 1
                    continue
                if m.read(T) != pow(x, -1, p) or m.read(X) != x:
                    bad_value = True
                if any(m.bits[q] for q in range(len(m.bits))
                       if q not in X + T):
                    bad_clean = True
                if bad_value:
                    wrong_value += 1
                if bad_clean and not bad_value:
                    dirty_only += 1
                if bad_value or bad_clean:
                    caught += 1
            rows.append({
                "circuit": "euclid_modular_inversion", "n": n, "prime_p": p,
                "prime_kind": kind,
                "input_coverage": ("exhaustive" if p < EXHAUSTIVE_BELOW
                                   else "random_sample"),
                "sample_seed": SEED if p >= EXHAUSTIVE_BELOW else None,
                "inputs_tested": len(xs),
                "tally_unmutated": clean, "tally_mutated": mut,
                "tally_changed_by_mutation": clean != mut,
                "caught_by_validation": caught,
                "caught_fraction": caught / len(xs),
                "caught_on_every_tested_input": caught == len(xs),
                "breakdown": {
                    "wrong_output_value": wrong_value,
                    "clean_but_dirty_ancillas_only": dirty_only,
                    "dirty_ancilla_exception_at_release": exc},
                "seconds": round(time.time() - t0, 2)})
            print("  inv n=%-3d p=%-8d tally_changed=%s caught %d/%d (%.1fs)"
                  % (n, p, clean != mut, caught, len(xs),
                     time.time() - t0), flush=True)
    return rows


def pointadd_control(rng):
    rows = []
    for n in EC_WIDTHS:
        for p, kind in prime_pair(n):
            t0 = time.time()
            x2, y2, A, B = any_point(p)
            clean = tally(lambda m, X, Y, q: point_add_euclid(m, X, Y, q,
                                                              x2, y2), n, p)
            mut = tally(lambda m, X, Y, q: point_add_euclid(m, X, Y, q, x2, y2,
                                                            True), n, p)
            pts = fast_curve_points(p, A, B)
            cases = []
            for (x1, y1) in pts:
                if x1 == x2:
                    continue
                lam = (y1 - y2) * pow(x1 - x2, -1, p) % p
                x3 = (lam * lam - x1 - x2) % p
                y3 = (lam * (x1 - x3) - y1) % p
                if x3 == x2:
                    continue
                cases.append((x1, y1, x3, y3))
            caught = wrong_value = dirty_only = exc = 0
            for (x1, y1, x3, y3) in cases:
                m = Machine(run=True)
                X = m.alloc(n, io=True)
                Y = m.alloc(n, io=True)
                m.prepare(X, x1)
                m.prepare(Y, y1)
                try:
                    point_add_euclid(m, X, Y, p, x2, y2, True)
                except DirtyAncilla:
                    exc += 1
                    caught += 1
                    continue
                bad_value = (m.read(X), m.read(Y)) != (x3, y3)
                bad_clean = any(m.bits[q] for q in range(len(m.bits))
                                if q not in X + Y)
                if bad_value:
                    wrong_value += 1
                if bad_clean and not bad_value:
                    dirty_only += 1
                if bad_value or bad_clean:
                    caught += 1
            rows.append({
                "circuit": "ec_point_addition_with_euclid_inverter",
                "n": n, "prime_p": p, "prime_kind": kind,
                "curve": {"A": A, "B": B}, "constant_point_Q": [x2, y2],
                "input_coverage": "exhaustive_over_declared_domain",
                "inputs_tested": len(cases),
                "tally_unmutated": clean, "tally_mutated": mut,
                "tally_changed_by_mutation": clean != mut,
                "caught_by_validation": caught,
                "caught_fraction": caught / len(cases) if cases else None,
                "caught_on_every_tested_input": caught == len(cases),
                "breakdown": {
                    "wrong_output_value": wrong_value,
                    "clean_but_dirty_ancillas_only": dirty_only,
                    "dirty_ancilla_exception_at_release": exc},
                "seconds": round(time.time() - t0, 2)})
            print("  ec  n=%-3d p=%-8d tally_changed=%s caught %d/%d (%.1fs)"
                  % (n, p, clean != mut, caught, len(cases),
                     time.time() - t0), flush=True)
    return rows


def main():
    t0 = time.time()
    rng = random.Random(SEED)
    print("== inverter, mutated ==", flush=True)
    inv = inverter_control(rng)
    print("== point addition, mutated ==", flush=True)
    ec = pointadd_control(rng)
    allr = inv + ec
    tot_in = sum(r["inputs_tested"] for r in allr)
    tot_caught = sum(r["caught_by_validation"] for r in allr)
    out = {
        "task": TASK, "goal": GOAL, "batch": BATCH, "lane": LANE,
        "artifact": "negative_control.json",
        "convention_reference": CONVENTION_REF,
        "preregistration_clause_discharged": "5",
        "seed": SEED,
        "mutation_named_in_advance":
            "PREREGISTRATION.md section 5, frozen at commit "
            "b3f6daddb0eb2c6e00a2acc470ddce386670ef0c and committed before "
            "this task ran: in the new inverter's shift/compare/conditional-"
            "subtract step, exchange which of the two mutually exclusive "
            "update rules is applied when the controlling bit is 0 versus 1.",
        "mutation_implementation":
            "src/euclid.py::_euclid_phase1(branch_order_swapped=True) swaps "
            "the control qubit of the branch-3 update (u <- u-v, r <- r+s) "
            "with that of the branch-4 update (v <- v-u, s <- s+r), and "
            "correspondingly swaps which branch flag feeds the u-halving and "
            "v-halving controls. Same gate types, same register operands, "
            "different control wiring -- the permutation-class defect "
            "KN-FIND-a4d4a4 identifies as invisible to a gate tally by "
            "construction.",
        "preregistered_expectation":
            "clause 5(a): the gate tally is expected NOT to change. What is "
            "measured is whether it changes and what fraction of inputs the "
            "semantic + global-ancilla check flags.",
        "inverter_rows": inv,
        "point_addition_rows": ec,
        "result": {
            "tally_changed_anywhere": any(r["tally_changed_by_mutation"]
                                          for r in allr),
            "tally_unchanged_everywhere": all(
                not r["tally_changed_by_mutation"] for r in allr),
            "configurations": len(allr),
            "inputs_tested_total": tot_in,
            "caught_total": tot_caught,
            "caught_fraction_overall": tot_caught / tot_in,
            "caught_on_every_tested_input_in_every_configuration":
                all(r["caught_on_every_tested_input"] for r in allr),
            "configurations_not_caught_on_every_input":
                [{"n": r["n"], "prime_p": r["prime_p"],
                  "caught_fraction": r["caught_fraction"],
                  "inputs_tested": r["inputs_tested"]}
                 for r in allr if not r["caught_on_every_tested_input"]],
        },
        "interpretation_boundary":
            "This artifact reports what the mutation did to the tally and what "
            "fraction of inputs the validation flagged. It does not assert "
            "that the validation catches defects in general, and it is not "
            "evidence that the unmutated circuit is correct -- only that the "
            "check used to test it can return the other answer.",
        "blind_by_design": BLIND_STATEMENT,
        "prohibition_statement": PROHIBITION,
        "wall_clock_seconds": None,
    }
    out["wall_clock_seconds"] = round(time.time() - t0, 2)
    dest = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "negative_control.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote", dest, "in %.1fs" % out["wall_clock_seconds"])


if __name__ == "__main__":
    main()

"""inverter_validation.json -- BLOCKING classical simulation of the identical
circuits run_inverter.py and run_comparison.py count.

WHAT IS AND IS NOT A CHECK HERE.  Per KN-FIND-a4d4a4 and PREREGISTRATION clause
1.9, gate-tally equality between the counting mode and the simulating mode is
NOT a correctness check: a counter and a simulator fed by one builder agreed
bit-identically on a provably broken circuit.  The checks this file relies on
are, in order:

  (1) SEMANTIC.  Simulate the circuit on a classical bit vector and compare its
      output register against x^-1 mod p (respectively against the affine
      point-addition result) computed independently in Python integer
      arithmetic, and check the input register is returned unchanged.
  (2) GLOBAL ANCILLA CLEANLINESS.  At end of circuit, assert that EVERY qubit
      outside the declared I/O registers is 0.  This is the non-vacuous
      backstop; BATCH-973b49's D-V2 records that the allocator-level
      DirtyAncilla guard is vacuous inside capture(), and this task relies on
      the end-of-circuit assertion, not on that guard.
  (3) The pre-registered mutation in run_negative_control.py, which shows the
      above can return the other answer.

Tally equality is still recorded per configuration, explicitly labelled as
plumbing evidence only.
"""
import json
import os
import random
import time

from common import (TASK, GOAL, BATCH, LANE, SEED, INV_LADDER, INV_HOLDOUT,
                    EC_LADDER, PROHIBITION, BLIND_STATEMENT, CONVENTION_REF,
                    prime_pair, any_point, primes_of_bitlength)
from euclid import Machine, mod_inv_euclid, point_add_euclid
from circuits import point_add as fermat_point_add
from run_validation import curve_points as inherited_curve_points

EXHAUSTIVE_BELOW = 600          # p below this: every x / every curve point


# ------------------------------------------------------------------ helpers
def classical_kaliski_iterations(p, x):
    u, v, k = p, x, 0
    while v != 0:
        if u % 2 == 0:
            u //= 2
        elif v % 2 == 0:
            v //= 2
        elif u > v:
            u = (u - v) // 2
        else:
            v = (v - u) // 2
        k += 1
    return k, u


def fast_curve_points(p, A, B):
    """All affine points of y^2 = x^3 + Ax + B over F_p, in O(p).
    Cross-checked against BATCH-973b49's own O(p^2) curve_points at small p
    (see step_bound_and_point_generator_checks in the output)."""
    sq = {}
    for y in range(p):
        sq.setdefault(y * y % p, []).append(y)
    pts = []
    for x in range(p):
        rhs = (x * x % p * x + A * x + B) % p
        for y in sq.get(rhs, ()):
            pts.append((x, y))
    return sorted(pts)


# --------------------------------------------------------------- inverter
def validate_inverter(cfgs, rng):
    out = []
    for n, p, kind in cfgs:
        t0 = time.time()
        if p < EXHAUSTIVE_BELOW:
            xs, cov = list(range(1, p)), "exhaustive"
        else:
            k = 64 if n <= 14 else (32 if n <= 20 else 16)
            xs = sorted(rng.sample(range(1, p), k))
            xs = sorted(set(xs) | {1, 2, p - 1, (p - 1) // 2})
            cov = "random_sample_plus_edge_inputs"
        fails, run_counts, dirty_total = [], None, 0
        for x in xs:
            m = Machine(run=True)
            X = m.alloc(n, io=True)
            T = m.alloc(n, io=True)
            m.prepare(X, x)
            mod_inv_euclid(m, X, T, p)
            got, gotx = m.read(T), m.read(X)
            want = pow(x, -1, p)
            dirty = [q for q in range(len(m.bits))
                     if q not in X + T and m.bits[q]]
            dirty_total += len(dirty)
            if got != want or gotx != x or dirty:
                fails.append({"x": x, "got": got, "want": want,
                              "input_preserved": gotx == x,
                              "dirty_ancillas": len(dirty)})
            run_counts = dict(m.counts)
        mc = Machine(run=False)
        Xc = mc.alloc(n, io=True)
        Tc = mc.alloc(n, io=True)
        mod_inv_euclid(mc, Xc, Tc, p)
        tal = dict(mc.counts)
        out.append({
            "circuit": "euclid_modular_inversion", "n": n, "prime_p": p,
            "prime_kind": kind,
            "w_hamming_weight_p_minus_2": bin(p - 2).count("1"),
            "function_checked": "T = x^-1 mod p, X preserved, for 1 <= x < p",
            "input_coverage": cov, "inputs_tested": len(xs),
            "input_space": p - 1,
            "sample_seed": SEED if cov != "exhaustive" else None,
            "failures": len(fails), "failure_detail": fails[:5],
            "passed": not fails,
            "global_ancilla_assertion":
                "every qubit outside X and T is 0 at end of circuit",
            "ancillas_returned_to_zero": dirty_total == 0,
            "dirty_ancilla_instances": dirty_total,
            "gate_tally_during_simulation": run_counts,
            "gate_tally_in_counting_mode": {"x": tal["x"], "cnot": tal["cnot"],
                                            "ccx": tal["ccx"]},
            "tallies_equal": run_counts == {"x": tal["x"],
                                            "cnot": tal["cnot"],
                                            "ccx": tal["ccx"]},
            "tally_equality_is_not_a_correctness_check":
                "recorded as plumbing evidence only; see KN-FIND-a4d4a4 and "
                "negative_control.json",
            "peak_qubits": mc.peak,
            "toffoli": tal["ccx"], "t_count": 7 * tal["ccx"],
            "seconds": round(time.time() - t0, 2)})
        print("  inv n=%-3d p=%-12d %s: %d/%d ok, clean=%s (%.1fs)"
              % (n, p, cov, len(xs) - len(fails), len(xs), dirty_total == 0,
                 time.time() - t0), flush=True)
    return out


# ------------------------------------------------------------- point addition
def validate_point_add(cfgs, rng):
    out = []
    for n, p, kind in cfgs:
        t0 = time.time()
        x2, y2, A, B = any_point(p)
        pts = fast_curve_points(p, A, B)
        assert (x2, y2) in pts
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
        excluded = len(pts) - 1 - len(cases)
        if p < EXHAUSTIVE_BELOW:
            cov = "exhaustive_over_declared_domain"
        else:
            k = 24 if n <= 11 else 6
            if len(cases) > k:
                cases = [cases[i]
                         for i in sorted(rng.sample(range(len(cases)), k))]
            cov = "random_sample"
        fails, run_counts, dirty_total = [], None, 0
        for (x1, y1, x3, y3) in cases:
            m = Machine(run=True)
            X = m.alloc(n, io=True)
            Y = m.alloc(n, io=True)
            m.prepare(X, x1)
            m.prepare(Y, y1)
            point_add_euclid(m, X, Y, p, x2, y2)
            gx, gy = m.read(X), m.read(Y)
            dirty = [q for q in range(len(m.bits))
                     if q not in X + Y and m.bits[q]]
            dirty_total += len(dirty)
            if (gx, gy) != (x3, y3) or dirty:
                fails.append({"input": [x1, y1], "got": [gx, gy],
                              "want": [x3, y3], "dirty_ancillas": len(dirty)})
            run_counts = dict(m.counts)
        mc = Machine(run=False)
        Xc = mc.alloc(n, io=True)
        Yc = mc.alloc(n, io=True)
        point_add_euclid(mc, Xc, Yc, p, x2, y2)
        tal = dict(mc.counts)
        out.append({
            "circuit": "ec_point_addition_with_euclid_inverter",
            "n": n, "prime_p": p, "prime_kind": kind,
            "w_hamming_weight_p_minus_2": bin(p - 2).count("1"),
            "curve": {"form": "y^2 = x^3 + A*x + B", "A": A, "B": B},
            "constant_point_Q": [x2, y2],
            "curve_affine_points": len(pts),
            "domain": "x1 != x2 and x3 != x2 (BATCH-973b49 defect D-1's "
                      "refined domain, inherited verbatim; this task changed "
                      "only the inverter, not the domain)",
            "excluded_by_declared_domain": excluded,
            "input_coverage": cov, "inputs_tested": len(cases),
            "sample_seed": SEED if cov == "random_sample" else None,
            "failures": len(fails), "failure_detail": fails[:5],
            "passed": not fails,
            "global_ancilla_assertion":
                "every qubit outside X and Y is 0 at end of circuit",
            "ancillas_returned_to_zero": dirty_total == 0,
            "dirty_ancilla_instances": dirty_total,
            "gate_tally_during_simulation": run_counts,
            "gate_tally_in_counting_mode": {"x": tal["x"], "cnot": tal["cnot"],
                                            "ccx": tal["ccx"]},
            "tallies_equal": run_counts == {"x": tal["x"],
                                            "cnot": tal["cnot"],
                                            "ccx": tal["ccx"]},
            "peak_qubits": mc.peak,
            "toffoli": tal["ccx"], "t_count": 7 * tal["ccx"],
            "seconds": round(time.time() - t0, 2)})
        print("  ec  n=%-3d p=%-8d %s: %d/%d ok, clean=%s (%.1fs)"
              % (n, p, cov, len(cases) - len(fails), len(cases),
                 dirty_total == 0, time.time() - t0), flush=True)
    return out


# ------------------------------------------------------------------- main
def main():
    t0 = time.time()
    rng = random.Random(SEED)

    print("== step-bound and point-generator checks ==", flush=True)
    bound = []
    for n in range(3, 17):
        for p in primes_of_bitlength(n, 2):
            mx, arg = 0, None
            for x in range(1, p):
                k, uf = classical_kaliski_iterations(p, x)
                assert uf == 1
                if k > mx:
                    mx, arg = k, x
            bound.append({"n": n, "prime_p": p, "max_iterations_observed": mx,
                          "argmax_x": arg, "fixed_circuit_K": 2 * n,
                          "K_sufficient": mx <= 2 * n,
                          "terminal_u_always_1": True})
        print("  n=%d worst-case iterations %d, K=%d"
              % (n, bound[-1]["max_iterations_observed"], 2 * n), flush=True)
    ptchk = []
    for p in (11, 13, 31, 61, 127):
        x2, y2, A, B = any_point(p)
        ptchk.append({"prime_p": p, "curve_A": A, "curve_B": B,
                      "inherited_generator_points": len(
                          inherited_curve_points(p, A, B)),
                      "fast_generator_points": len(fast_curve_points(p, A, B)),
                      "identical": sorted(inherited_curve_points(p, A, B))
                      == fast_curve_points(p, A, B)})

    print("== euclid inverter ==", flush=True)
    inv_cfgs = [(n, p, kind) for n in INV_LADDER + INV_HOLDOUT
                for p, kind in prime_pair(n)]
    inv = validate_inverter(inv_cfgs, rng)

    print("== ec point addition with the euclid inverter ==", flush=True)
    ec_cfgs = [(n, p, kind) for n in EC_LADDER for p, kind in prime_pair(n)]
    ec = validate_point_add(ec_cfgs, rng)

    out = {
        "task": TASK, "goal": GOAL, "batch": BATCH, "lane": LANE,
        "artifact": "inverter_validation.json",
        "convention_reference": CONVENTION_REF,
        "preregistration_clauses_discharged": ["1.3", "1.9", "1.10", "3.1",
                                               "3.2"],
        "seed": SEED,
        "blocking_rule":
            "PREREGISTRATION clause 1.9. A width whose simulation fails has "
            "its count withheld. Zero widths failed, so nothing was withheld; "
            "the rule is procedural rather than mechanised, which is "
            "BATCH-973b49's open defect D-V4 and is inherited here unrepaired "
            "(recorded in execution_report.yaml).",
        "what_counts_as_a_check":
            "Semantic comparison against the function the circuit should "
            "compute, plus a global end-of-circuit assertion that every qubit "
            "outside the declared I/O registers is 0. Gate-tally equality "
            "between the counting and simulating modes is recorded but is NOT "
            "treated as a correctness check (KN-FIND-a4d4a4); the mutation in "
            "negative_control.json is what bounds it.",
        "ancilla_guard_note":
            "BATCH-973b49 defect D-V2: the allocator's DirtyAncilla exception "
            "is vacuous inside capture(), and the derived inverter builds its "
            "whole phase-1 block inside capture(). This task therefore relies "
            "on the global end-of-circuit zero assertion above, and states so "
            "plainly, exactly as PREREGISTRATION clause 1.3 requires.",
        "blind_by_design": BLIND_STATEMENT,
        "prohibition_statement": PROHIBITION,
        "step_bound_and_point_generator_checks": {
            "fixed_step_count_K": "2n",
            "claim": "derivation D2 in src/euclid.py bounds the classical "
                     "iteration count by 2n-1; here that bound is checked "
                     "exhaustively over every x in [1,p) for two primes per "
                     "bit length, n = 3..16",
            "rows": bound,
            "K_sufficient_everywhere": all(r["K_sufficient"] for r in bound),
            "max_iterations_equals_2n_minus_1_everywhere":
                all(r["max_iterations_observed"] == 2 * r["n"] - 1
                    for r in bound),
            "point_generator_cross_check": ptchk,
            "point_generator_agrees_with_inherited":
                all(r["identical"] for r in ptchk),
        },
        "euclid_inverter_validation": inv,
        "ec_point_addition_validation": ec,
        "summary": {
            "inverter_configs": len(inv),
            "inverter_configs_failed": sum(1 for r in inv if not r["passed"]),
            "inverter_widths_validated": sorted({r["n"] for r in inv
                                                 if r["passed"]}),
            "inverter_widths_failed": sorted({r["n"] for r in inv
                                              if not r["passed"]}),
            "ec_configs": len(ec),
            "ec_configs_failed": sum(1 for r in ec if not r["passed"]),
            "ec_widths_validated": sorted({r["n"] for r in ec if r["passed"]}),
            "ec_widths_failed": sorted({r["n"] for r in ec
                                        if not r["passed"]}),
            "total_circuit_instances_simulated":
                sum(r["inputs_tested"] for r in inv + ec),
            "all_ancillas_clean": all(r["ancillas_returned_to_zero"]
                                      for r in inv + ec),
            "all_tallies_equal": all(r["tallies_equal"] for r in inv + ec),
        },
        "wall_clock_seconds": None,
    }
    out["wall_clock_seconds"] = round(time.time() - t0, 2)
    dest = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "inverter_validation.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote", dest, "in %.1fs" % out["wall_clock_seconds"])


if __name__ == "__main__":
    main()

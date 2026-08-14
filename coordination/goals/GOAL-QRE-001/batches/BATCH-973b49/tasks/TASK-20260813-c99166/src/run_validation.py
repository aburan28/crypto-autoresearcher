"""Produce validation.json: classical simulation of the IDENTICAL circuits that
run_counts.py counts (PREREGISTRATION clauses 8 and 9).

The correspondence is mechanical, not asserted: for every validated
configuration this script
  (1) builds the circuit with Machine(run=True) and checks the output,
  (2) builds the same circuit with Machine(run=False) (the counting mode used
      by run_counts.py), and
  (3) records BOTH gate tallies and whether they are identical.
A run-mode machine tallies gates as it executes them, so an equal tally is
direct evidence that the simulated gate stream is the counted gate stream.

Ancilla cleanliness is enforced by the allocator (it refuses to release a
qubit in state 1), and is additionally re-checked at top level: every qubit
outside the declared I/O registers must be 0 when the circuit ends.

Validation is BLOCKING: a configuration that fails here has its count
withheld in the report.
"""
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from circuits import (Machine, add, sub, add_const, mod_add, mod_sub,       # noqa
                      mod_add_const, mod_sub_const, mod_neg, mod_dbl,
                      mod_hlv, modmul_acc, mod_inv, modexp, point_add)
from run_counts import (is_prime, primes_of_bitlength, rsa_modulus,          # noqa
                        any_point, count_modexp, count_point_add)

SEED = 20260813


def tally_only(build):
    m = Machine(run=False)
    build(m)
    return dict(m.counts), m.peak


# ------------------------------------------------------------------ level 1
def validate_components():
    """Exhaustive checks of every sub-circuit the two headline circuits are
    made of, at small widths."""
    res = []

    def rec(name, width, modulus, cases, failures, extra=None):
        r = {"subcircuit": name, "bit_width_n": width, "modulus": modulus,
             "input_coverage": "exhaustive", "cases": cases,
             "failures": failures, "passed": failures == 0}
        if extra:
            r.update(extra)
        res.append(r)

    # ripple adder / subtractor mod 2^n
    for n in (3, 4, 5):
        c = f = 0
        for av in range(1 << n):
            for bv in range(1 << n):
                m = Machine(run=True)
                A = m.alloc(n, io=True)
                B = m.alloc(n, io=True)
                m.prepare(A, av)
                m.prepare(B, bv)
                add(m, A, B)
                c += 1
                if m.read(B) != (av + bv) % (1 << n) or m.read(A) != av:
                    f += 1
                m2 = Machine(run=True)
                A = m2.alloc(n, io=True)
                B = m2.alloc(n, io=True)
                m2.prepare(A, av)
                m2.prepare(B, bv)
                sub(m2, A, B)
                c += 1
                if m2.read(B) != (bv - av) % (1 << n):
                    f += 1
        rec("ripple_adder_and_subtractor_mod_2^n", n, 1 << n, c, f)

    # constant adder mod 2^n
    for n in (4,):
        c = f = 0
        for k in range(1 << n):
            for bv in range(1 << n):
                m = Machine(run=True)
                B = m.alloc(n, io=True)
                m.prepare(B, bv)
                add_const(m, k, B)
                c += 1
                if m.read(B) != (bv + k) % (1 << n):
                    f += 1
        rec("constant_adder_mod_2^n", n, 1 << n, c, f)

    # modular addition / subtraction / constant variants
    for M in (5, 7, 11, 13, 29, 31):
        n = M.bit_length()
        c = f = 0
        for av in range(M):
            for bv in range(M):
                m = Machine(run=True)
                A = m.alloc(n, io=True)
                B = m.alloc(n, io=True)
                m.prepare(A, av)
                m.prepare(B, bv)
                mod_add(m, A, B, M)
                c += 1
                if m.read(B) != (av + bv) % M or m.read(A) != av:
                    f += 1
                m2 = Machine(run=True)
                A = m2.alloc(n, io=True)
                B = m2.alloc(n, io=True)
                m2.prepare(A, av)
                m2.prepare(B, bv)
                mod_sub(m2, A, B, M)
                c += 1
                if m2.read(B) != (bv - av) % M:
                    f += 1
                m3 = Machine(run=True)
                B = m3.alloc(n, io=True)
                m3.prepare(B, bv)
                mod_add_const(m3, av, B, M)
                c += 1
                if m3.read(B) != (av + bv) % M:
                    f += 1
                m4 = Machine(run=True)
                B = m4.alloc(n, io=True)
                m4.prepare(B, bv)
                mod_sub_const(m4, av, B, M)
                c += 1
                if m4.read(B) != (bv - av) % M:
                    f += 1
        rec("modular_add_sub_and_constant_variants", n, M, c, f)

    # modular doubling / halving / negation
    for M in (11, 13, 29, 31, 61, 127):
        n = M.bit_length()
        c = f = 0
        for bv in range(M):
            m = Machine(run=True)
            B = m.alloc(n, io=True)
            m.prepare(B, bv)
            mod_dbl(m, B, M)
            c += 1
            if m.read(B) != (2 * bv) % M:
                f += 1
            m2 = Machine(run=True)
            B = m2.alloc(n, io=True)
            m2.prepare(B, bv)
            mod_hlv(m2, B, M)
            c += 1
            if (2 * m2.read(B)) % M != bv:
                f += 1
            if bv:
                m3 = Machine(run=True)
                B = m3.alloc(n, io=True)
                m3.prepare(B, bv)
                mod_neg(m3, B, M)
                c += 1
                if m3.read(B) != (M - bv) % M:
                    f += 1
        rec("modular_double_halve_negate", n, M, c, f)

    # quantum x quantum modular multiplication and squaring
    for M in (11, 13, 29, 31):
        n = M.bit_length()
        c = f = 0
        for xv in range(M):
            for yv in range(M):
                m = Machine(run=True)
                X = m.alloc(n, io=True)
                Y = m.alloc(n, io=True)
                Z = m.alloc(n, io=True)
                m.prepare(X, xv)
                m.prepare(Y, yv)
                modmul_acc(m, X, Y, Z, M, 1)
                c += 1
                if m.read(Z) != xv * yv % M or m.read(X) != xv or \
                        m.read(Y) != yv:
                    f += 1
            m2 = Machine(run=True)
            X = m2.alloc(n, io=True)
            Z = m2.alloc(n, io=True)
            m2.prepare(X, xv)
            modmul_acc(m2, X, X, Z, M, 1)
            c += 1
            if m2.read(Z) != xv * xv % M:
                f += 1
        rec("modular_multiplication_and_squaring", n, M, c, f)

    # Fermat modular inversion
    for M in (11, 13, 29, 31, 61, 127):
        n = M.bit_length()
        c = f = 0
        for xv in range(1, M):
            m = Machine(run=True)
            X = m.alloc(n, io=True)
            T = m.alloc(n, io=True)
            m.prepare(X, xv)
            mod_inv(m, X, T, M)
            c += 1
            if m.read(T) != pow(xv, -1, M) or m.read(X) != xv:
                f += 1
        rec("fermat_modular_inversion", n, M, c, f)
    return res


# ------------------------------------------------------------------ level 2
def validate_modexp(cfgs, rng):
    out = []
    for n, N, a, mode, k in cfgs:
        t0 = time.time()
        exps = (list(range(1 << (2 * n))) if mode == "exhaustive"
                else sorted(rng.sample(range(1 << (2 * n)), k)))
        fails, run_counts = [], None
        for e in exps:
            m = Machine(run=True)
            E = m.alloc(2 * n, io=True)
            Z = m.alloc(n, io=True)
            m.prepare(E, e)
            m.prepare(Z, 1)
            modexp(m, E, Z, a, N)
            got, gote = m.read(Z), m.read(E)
            want = pow(a, e, N)
            dirty = [q for q in range(len(m.bits))
                     if q not in E + Z and m.bits[q]]
            if got != want or gote != e or dirty:
                fails.append({"exponent": e, "got": got, "want": want,
                              "exponent_preserved": gote == e,
                              "dirty_ancillas": len(dirty)})
            run_counts = dict(m.counts)
        tal = count_modexp(n, N, a)
        tal_counts = {"x": tal["x"], "cnot": tal["cnot"], "ccx": tal["toffoli"]}
        out.append({
            "circuit": "modular_exponentiation", "n": n, "modulus_N": N,
            "base_a": a, "modulus_factors": list(_factor2(N)),
            "exponent_register_bits": 2 * n,
            "input_coverage": mode,
            "inputs_tested": len(exps),
            "input_space": 1 << (2 * n),
            "sample_seed": SEED if mode != "exhaustive" else None,
            "failures": len(fails), "failure_detail": fails[:5],
            "passed": not fails,
            "ancillas_returned_to_zero": not any(
                f.get("dirty_ancillas") for f in fails),
            "gate_tally_during_simulation": run_counts,
            "gate_tally_in_counting_mode": tal_counts,
            "simulated_circuit_is_counted_circuit":
                run_counts == tal_counts,
            "toffoli": tal["toffoli"], "t_count": 7 * tal["toffoli"],
            "seconds": round(time.time() - t0, 2)})
        print("  modexp n=%d N=%d %s: %d/%d ok, tally match %s (%.1fs)"
              % (n, N, mode, len(exps) - len(fails), len(exps),
                 run_counts == tal_counts, time.time() - t0), flush=True)
    return out


def _factor2(N):
    for d in range(3, int(math.isqrt(N)) + 1, 2):
        if N % d == 0:
            return d, N // d
    return (N,)


# ------------------------------------------------------------------ level 3
def curve_points(p, A, B):
    return [(x, y) for x in range(p) for y in range(p)
            if (y * y - x ** 3 - A * x - B) % p == 0]


def validate_point_add(cfgs, rng):
    out = []
    for n, p, mode, k in cfgs:
        t0 = time.time()
        x2, y2, A, B = any_point(p)
        pts = curve_points(p, A, B)
        assert (x2, y2) in pts
        # declared domain: x1 != x2 and x3 != x2
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
        if mode != "exhaustive" and len(cases) > k:
            cases = [cases[i] for i in sorted(rng.sample(range(len(cases)), k))]
            cov = "random_sample"
        else:
            cov = "exhaustive_over_declared_domain"
        fails, run_counts = [], None
        for (x1, y1, x3, y3) in cases:
            m = Machine(run=True)
            X = m.alloc(n, io=True)
            Y = m.alloc(n, io=True)
            m.prepare(X, x1)
            m.prepare(Y, y1)
            point_add(m, X, Y, p, x2, y2)
            gx, gy = m.read(X), m.read(Y)
            dirty = [q for q in range(len(m.bits))
                     if q not in X + Y and m.bits[q]]
            if (gx, gy) != (x3, y3) or dirty:
                fails.append({"input": [x1, y1], "got": [gx, gy],
                              "want": [x3, y3], "dirty_ancillas": len(dirty)})
            run_counts = dict(m.counts)
        tal = count_point_add(n, p, x2, y2)
        tal_counts = {"x": tal["x"], "cnot": tal["cnot"], "ccx": tal["toffoli"]}
        out.append({
            "circuit": "ec_point_addition", "n": n, "prime_p": p,
            "curve": {"form": "y^2 = x^3 + A*x + B", "A": A, "B": B},
            "constant_point_Q": [x2, y2],
            "curve_affine_points": len(pts),
            "input_coverage": cov, "inputs_tested": len(cases),
            "excluded_by_declared_domain": excluded,
            "domain": "x1 != x2 and x3 != x2",
            "sample_seed": SEED if cov == "random_sample" else None,
            "failures": len(fails), "failure_detail": fails[:5],
            "passed": not fails,
            "ancillas_returned_to_zero": not any(
                f.get("dirty_ancillas") for f in fails),
            "gate_tally_during_simulation": run_counts,
            "gate_tally_in_counting_mode": tal_counts,
            "simulated_circuit_is_counted_circuit": run_counts == tal_counts,
            "toffoli": tal["toffoli"], "t_count": 7 * tal["toffoli"],
            "seconds": round(time.time() - t0, 2)})
        print("  point_add n=%d p=%d %s: %d/%d ok, tally match %s (%.1fs)"
              % (n, p, cov, len(cases) - len(fails), len(cases),
                 run_counts == tal_counts, time.time() - t0), flush=True)
    return out


# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    rng = random.Random(SEED)
    print("== components ==", flush=True)
    comps = validate_components()
    print("  %d component checks, %d failing"
          % (len(comps), sum(1 for c in comps if not c["passed"])), flush=True)

    print("== modular exponentiation ==", flush=True)
    modexp_cfgs = [
        (4, 15, 7, "exhaustive", None),
        (4, 15, 4, "exhaustive", None),
        (5, 21, 2, "exhaustive", None),
        (6, 55, 3, "random_sample", 128),
        (7, 119, 3, "random_sample", 64),
        (8, 247, 3, "random_sample", 32),
        (9, 437, 3, "random_sample", 16),
        (10, 899, 3, "random_sample", 8),
        (12, 3599, 3, "random_sample", 4),
    ]
    mx = validate_modexp(modexp_cfgs, rng)

    print("== ec point addition ==", flush=True)
    ec_cfgs = [
        (4, 11, "exhaustive", None),
        (4, 13, "exhaustive", None),
        (5, 31, "exhaustive", None),
        (5, 23, "exhaustive", None),
        (6, 61, "exhaustive", None),
        (6, 59, "exhaustive", None),
        (7, 127, "exhaustive", None),
        (7, 109, "random_sample", 24),
        (8, 251, "random_sample", 40),
        (9, 509, "random_sample", 20),
        (10, 1021, "random_sample", 10),
        (11, 2039, "random_sample", 5),
        (12, 4093, "random_sample", 3),
    ]
    ec = validate_point_add(ec_cfgs, rng)

    out = {
        "task": "TASK-20260813-c99166", "goal": "GOAL-QRE-001",
        "batch": "BATCH-973b49",
        "convention_reference": "PREREGISTRATION.md clauses 8 and 9",
        "seed": SEED,
        "correspondence_mechanism":
            "One builder (src/circuits.py) emits every circuit into an "
            "abstract machine. Machine(run=True) executes the gate stream on "
            "a classical bit vector while tallying it; Machine(run=False) is "
            "the counting mode used by src/run_counts.py. Each entry below "
            "reports both tallies and whether they are identical, so the "
            "claim 'the simulated circuit is the counted circuit' is checked "
            "rather than asserted.",
        "ancilla_check":
            "The allocator raises DirtyAncilla if any register is released "
            "in state 1, and each entry additionally re-checks that every "
            "qubit outside the declared I/O registers is 0 at the end.",
        "prohibition_statement":
            "This artifact reports simulation outcomes only. It contains no "
            "date, timeline, arrival probability, forecast or policy "
            "statement.",
        "component_validation": comps,
        "modular_exponentiation_validation": mx,
        "ec_point_addition_validation": ec,
        "summary": {
            "component_checks": len(comps),
            "component_checks_failed": sum(1 for c in comps if not c["passed"]),
            "modexp_widths_validated": sorted({r["n"] for r in mx
                                               if r["passed"]}),
            "modexp_widths_failed": sorted({r["n"] for r in mx
                                            if not r["passed"]}),
            "ec_widths_validated": sorted({r["n"] for r in ec if r["passed"]}),
            "ec_widths_failed": sorted({r["n"] for r in ec
                                        if not r["passed"]}),
            "all_tallies_match": all(
                r["simulated_circuit_is_counted_circuit"] for r in mx + ec),
            "total_circuit_instances_simulated":
                sum(c["cases"] for c in comps)
                + sum(r["inputs_tested"] for r in mx + ec),
            "blocking_rule": "A width appearing in *_widths_failed has its "
                             "count withheld from counts.json reporting.",
        },
        "wall_clock_seconds": round(time.time() - t0, 1),
    }
    dest = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "validation.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote", dest, "in %.1fs" % out["wall_clock_seconds"])


if __name__ == "__main__":
    main()

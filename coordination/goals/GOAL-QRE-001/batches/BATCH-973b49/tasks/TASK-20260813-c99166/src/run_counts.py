"""Produce counts.json: exact enumerated Toffoli/T counts vs n for both
circuits, with derived closed forms, residuals and held-out checks.

Every count here is an exact enumeration produced by running the SAME builder
that run_validation.py simulates (circuits.py, PREREGISTRATION clause 8).
No constant is imported from any publication.
"""
import json
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from circuits import Machine, modexp, point_add, mod_add, mod_dbl, modmul_acc  # noqa

T_PER_TOFFOLI = 7  # derived in derive_identities.py; see PREREGISTRATION cl.2


# ---------------------------------------------------------------- utilities
def is_prime(x):
    if x < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if x % q == 0:
            return x == q
    d, r = x - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        y = pow(a, d, x)
        if y in (1, x - 1):
            continue
        for _ in range(r - 1):
            y = y * y % x
            if y == x - 1:
                break
        else:
            return False
    return True


def primes_of_bitlength(n, count):
    out = []
    x = (1 << n) - 1
    while x > (1 << (n - 1)) and len(out) < count:
        if is_prime(x):
            out.append(x)
        x -= 2
    return out


def rsa_modulus(n):
    """Deterministic n-bit RSA-shape modulus: a product of two distinct primes
    of as nearly equal size as possible, chosen by a fixed rule."""
    cands = []
    for bh in ((n + 1) // 2, (n + 1) // 2 + 1, n // 2):
        for bl in (n // 2, n // 2 - 1, (n + 1) // 2):
            if bh < 2 or bl < 2:
                continue
            for p in primes_of_bitlength(bh, 6):
                for q in primes_of_bitlength(bl, 6):
                    if p != q and (p * q).bit_length() == n:
                        cands.append((p * q, min(p, q), max(p, q)))
    if not cands:
        raise ValueError("no modulus for n=%d" % n)
    cands.sort(key=lambda t: (-t[1], -t[0]))   # prefer the most balanced
    return cands[0]


def interp_exact(points, degree):
    """Exact rational interpolation through the first degree+1 points."""
    pts = points[: degree + 1]
    m = [[Fraction(x) ** j for j in range(degree + 1)] + [Fraction(y)]
         for x, y in pts]
    k = degree + 1
    for i in range(k):
        piv = next(r for r in range(i, k) if m[r][i] != 0)
        m[i], m[piv] = m[piv], m[i]
        m[i] = [v / m[i][i] for v in m[i]]
        for r in range(k):
            if r != i and m[r][i] != 0:
                f = m[r][i]
                m[r] = [a - f * b for a, b in zip(m[r], m[i])]
    return [row[k] for row in m]


def poly_eval(c, x):
    return sum(ci * Fraction(x) ** i for i, ci in enumerate(c))


def fmt_poly(c, var="n"):
    terms = []
    for i in reversed(range(len(c))):
        if c[i] == 0:
            continue
        co = c[i]
        cs = str(co) if co.denominator != 1 else str(co.numerator)
        terms.append(cs if i == 0 else
                     ("%s*%s^%d" % (cs, var, i) if i > 1 else "%s*%s" % (cs, var)))
    return " + ".join(terms) if terms else "0"


def coeff_list(c):
    return [str(x) if x.denominator != 1 else int(x) for x in c]


# ---------------------------------------------------------------- counters
def count_modexp(n, N, a):
    m = Machine(run=False)
    E = m.alloc(2 * n, io=True)
    Z = m.alloc(n, io=True)
    t0 = time.time()
    modexp(m, E, Z, a, N)
    return {"n": n, "modulus_N": N, "base_a": a,
            "toffoli": m.counts["ccx"], "cnot": m.counts["cnot"],
            "x": m.counts["x"], "t_count": T_PER_TOFFOLI * m.counts["ccx"],
            "peak_qubits": m.peak, "io_qubits": m.io,
            "ancilla_qubits": m.peak - m.io,
            "seconds": round(time.time() - t0, 3)}


def count_point_add(n, p, x2, y2):
    m = Machine(run=False)
    X = m.alloc(n, io=True)
    Y = m.alloc(n, io=True)
    t0 = time.time()
    point_add(m, X, Y, p, x2, y2)
    e = p - 2
    return {"n": n, "prime_p": p, "e_bitlength_b": e.bit_length(),
            "e_hamming_weight_w": bin(e).count("1"),
            "constant_point": [x2, y2],
            "toffoli": m.counts["ccx"], "cnot": m.counts["cnot"],
            "x": m.counts["x"], "t_count": T_PER_TOFFOLI * m.counts["ccx"],
            "peak_qubits": m.peak, "io_qubits": m.io,
            "ancilla_qubits": m.peak - m.io,
            "seconds": round(time.time() - t0, 3)}


def any_point(p):
    """Deterministic affine point of a nonsingular short Weierstrass curve
    over F_p: fix (x2,y2)=(1,1), take B = 1-1-A = -A, and pick the smallest
    A >= 1 for which 4A^3+27B^2 = A^2(4A+27) is nonzero mod p.
    Only (x2,y2) enters the circuit; A and B are recorded for validation."""
    x2, y2 = 1, 1
    A = 1
    while A % p == 0 or (4 * A + 27) % p == 0:
        A += 1
    B = (y2 * y2 - x2 ** 3 - A * x2) % p
    return x2, y2, A, B


# ---------------------------------------------------------------- main
def main():
    t_start = time.time()
    modexp_ladder = [4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20]
    modexp_holdout = [24, 32, 48, 64, 96, 128]
    ec_ladder_n = list(range(4, 15))
    ec_holdout_n = [15, 16, 20, 24, 32]

    out = {
        "task": "TASK-20260813-c99166",
        "goal": "GOAL-QRE-001",
        "batch": "BATCH-973b49",
        "convention_reference":
            "PREREGISTRATION.md (frozen at commit "
            "5fa40e21de534100449eb03506e3d4840df8b869, clean tree)",
        "gate_set": ["X", "CNOT", "CCX"],
        "t_count_rule": {
            "rule": "T = 7 * Toffoli",
            "status": "derived",
            "derivation": "src/derive_identities.py exhibits an explicit "
                          "Clifford+T circuit with exactly 7 T/Tdg gates, "
                          "multiplies its 8x8 unitary out in exact complex "
                          "arithmetic and compares it with the Toffoli "
                          "permutation matrix; max deviation 3.14e-16 < 1e-12.",
            "not_claimed": "optimality; no smaller-T construction is used or "
                           "cited",
        },
        "measurement_status": {
            "enumerated": "exact gate-by-gate tally of the built circuit",
            "closed_form": "algebraically derived from the construction and "
                           "checked to reproduce every enumerated point exactly",
            "evaluated_from_closed_form": "closed form evaluated at a width "
                                          "too large to enumerate here; "
                                          "arithmetic, not a measurement",
        },
        "prohibition_statement":
            "This artifact states only what these circuits cost under the "
            "frozen convention. It contains no date, timeline, arrival "
            "probability, forecast, migration guidance or policy statement.",
    }

    # ---------------- sub-circuit closed forms (all enumerated) -----------
    print("== sub-circuits ==", flush=True)
    from circuits import (add as _add, mod_add as _madd, mod_dbl as _mdbl,
                          modmul_acc as _mmul, mod_inv as _minv,
                          ctrl_modmul as _cmm)

    def _tally(fn, *a, **k):
        m = Machine(run=False)
        fn(m, *a, **k)
        return m.counts["ccx"]

    sub = []
    for n in range(4, 13):
        p = primes_of_bitlength(n, 1)[0]
        e = p - 2
        b, w = e.bit_length(), bin(e).count("1")
        N = rsa_modulus(n)[0]

        def regs(m, k):
            return [m.alloc(n) for _ in range(k)]

        def f_add(m):
            A, B = regs(m, 2)
            _add(m, A, B)

        def f_madd(m):
            A, B = regs(m, 2)
            _madd(m, A, B, p)

        def f_dbl(m):
            (B,) = regs(m, 1)
            _mdbl(m, B, p)

        def f_mul(m):
            A, B, C = regs(m, 3)
            _mmul(m, A, B, C, p, 1)

        def f_inv(m):
            A, T = regs(m, 2)
            _minv(m, A, T, p)

        def f_cmm(m):
            (Z,) = regs(m, 1)
            (c,) = m.alloc(1)
            k = next(v for v in range(3, N)
                     if __import__("math").gcd(v, N) == 1)
            _cmm(m, c, Z, k, N)

        sub.append({
            "n": n, "p": p, "b": b, "w": w, "N": N,
            "ripple_adder": {"enumerated": _tally(f_add), "form": "2n",
                             "closed_form": 2 * n},
            "modular_addition": {"enumerated": _tally(f_madd),
                                 "form": "10(n+1)", "closed_form": 10 * (n + 1)},
            "modular_doubling": {"enumerated": _tally(f_dbl),
                                 "form": "4(n+1)", "closed_form": 4 * (n + 1)},
            "modmul_quantum_quantum": {"enumerated": _tally(f_mul),
                                       "form": "20n^2+10n-8",
                                       "closed_form": 20 * n * n + 10 * n - 8},
            "fermat_inversion": {
                "enumerated": _tally(f_inv),
                "form": "2(b+w-2)(20n^2+10n-8)",
                "closed_form": 2 * (b + w - 2) * (20 * n * n + 10 * n - 8)},
            "controlled_modular_multiplication": {
                "enumerated": _tally(f_cmm), "form": "20n^2+25n",
                "closed_form": 20 * n * n + 25 * n},
        })
    sub_ok = all(v["enumerated"] == v["closed_form"]
                 for row in sub for k, v in row.items()
                 if isinstance(v, dict))
    out["subcircuit_closed_forms"] = {
        "note": "Every constant used in the two headline closed forms comes "
                "from this table, and every entry here is an exact "
                "enumeration of the built sub-circuit compared with the form "
                "derived from its construction. Toffoli counts only.",
        "all_match": sub_ok, "rows": sub,
    }
    print(" sub-circuit closed forms match enumeration:", sub_ok, flush=True)

    # ---------------- circuit A : modular exponentiation ----------------
    print("== modular exponentiation ==", flush=True)
    rows = []
    for n in modexp_ladder + modexp_holdout:
        N, p1, p2 = rsa_modulus(n)
        a = next(a for a in range(3, N) if __import__("math").gcd(a, N) == 1)
        r = count_modexp(n, N, a)
        r["modulus_factors"] = [p1, p2]
        r["role"] = "fit" if n in modexp_ladder else "holdout"
        rows.append(r)
        print(" n=%-3d N=%-20d toffoli=%-14d %.1fs"
              % (n, N, r["toffoli"], r["seconds"]), flush=True)

    # constant-independence check: same n, different (N, a) -> same Toffoli
    indep = []
    for n in (8, 12):
        N, _, _ = rsa_modulus(n)
        alt = [x for x in range((1 << (n - 1)) + 1, 1 << n, 2)
               if not is_prime(x) and x != N][:1]
        for M in alt:
            a2 = next(a for a in range(3, M)
                      if __import__("math").gcd(a, M) == 1)
            r2 = count_modexp(n, M, a2)
            base = next(r for r in rows if r["n"] == n)
            indep.append({"n": n, "modulus_a": base["modulus_N"],
                          "modulus_b": M,
                          "toffoli_a": base["toffoli"],
                          "toffoli_b": r2["toffoli"],
                          "cnot_a": base["cnot"], "cnot_b": r2["cnot"],
                          "toffoli_identical": base["toffoli"] == r2["toffoli"],
                          "cnot_identical": base["cnot"] == r2["cnot"]})

    fitrows = [r for r in rows if r["role"] == "fit"]
    tof_pts = [(r["n"], r["toffoli"]) for r in fitrows]
    c_tof = interp_exact(tof_pts, 3)
    res_tof = [{"n": r["n"], "role": r["role"], "enumerated": r["toffoli"],
                "closed_form": int(poly_eval(c_tof, r["n"])),
                "residual": r["toffoli"] - int(poly_eval(c_tof, r["n"]))}
               for r in rows]
    q_pts = [(r["n"], r["peak_qubits"]) for r in fitrows]
    c_q = interp_exact(q_pts, 1)
    res_q = [{"n": r["n"], "enumerated": r["peak_qubits"],
              "closed_form": int(poly_eval(c_q, r["n"])),
              "residual": r["peak_qubits"] - int(poly_eval(c_q, r["n"]))}
             for r in rows]

    # independent algebraic derivation of the same closed form
    def modexp_algebraic(n):
        t_modadd = 10 * (n + 1)          # five (n+1)-bit adder passes
        t_ctrl_modmul = 2 * n * (2 + t_modadd) + n
        return 2 * n * t_ctrl_modmul
    alg_ok = all(modexp_algebraic(r["n"]) == r["toffoli"] for r in rows)

    out["circuit_a_modular_exponentiation"] = {
        "definition": "PREREGISTRATION clause 5: |e>|1> -> |e>|a^e mod N>, "
                      "2n-bit exponent register, n-bit modulus, 2n controlled "
                      "modular multiplications, all ancillas returned to |0>. "
                      "QFT/measurement/error-correction excluded.",
        "rows": rows,
        "constant_independence_check": indep,
        "toffoli_closed_form": {
            "form": fmt_poly(c_tof),
            "coefficients_ascending": coeff_list(c_tof),
            "degree_assumed": 3,
            "fit_method": "exact rational interpolation on the four smallest "
                          "ladder widths, then residual-checked at every "
                          "ladder and holdout width",
            "residuals": res_tof,
            "all_residuals_zero": all(x["residual"] == 0 for x in res_tof),
            "independent_algebraic_derivation":
                "2n * [ 2n*(2 + 10(n+1)) + n ] = 40n^3 + 50n^2, from: "
                "modular addition = 5 ripple-adder passes on n+1 bits at 2 "
                "Toffoli/bit = 10(n+1); one controlled modular multiplication "
                "= 2n accumulation steps (2 Toffoli each for the AND of the "
                "control with an exponent-register bit, constants loaded by "
                "CNOT only) plus n controlled swaps; 2n such multiplications.",
            "algebraic_matches_enumeration": alg_ok,
        },
        "t_closed_form": {
            "form": fmt_poly([7 * c for c in c_tof]),
            "coefficients_ascending": coeff_list([7 * c for c in c_tof]),
        },
        "peak_qubits_closed_form": {
            "form": fmt_poly(c_q), "coefficients_ascending": coeff_list(c_q),
            "degree_assumed": 1, "residuals": res_q,
            "all_residuals_zero": all(x["residual"] == 0 for x in res_q)},
        "cnot_and_x_note":
            "CNOT and X counts depend on the Hamming weights of the classical "
            "constants a^(2^j) mod N and are therefore NOT a polynomial in n; "
            "they are reported per row with the exact modulus and base used, "
            "and are not fitted. Toffoli and T are constant-independent "
            "(see constant_independence_check).",
        "evaluated_at_rsa_2048_shape": {
            "n": 2048,
            "status": "evaluated_from_closed_form",
            "toffoli": int(poly_eval(c_tof, 2048)),
            "t_count": 7 * int(poly_eval(c_tof, 2048)),
            "peak_qubits": int(poly_eval(c_q, 2048)),
            "caveat": "This is the cost of THIS construction under the frozen "
                      "convention, enumerated exactly up to n=%d and "
                      % max(r["n"] for r in rows) +
                      "extended by an algebraically derived closed form that "
                      "reproduces every enumerated width with zero residual. "
                      "It is arithmetic, not a measurement, and it is not a "
                      "claim that this construction is the cheapest one.",
        },
    }

    # ---------------- circuit B : elliptic-curve point addition -------------
    print("== elliptic-curve point addition ==", flush=True)
    ec_rows = []
    for n in ec_ladder_n + ec_holdout_n:
        ps = primes_of_bitlength(n, 40)
        chosen, weights = [], set()
        for p in ps:
            w = bin(p - 2).count("1")
            if w not in weights:
                chosen.append(p)
                weights.add(w)
            if len(chosen) == 2:
                break
        for p in chosen:
            x2, y2, A, B = any_point(p)
            r = count_point_add(n, p, x2, y2)
            r["curve_A"], r["curve_B"] = A, B
            r["role"] = "fit" if n in ec_ladder_n else "holdout"
            r["prime_rank"] = "primary" if p == chosen[0] else "secondary"
            ec_rows.append(r)
            print(" n=%-3d p=%-8d w=%-3d toffoli=%-12d %.1fs"
                  % (n, p, r["e_hamming_weight_w"], r["toffoli"],
                     r["seconds"]), flush=True)

    def cmul(n):
        return 20 * n * n + 10 * n - 8

    def ec_algebraic(n, b, w):
        chain = b + w - 2                     # squarings + multiplications
        n_modmul = 8 * chain + 5              # 4 inversion replays + 5 modmuls
        return n_modmul * cmul(n) + 5 * 10 * (n + 1) + 2 * n

    ec_check = [{"n": r["n"], "p": r["prime_p"], "b": r["e_bitlength_b"],
                 "w": r["e_hamming_weight_w"], "enumerated": r["toffoli"],
                 "closed_form": ec_algebraic(r["n"], r["e_bitlength_b"],
                                             r["e_hamming_weight_w"]),
                 "residual": r["toffoli"] - ec_algebraic(
                     r["n"], r["e_bitlength_b"], r["e_hamming_weight_w"])}
                for r in ec_rows]

    # fit in n alone over the primary-prime ladder (residuals expected != 0)
    prim = [r for r in ec_rows if r["prime_rank"] == "primary"]
    prim_fit = [r for r in prim if r["role"] == "fit"]
    c_ec = interp_exact([(r["n"], r["toffoli"]) for r in prim_fit], 3)
    res_ec = [{"n": r["n"], "p": r["prime_p"], "w": r["e_hamming_weight_w"],
               "role": r["role"], "enumerated": r["toffoli"],
               "cubic_in_n": int(poly_eval(c_ec, r["n"])),
               "residual": r["toffoli"] - int(poly_eval(c_ec, r["n"])),
               "relative_residual": float(
                   Fraction(r["toffoli"] - int(poly_eval(c_ec, r["n"])),
                            r["toffoli"]))}
              for r in prim]
    cq_ec = interp_exact([(r["n"], r["peak_qubits"]) for r in prim_fit], 2)
    resq_ec = [{"n": r["n"], "w": r["e_hamming_weight_w"],
                "enumerated": r["peak_qubits"],
                "quadratic_in_n": int(poly_eval(cq_ec, r["n"])),
                "residual": r["peak_qubits"] - int(poly_eval(cq_ec, r["n"]))}
               for r in prim]

    p256 = next(p for p in [(1 << 256) - k for k in range(1, 4000, 2)]
                if is_prime(p))
    b256, w256 = (p256 - 2).bit_length(), bin(p256 - 2).count("1")

    out["circuit_b_ec_point_addition"] = {
        "definition": "PREREGISTRATION clause 6: in-place |x1>|y1> -> "
                      "|x3>|y3> for (x3,y3) = (x1,y1) + Q with Q a classical "
                      "affine point, short Weierstrass curve over F_p, all "
                      "ancillas returned to |0>. QFT/measurement/error "
                      "correction and exceptional cases excluded.",
        "declared_domain": "x1 != x2 AND x3 != x2 (i.e. P != +-Q and "
                           "P != -2Q). See execution_report.yaml deviation "
                           "D-1: the x3 != x2 condition is a refinement of "
                           "the frozen clause 6 domain, recorded rather than "
                           "edited into the pre-registration.",
        "inverter": "Fermat: x^(p-2) mod p by left-to-right square-and-"
                    "multiply, every intermediate in its own clean register, "
                    "result copied out, whole chain reversed. No Euclid/"
                    "Kaliski inverter was derived in this task.",
        "rows": ec_rows,
        "toffoli_closed_form_in_n_b_w": {
            "form": "(8*(b + w - 2) + 5) * (20n^2 + 10n - 8) + 50*(n+1) + 2n",
            "where": "n = bitlength(p); b = bitlength(p-2); "
                     "w = Hamming weight of p-2",
            "derivation": "one quantum x quantum modular multiplication costs "
                          "2n^2 (partial-product AND and its uncomputation) + "
                          "10n(n+1) (n modular additions) + 8(n^2-1) (n-1 "
                          "modular doublings and their inverses) = "
                          "20n^2+10n-8; the Fermat chain is (b-1) squarings "
                          "and (w-1) multiplications, one inversion is a "
                          "forward and a reverse chain, the circuit executes "
                          "four such inversion blocks, and it contains five "
                          "further modular multiplications, five constant "
                          "modular additions and one modular negation (2n).",
            "residual_check": ec_check,
            "all_residuals_zero": all(x["residual"] == 0 for x in ec_check),
        },
        "toffoli_fit_in_n_alone": {
            "form": fmt_poly(c_ec), "coefficients_ascending": coeff_list(c_ec),
            "degree_assumed": 3,
            "basis": "largest prime of each bit length in the fit ladder",
            "residuals": res_ec,
            "note": "Residuals here are NOT zero and are not expected to be: "
                    "the count depends on the Hamming weight of p-2, so no "
                    "function of n alone can be exact. The exact form is "
                    "toffoli_closed_form_in_n_b_w.",
        },
        "peak_qubits_fit_in_n_alone": {
            "form": fmt_poly(cq_ec), "coefficients_ascending": coeff_list(cq_ec),
            "degree_assumed": 2, "residuals": resq_ec,
            "note": "quadratic in n because the Fermat chain holds ~ (b+w-2) "
                    "registers of n qubits simultaneously"},
        "evaluated_at_256_bit_shape": {
            "n": 256, "prime_p": p256, "b": b256, "w": w256,
            "prime_selection": "largest prime below 2^256, computed here",
            "status": "evaluated_from_closed_form",
            "toffoli": ec_algebraic(256, b256, w256),
            "t_count": 7 * ec_algebraic(256, b256, w256),
            "caveat": "Cost of THIS construction (Fermat inversion) under the "
                      "frozen convention. Enumerated exactly up to n=%d and "
                      % max(r["n"] for r in ec_rows) +
                      "extended by a closed form with zero residual at every "
                      "enumerated point. Arithmetic, not a measurement, and "
                      "not a claim of optimality; a Euclid-style inverter was "
                      "not derived here and would change this number.",
        },
    }

    out["wall_clock_seconds"] = round(time.time() - t_start, 1)
    dest = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "counts.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote", dest, "in %.1fs" % out["wall_clock_seconds"])


if __name__ == "__main__":
    main()

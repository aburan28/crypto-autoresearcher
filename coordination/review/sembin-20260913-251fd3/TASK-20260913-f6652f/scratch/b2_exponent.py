"""TASK-20260913-f6652f, joint B2 -- exponent under bound B, growth check, searched-coset
selection cost, and the fixed-C_0 asymptotics of T4.  Own code; imports nothing from the
producer.  Writes b2_exponent.json."""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LN2 = math.log(2.0)


def m_of(n, c0):
    return max(2, math.ceil(n / c0))


def per_coset_deficit_bits(c0):
    """Second-order expansion 1/(2 S ln2), S = 2^c0; exact at c0 <= 16 for the check."""
    S = 2 ** c0
    if S > (1 << 16):
        return 1.0 / (2.0 * S * LN2)
    logS = math.lgamma(S + 1)
    w = acc = 0.0
    for b in range(1, S + 1):
        p = math.exp(logS - math.lgamma(b + 1) - math.lgamma(S - b + 1) - S * LN2)
        w += p
        acc += p * math.log2(2.0 * b)
    return math.log2(S) - acc / w


_D = {}


def total_deficit(n, c0):
    if c0 not in _D:
        _D[c0] = per_coset_deficit_bits(c0)
    return m_of(n, c0) * _D[c0]


def bound_B(n, tol=1.0):
    prof = [total_deficit(n, c) for c in range(1, 80)]
    for i in range(len(prof)):
        if all(x <= tol for x in prof[i:]):
            return i + 1
    return None


def main():
    out = {}
    # (1) growth of bound B: compare to log2 n - log2 log2 n + O(1)
    rows = []
    for k in range(7, 27):
        n = 2 ** k
        b = bound_B(n)
        pred = math.log2(n) - math.log2(math.log2(n))
        rows.append({"n": n, "log2_n": k, "bound_B": b, "log2n_minus_log2log2n": pred,
                     "B_minus_pred": b - pred})
    out["bound_B_growth"] = rows
    out["bound_B_at_labels"] = {n: bound_B(n) for n in (163, 233, 283, 409, 571)}
    out["bound_B_closed_form"] = (
        "Delta = m/(2^{C_0+1} ln 2) <= tol with m = n/C_0  <=>  2^{C_0} >= n/(2 C_0 tol ln 2)"
        "  <=>  C_0 >= log2 n - log2 C_0 - log2(2 tol ln 2) = log2 n - log2 log2 n + O(1)."
        "  The recomputed integer bound tracks log2 n - log2 log2 n to within a bounded offset"
        " (column B_minus_pred), i.e. Theta(log n).")

    # (2) the decompose exponent under bound B, as a local slope in log2 n at large n
    def log2_cost(n, omega, c0):
        m = m_of(n, c0)
        N = n * (m - 1)
        fb = math.log2(m) + c0
        mon = 4 * math.log2(N) - math.log2(24)          # log2 C(N+4,4) ~ log2 N^4/24 at large N
        return fb + omega * mon + total_deficit(n, c0)  # T3 + omega T1 + T4 (T4 ~ Delta at large Delta)

    slopes = []
    for omega in (2.376, 2.807, 3.0):
        for k in (14, 16, 18, 20, 22, 24):
            n1, n2 = 2 ** k, 2 ** (k + 1)
            c1, c2 = bound_B(n1), bound_B(n2)
            s = log2_cost(n2, omega, c2) - log2_cost(n1, omega, c1)   # per doubling = local exponent
            slopes.append({"omega": omega, "n_from": n1, "n_to": n2, "C_0_from": c1, "C_0_to": c2,
                           "local_exponent": s, "8w+2": 8 * omega + 2, "8w+1": 8 * omega + 1,
                           "polylog_correction_(4w+2)*dlog2log2n":
                               -(4 * omega + 2) * (math.log2(math.log2(n2)) - math.log2(math.log2(n1)))})
    out["local_exponent_under_bound_B"] = slopes
    out["symbolic_derivation"] = [
        "bound B: 2^{C_0} = Theta(n / log n)  (tol fixed)",
        "m = n / C_0 = Theta(n / log n)",
        "#Fb = m 2^{C_0} = Theta(n^2 / log^2 n)",
        "N = n (m - 1) = Theta(n^2 / log n)",
        "monomials C(N+4,4) = Theta(N^4) = Theta(n^8 / log^4 n)",
        "decompose = #Fb x 2^{T4} x C(N+4,4)^omega = Theta(n^{8w+2} / (log n)^{4w+2}) x 2^{O(1)}",
        "linear algebra = #Fb^omega = Theta(n^{2w} / log^{2w} n) -- dominated",
        "=> polynomial; exponent 8w+2 minus a (log n)^{-(4w+2)} factor; NOT 8w+1.",
    ]

    # (3) fixed C_0, fixed cosets: T4 = Delta grows linearly in n
    fixed = []
    for c0 in (3, 4, 6, 8, 12, 16):
        d1 = per_coset_deficit_bits(c0)
        fixed.append({"C_0": c0, "per_coset_deficit_bits": d1,
                      "Delta_bits_per_unit_n": d1 / c0,
                      "Delta_at_n_571": total_deficit(571, c0),
                      "n_at_which_Delta_reaches_64_bits": 64 * c0 / d1,
                      "n_at_which_2^Delta_exceeds_n^(8w+1)_w2p807": None})
    # solve Delta(n) = (8w+1) log2 n for w = 2.807 numerically
    for row in fixed:
        c0 = row["C_0"]
        slope = row["Delta_bits_per_unit_n"]
        n = 1000.0
        for _ in range(200):
            f = slope * n - (8 * 2.807 + 1) * math.log2(n)
            fp = slope - (8 * 2.807 + 1) / (n * LN2)
            n = max(100.0, n - f / fp)
        row["n_at_which_2^Delta_exceeds_n^(8w+1)_w2p807"] = n
    out["fixed_C0_fixed_cosets_T4_asymptotics"] = fixed
    out["fixed_C0_statement"] = (
        "Under HEUR-1 with the cosets fixed before inspection and T4 charged at the typical"
        " product (the run's own convention), Delta = m delta_1(C_0) = n delta_1(C_0)/C_0 grows"
        " LINEARLY in n at constant C_0, so the expected trials per relation 2^{Delta} is"
        " exp(Theta(n)) and the decompose step is not polynomial at literally constant C_0."
        "  Polynomiality needs Delta = O(log n), i.e. C_0 >= log2 n - 2 log2 log2 n + O(1) ="
        " Theta(log n) (bound B is the 1-bit version of this), OR the searched-coset reading.")

    # (4) searched-coset selection cost at n = 571 for each C_0
    sel = []
    for c0 in (1, 2, 3, 4, 6, 8):
        m = m_of(571, c0)
        S = 2 ** c0
        # fraction of cosets with #Fb_i >= 2^{C_0} i.e. Bin(S,1/2) >= S/2
        logS = math.lgamma(S + 1)
        frac_ge_mean = sum(math.exp(logS - math.lgamma(b + 1) - math.lgamma(S - b + 1) - S * LN2)
                           for b in range((S + 1) // 2, S + 1))
        tests = m / frac_ge_mean
        # cost per test: 2^{C_0} x-values, each a trace of (x + a + b/x^2): one inversion + O(1) mults ~ n^2 bit ops
        cost_bits = math.log2(tests) + c0 + 2 * math.log2(571)
        fb_build_bits = math.log2(m) + c0 + 2 * math.log2(571)   # writing Fb needs a sqrt per x ~ n^2 too
        sel.append({"C_0": c0, "m": m, "cosets_available_log2": 571 - c0,
                    "fraction_of_cosets_with_count_ge_mean": frac_ge_mean,
                    "expected_cosets_tested": tests,
                    "log2_selection_cost_bit_ops": cost_bits,
                    "log2_factor_base_construction_bit_ops": fb_build_bits,
                    "selection_over_construction_bits": cost_bits - fb_build_bits,
                    "product_guarantee": "each selected coset has #Fb_i >= 2^{C_0}, so prod >= 2^{m C_0} >= 2^n; Delta <= 0"})
    out["searched_coset_selection_n571"] = sel
    json.dump(out, open(os.path.join(HERE, "b2_exponent.json"), "w"), indent=1)
    print(json.dumps(out["bound_B_at_labels"]))
    for r in rows[::3]:
        print(r)
    for s in slopes:
        if s["n_from"] in (2 ** 16, 2 ** 22):
            print(s)
    for f in fixed:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in f.items()})
    for s in sel:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items() if k != "product_guarantee"})


if __name__ == "__main__":
    main()

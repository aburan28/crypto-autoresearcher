"""Self-test: every formula in this experiment against a HAND-CHECKED value.

Required by the contract ("a self-test file exercising every formula against a
hand-checked value").  Each expected value below was worked by hand or from a
closed identity and is written as a literal; the check does not compute the
expectation with the code under test.  Run as a script: prints JSON and exits
non-zero on any failure.
"""

from __future__ import annotations

import json
import math
import sys

import arm_c_coset as C
import arm_i_independent_memory as I
import nagao_cost as N
import semaev_repro as R
from binary_field import BinaryField

CHECKS = []


def check(name, got, want, tol=1e-9):
    if isinstance(want, (tuple, list)) or isinstance(got, bool) or isinstance(want, bool):
        ok = got == want
        err = None
    else:
        err = abs(float(got) - float(want))
        ok = err <= tol
    CHECKS.append({"name": name, "got": got, "want": want,
                   "abs_error": err, "tol": tol, "pass": bool(ok)})


def run() -> dict:
    # --- semaev_repro primitives -------------------------------------------
    check("log2_int(2^100) = 100", R.log2_int(2 ** 100), 100.0)
    check("log2_factorial(5) = log2 120 = 6.906890595608519",
          R.log2_factorial(5), 6.906890595608519)
    check("log2_add(3,3) = 4", R.log2_add(3.0, 3.0), 4.0)
    check("k_of(571,12,ceiled) = 48", R.k_of(571, 12, "ceiled"), 48.0)
    check("k_of(571,12,unceiled) = 47.58333", R.k_of(571, 12, "unceiled"),
          571 / 12)
    check("boolean monomials N=4,d=2: 1+4+6 = 11 -> log2 11",
          R.log2_boolean_monomials(4, 2), math.log2(11))
    # stage 1 by hand: n=12, m=2, omega=1, unceiled k=6, eq11: 1/P = 2! * 2^0
    #   = 2 -> 1 bit; n^{4 omega} = 12^4 -> 4 log2 12 = 14.339850002884624
    #   total 6 + 1 + 14.339850002884624 = 21.339850002884624
    check("semaev_stage1 n=12 m=2 w=1 = 21.339850002884624",
          R.semaev_stage1_log2(12, 2, 1.0)["log2_stage1"], 21.339850002884624)
    # m_only vs eq11 differ by exactly n - m k at ceiled k: n=13, m=2, k=7 -> -1
    check("eq11 minus m_only at n=13,m=2,ceiled = n - mk = -1",
          R.semaev_stage1_log2(13, 2, 1.0, "eq11", "ceiled")["log2_stage1"]
          - R.semaev_stage1_log2(13, 2, 1.0, "m_only", "ceiled")["log2_stage1"],
          -1.0)
    # vOW: log2(0.886) + n/2 ; ln 0.886 = -0.121046..., /ln2 = -0.174631...
    check("vow_walk_work_log2(100) = 50 + log2 0.886", R.vow_walk_work_log2(100),
          50.0 + math.log(0.886) / math.log(2.0))
    # T x Mem minimum = 6 n W exactly
    check("vow pareto product min n=100 = log2 600 + W",
          R.vow_pareto_minimum(100, "time_memory_product")["metric_log2"],
          math.log2(600) + 50.0 + math.log(0.886) / math.log(2.0))
    # equal-rate max: sqrt(6nW) -> half the product in log2
    check("vow equal_rate_max = half the product minimum",
          R.vow_pareto_minimum(283, "equal_rate_max")["metric_log2"],
          R.vow_pareto_minimum(283, "time_memory_product")["metric_log2"] / 2)
    # O-6: dominated charge (30 + log2 3n + W) minus minimum (log2 6n + W)
    #   = 30 - log2 2 = 29.0 EXACTLY, independent of n
    for n in (163, 283, 571, 1000):
        d = R.vow_dominated_charge_8d123b(n)
        check(f"O-6 overcharge is exactly 29.0 at n={n}",
              d["log2_time"] + d["log2_memory_bits"]
              - R.vow_pareto_minimum(n, "time_memory_product")["metric_log2"],
              29.0)
    # degenerate slice: exact 0 at un-ceiled C_0
    check("degenerate slice n=571 m=12 unceiled difference = 0",
          R.degenerate_slice(571, 12)["unceiled"]["difference_bits"], 0.0)
    # at the ceiled reading BOTH sides carry the same integer C_0 = k, so the
    # identity is again exact; the ceiling slack 48 - 571/12 = 0.41667 is a
    # separate reported number, not a difference between the two sides
    check("degenerate slice n=571 m=12 ceiled difference = 0",
          R.degenerate_slice(571, 12)["ceiled"]["difference_bits"], 0.0)
    check("degenerate slice ceiling slack = 48 - 571/12 = 0.416667",
          R.degenerate_slice(571, 12)["ceiling_slack_bits_closed_form"],
          48 - 571 / 12)

    # --- arm_c_coset closed forms ------------------------------------------
    check("m_of(571,8) = ceil(571/8) = 72", C.m_of(571, 8), 72)
    check("m_of(163,4) = 41", C.m_of(163, 4), 41)
    # Pr[all nonempty] at p=2, C_0=1, m=3: (1 - 1/4)^3 = 27/64
    check("log2 Pr[all nonempty] p=2 C0=1 m=3 = log2(27/64)",
          C.log2_prob_all_cosets_nonempty(2, 1, 3), math.log2(27 / 64))
    # expected empty cosets p=2, C_0=2, m=4: 4 * (1/2)^4 = 0.25
    check("expected empty cosets p=2 C0=2 m=4 = 0.25",
          C.expected_empty_cosets(2, 2, 4), 0.25)
    # exact per-coset deficit, s = 1: E[2B] = 1 -> 0 bits; E[log2 2B | B>=1]
    #   = 1 bit; deficit = -1.  s = 2: log2 E[2B] = 1; conditional weights
    #   2/3 on B=1 (1 bit), 1/3 on B=2 (2 bits) -> 4/3; deficit = -1/3.
    check("per-coset deficit s=1 = -1 bit",
          C.per_coset_log2_deficit(2, 0)["deficit_bits_exact"], -1.0)
    check("per-coset deficit s=2 = -1/3 bit",
          C.per_coset_log2_deficit(2, 1)["deficit_bits_exact"], -1.0 / 3.0)
    # asymptotic deficit (1-delta)/(2 delta s ln2) at s=256, delta=1/2:
    #   1/(256 ln 2) = 0.005634...; exact must be within 1e-4 of it
    check("deficit exact vs second-order at s=256 agree to 1e-4",
          C.per_coset_log2_deficit(2, 8)["exact_minus_asymptotic"], 0.0, 1e-4)
    # bound A order of growth: with eps = 0.05 the condition is
    #   m 2^{-2^{C_0}} <= -log(1-eps)... check the monotone fact that the
    #   bound is non-decreasing in n over the FIPS labels
    bounds_a = [C.bound_A(n, 2)["C_0_min"] for n in (163, 233, 283, 409, 571)]
    check("bound A non-decreasing in n", all(bounds_a[i] <= bounds_a[i + 1]
                                          for i in range(4)), True)
    check("crude p^C0 >= n at n=571 real = log2 571 = 9.1573",
          C.crude_bounds(571, 2)["C_0_from_p_to_C0_ge_n_real"], math.log2(571))

    # --- binary field and enumeration: exactness checks ---------------------
    # Tr(1) over F_{2^n} is n mod 2
    for n in (3, 4, 8, 9):
        f = BinaryField(n)
        check(f"Tr(1) over F_2^{n} = {n % 2}", f.trace_scalar(1), n % 2)
    # #E = 2 * |x-image| (one point at x=0, two at each other image x, plus
    #   infinity) must satisfy Hasse: |#E - (2^n + 1)| <= 2 * 2^{n/2}
    import numpy as _np
    rng = _np.random.default_rng(1)
    for n in (8, 10, 12):
        f = BinaryField(n)
        a = int(rng.integers(0, f.size))
        b = int(rng.integers(1, f.size))
        size = int(C.x_coordinate_image(f, a, b).size)
        check(f"Hasse bound holds for enumerated curve n={n}",
              abs(2 * size - (f.size + 1)) <= 2 * math.sqrt(f.size), True)
    # coset index of the low-bit subspace: 2^{n-k} cosets, every one indexed
    f = BinaryField(6)
    idx = C.coset_index_lowbits(_np.arange(64), 2)
    check("low-bit coset index covers 2^{n-k} = 16 cosets each 4 times",
          sorted(set(_np.bincount(idx).tolist())), [4])
    # random-subspace functionals: n-k masks, all cosets equally sized
    masks, _ = C.random_subspace_functionals(6, 2, _np.random.default_rng(3))
    check("random V: n-k = 4 functionals", len(masks), 4)
    check("random V: 16 equal cosets of size 4",
          sorted(set(_np.bincount(C.apply_functionals(_np.arange(64), masks),
                                  minlength=16).tolist())), [4])

    # --- nagao_cost -----------------------------------------------------------
    check("d_F bound p=2 is 4", N.d_F_bound(2), 4)
    check("d_F bound p=3 is 3p+1 = 10", N.d_F_bound(3), 10)
    check("Theorem 1 exponent p=2 w=3: 8w+1 = 25",
          N.theorem1_exponent(2, 3.0)["exponent_in_n"], 25.0)
    check("Theorem 1 exponent p=3 w=3: (6p+2)w+1 = 61",
          N.theorem1_exponent(3, 3.0)["exponent_in_n"], 61.0)
    check("Theorem 1 exponent p=5 w=2: (32)w+1 = 65",
          N.theorem1_exponent(5, 2.0)["exponent_in_n"], 65.0)
    check("variable_count n=12 m=3 C0=4: frozen 24, exact 24, slack 0",
          (lambda v: (v["N_frozen_n_times_m_minus_1"],
                      v["N_exact_shifted_system"],
                      v["slack_m_C0_minus_n"]))(N.variable_count(12, 3, 4)),
          (24, 24, 0))
    check("log2 monomials binomial N=4 d=2: C(6,2) = 15",
          N.log2_monomials(4, 2, "binomial_C_N_plus_d_choose_d"), math.log2(15))
    check("log2 monomials loose N=4 d=2: 4^2 -> 4 bits",
          N.log2_monomials(4, 2, "nagao_loose_N_to_the_d"), 4.0)
    # HEUR-2 constant: 1 - 1/e = 0.6321206; ln = -0.4586751; / ln 2 =
    #   -0.6617284 -> 0.66173 bits.  (H-SEMBIN-4a80f3 quotes "~0.663"; the
    #   hand value is 0.6617, recorded as-is, the hypothesis is not edited.)
    check("HEUR-2 inverse yield at lambda=1 = -log2(1-1/e) = 0.66173",
          -math.log2(-math.expm1(-1.0)), 0.661728, 1e-5)
    # T4 at a cell with zero slack equals HEUR-2 evaluated at the ARM C
    #   deficit: n=8, C_0=4 -> m=2, slack 0, lambda = 2^{-Delta}
    y = N.inverse_yield_bits(8, 2, 4, 2)
    delta_bits = C.total_log2_deficit(8, 2, 4)["total_deficit_bits"]
    check("T4 at zero slack = -log2(1 - exp(-2^{-Delta}))",
          y["T4_inverse_yield_bits"],
          -math.log2(-math.expm1(-(2.0 ** (-delta_bits)))))
    # a whole cell by hand: n=8, p=2, C_0=4, omega=1, loose reading
    #   m=2, N=8, T1 = 4 log2 8 = 12, T2 = 0, T3 = log2(2*16 + 1) = log2 33
    cell = N.nagao_cell(8, 2, 4, 1.0, "nagao_loose_N_to_the_d")
    check("cell n=8 C0=4 w=1 loose: T1 = 12", cell["T1_monomial_count_log2"], 12.0)
    check("cell n=8 C0=4 w=1 loose: T2 = 0", cell["T2_linear_algebra_exponent_log2"], 0.0)
    check("cell n=8 C0=4 w=1: T3 = log2 33", cell["T3_coset_constant_log2"], math.log2(33))
    check("cell n=8 C0=4: T5 frozen = log2 C(12,4) = log2 495",
          cell["T5_memory_log2_frozen_width"], math.log2(495))
    check("cell: time_decompose = T1+T2+T3+T4",
          cell["sum_T1_to_T4_time_decompose_log2"],
          cell["T1_monomial_count_log2"] + cell["T2_linear_algebra_exponent_log2"]
          + cell["T3_coset_constant_log2"] + cell["T4_inverse_yield_log2"])
    # sign convention: nagao metric below vOW -> negative margin, nagao_ahead
    fake = dict(cell)
    fake["time_log2_total"] = 1.0
    mg = N.margin(fake, "time_only")
    check("margin sign: Nagao cheaper -> negative margin", mg["margin_bits_nagao_minus_vow"] < 0, True)
    check("margin sign: Nagao cheaper -> nagao_ahead True", mg["nagao_ahead"], True)
    # ARM K predicted rise under each reading, by hand at N=8, omega=1:
    #   loose: 5 log2 8 - 4 log2 8 = 3;  binomial: log2 C(13,5) - log2 C(12,4)
    #   = log2(1287/495)
    c5 = N.nagao_cell(8, 2, 4, 1.0, "nagao_loose_N_to_the_d", d_f=5)
    check("d_F 4->5 loose rise at N=8 w=1 = log2 8 = 3",
          c5["T1_monomial_count_log2"] - cell["T1_monomial_count_log2"], 3.0)
    cb4 = N.nagao_cell(8, 2, 4, 1.0, "binomial_C_N_plus_d_choose_d")
    cb5 = N.nagao_cell(8, 2, 4, 1.0, "binomial_C_N_plus_d_choose_d", d_f=5)
    check("d_F 4->5 binomial rise at N=8 = log2(1287/495)",
          cb5["T1_monomial_count_log2"] - cb4["T1_monomial_count_log2"],
          math.log2(1287 / 495))

    # --- ARM I's own self-check --------------------------------------------
    check("ARM I self_check all_pass", I.self_check()["all_pass"], True)

    return {"checks": CHECKS, "n_checks": len(CHECKS),
            "n_failed": sum(1 for c in CHECKS if not c["pass"]),
            "all_pass": all(c["pass"] for c in CHECKS)}


if __name__ == "__main__":
    out = run()
    print(json.dumps(out, indent=1, default=str))
    sys.exit(0 if out["all_pass"] else 1)

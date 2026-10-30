#!/usr/bin/env python3
"""Blind re-derivation for sheriff case SHF-20261028-0f3f64, reader `stark` (B2).

Independent of the producer's Rust implementation.  Inputs are the
construction as stated in the module docs of crypto:src/zk/stark_v2.rs
(items 1-5, "Transcript", "Soundness") and the public parameters.  The one
constant copied from the producer tree is the BLS12-381 scalar modulus
(crypto:src/bls12_381/fq.rs:21), which is the standard published value.
Polynomial arithmetic, the coset DFT, the composition, the DEEP quotient
and the FRI fold are re-implemented here from their textbook definitions.

Writes stark_rederive.json and prints a human-readable log (kept as
stark_rederive.out by the caller).  Seeded; deterministic.
"""
import json
import math
import os
import random
from fractions import Fraction

import sympy

R = int("73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001", 16)
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SEED = 20261028
rng = random.Random(SEED)
RESULTS = {"seed": SEED, "checks": {}}
CTX = [""]


def record(name, ok, **detail):
    name = CTX[0] + name
    RESULTS["checks"][name] = {"ok": bool(ok), **detail}
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {json.dumps(detail, default=str)}")


def inv(a):
    a %= R
    assert a != 0, "inverse of zero"
    return pow(a, R - 2, R)


# ── polynomials over F_r: coefficient lists, low -> high ─────────────
def peval(c, x):
    acc = 0
    for a in reversed(c):
        acc = (acc * x + a) % R
    return acc


def pmul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % R
    return out


def padd(a, b):
    n = max(len(a), len(b))
    return [((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % R for i in range(n)]


def deg(c):
    for i in range(len(c) - 1, -1, -1):
        if c[i] % R:
            return i
    return -1


def div_linear(c, a):
    """Divide c(X) by (X - a): (quotient, remainder) by synthetic division."""
    m = len(c)
    q = [0] * (m - 1)
    acc = 0
    for i in range(m - 1, -1, -1):
        acc = (acc * a + c[i]) % R
        if i > 0:
            q[i - 1] = acc
    return q, acc


def interpolate(xs, ys):
    n = len(xs)
    res = [0] * n
    for i in range(n):
        num, den = [1], 1
        for j in range(n):
            if j != i:
                num = pmul(num, [(-xs[j]) % R, 1])
                den = den * (xs[i] - xs[j]) % R
        s = ys[i] * inv(den) % R
        for k in range(len(num)):
            res[k] = (res[k] + s * num[k]) % R
    return res


def coset_coeffs(table, g, w):
    """Coefficients of the unique polynomial of degree < L through
    (g*w^i, table[i]): inverse DFT of p(gX) on <w>, then undo the shift."""
    L = len(table)
    winv, Linv, ginv = inv(w), inv(L), inv(g)
    out = []
    for j in range(L):
        wj = pow(winv, j, R)
        s, x = 0, 1
        for t in table:
            s = (s + t * x) % R
            x = x * wj % R
        out.append(s * Linv % R * pow(ginv, j, R) % R)
    return out


def coset_degree(table, g, w):
    return deg(coset_coeffs(table, g, w))


# ── 1. field facts ────────────────────────────────────────────────────
def field_facts():
    fac = sympy.factorint(R - 1)
    two_adicity = fac.get(2, 0)
    gen7 = all(pow(7, (R - 1) // p, R) != 1 for p in fac)
    qnr7 = pow(7, (R - 1) // 2, R) == R - 1
    seven_outside_H2_32 = pow(7, 2 ** 32, R) != 1
    log2r = math.log2(R)
    RESULTS["field"] = {
        "r_hex": hex(R), "r_bits": R.bit_length(), "log2_r": log2r,
        "r_is_prime": bool(sympy.isprime(R)),
        "r_minus_1_factorisation": {str(p): e for p, e in sorted(fac.items())},
        "two_adicity": two_adicity, "seven_generates_Fr_star": gen7,
        "seven_is_qnr": qnr7, "seven_not_in_any_2power_subgroup_le_2^32": seven_outside_H2_32,
    }
    record("field.r_prime_and_log2", sympy.isprime(R) and abs(log2r - 254.857) < 0.001,
           log2_r=round(log2r, 4))
    record("field.two_adicity_32_bounds_L", two_adicity == 32, two_adicity=two_adicity)
    record("field.g7_generator_so_coset_misses_H_lde", gen7 and qnr7 and seven_outside_H2_32,
           generator=gen7, qnr=qnr7)


# ── 2. domains ────────────────────────────────────────────────────────
def setup(n, beta):
    L = n * beta
    wn = pow(7, (R - 1) // n, R)
    wL = pow(7, (R - 1) // L, R)
    H = [pow(wn, i, R) for i in range(n)]
    C = [7 * pow(wL, i, R) % R for i in range(L)]
    return L, wn, wL, H, C


def random_ood_point(n, L):
    while True:
        z = rng.randrange(R)
        if pow(z, n, R) != 1 and pow(z * inv(7) % R, L, R) != 1:
            return z


def comp_at(x, fx, fwx, H, n, trans, boundary, a1, a2):
    """Module docs item 2: a1*C(f(x),f(wx))/Z(x) + sum_k a2^k (f(x)-v_k)/(x-w^{p_k}),
    Z(x) = (x^n - 1)/(x - w^{n-1}); `trans` is a callable C(prev, next)."""
    Z = (pow(x, n, R) - 1) * inv(x - H[n - 1]) % R
    acc = a1 * trans(fx, fwx) % R * inv(Z) % R
    p = 1
    for pos, v in boundary:
        acc = (acc + p * ((fx - v) % R) % R * inv(x - H[pos])) % R
        p = p * a2 % R
    return acc


def deep_at(x, fx, fwx, cx, z, ood, gam, lam):
    """Module docs item 4."""
    fz, fwz, cz = ood
    i = inv(x - z)
    s = (gam[0] * (fx - fz) + gam[1] * (fwx - fwz) + gam[2] * (cx - cz)) % R * i % R
    return (lam[0] + lam[1] * x) % R * s % R


def fold_eval(T, dom, alpha):
    """FRI fold on evaluations: ((f(x)+f(-x)) + alpha (f(x)-f(-x))/x)/2 at x^2."""
    half = len(T) // 2
    i2 = inv(2)
    out, nd = [], []
    for i in range(half):
        a, b, x = T[i], T[i + half], dom[i]
        assert dom[i + half] == (-x) % R
        out.append(((a + b) + alpha * ((a - b) % R) % R * inv(x)) % R * i2 % R)
        nd.append(x * x % R)
    return out, nd


def fold_coeffs(c, alpha):
    """Same fold on coefficients: p = pe(X^2) + X po(X^2) -> pe + alpha po."""
    c = c + [0] * (len(c) % 2)
    return [(c[2 * j] + alpha * c[2 * j + 1]) % R for j in range(len(c) // 2)]


def fri_final_layer(T, dom, folds):
    for _ in range(folds):
        T, dom = fold_eval(T, dom, rng.randrange(R))
    return T


# ── 3. DEEP algebra ───────────────────────────────────────────────────
def deep_algebra(n=8, beta=4):
    L, wn, wL, H, C = setup(n, beta)
    record("domain.omega_L^beta_equals_omega_n", pow(wL, beta, R) == wn, n=n, beta=beta)
    record("domain.coset_disjoint_from_H_trace", not (set(C) & set(H)))
    f = [rng.randrange(R) for _ in range(n)]
    g = [f[j] * pow(wn, j, R) % R for j in range(n)]          # g(X) = f(wX)
    T = [peval(f, x) for x in C]
    record("domain.f(wx)_is_table_index_plus_beta_mod_L",
           all(T[(i + beta) % L] == peval(f, wn * C[i] % R) for i in range(L)))
    z = random_ood_point(n, L)
    wz = wn * z % R
    # current form: (f(wX) - f(wz)) / (X - z)
    gz = peval(g, z)
    record("deep.g(z)_equals_f(wz)", gz == peval(f, wz))
    q, rem = div_linear([(g[0] - gz) % R] + g[1:], z)
    record("deep.term2_current_(f(wX)-f(wz))/(X-z)_is_polynomial", rem == 0, quotient_degree=deg(q),
           bound="< n-1", n=n)
    _, rem_bad = div_linear([(g[0] - gz - 1) % R] + g[1:], z)
    record("deep.term2_wrong_claim_leaves_pole", rem_bad != 0)
    # pre-a232be6a8 form: (f(X) - f(wz)) / (X - wz)
    q_old, rem_old = div_linear([(f[0] - peval(f, wz)) % R] + f[1:], wz)
    record("deep.term2_old_(f(X)-f(wz))/(X-wz)_is_also_polynomial", rem_old == 0,
           quotient_degree=deg(q_old))
    # mixed (invalid) form: (f(X) - f(wz)) / (X - z)
    _, rem_mixed = div_linear([(f[0] - peval(f, wz)) % R] + f[1:], z)
    record("deep.term2_mixed_(f(X)-f(wz))/(X-z)_is_not_polynomial", rem_mixed != 0)
    # the same on the coset, from the table alone
    tab = [((T[(i + beta) % L] - gz) * inv(C[i] - z)) % R for i in range(L)]
    d_tab = coset_degree(tab, 7, wL)
    record("deep.term2_on_coset_from_shifted_table_degree", d_tab == n - 2, degree=d_tab, L=L)
    tab_bad = [((T[(i + beta) % L] - gz - 1) * inv(C[i] - z)) % R for i in range(L)]
    d_bad = coset_degree(tab_bad, 7, wL)
    record("deep.term2_on_coset_wrong_claim_is_full_degree", d_bad >= L - 2, degree=d_bad)


# ── 4. composition degree, DEEP degree, degree adjustment, FRI ───────
def degree_checks(n=8, beta=4):
    L, wn, wL, H, C = setup(n, beta)
    dbl = lambda p, nx: (nx - 2 * p) % R                   # affine: -2*prev + next
    boundary = [(0, 1), (n - 1, 2 ** (n - 1))]
    trace = [2 ** i for i in range(n)]
    f = interpolate(H, trace)
    T = [peval(f, x) for x in C]
    a1, a2 = rng.randrange(R), rng.randrange(R)
    comp = [comp_at(C[i], T[i], T[(i + beta) % L], H, n, dbl, boundary, a1, a2) for i in range(L)]
    dc = coset_degree(comp, 7, wL)
    record("comp.valid_trace_degree", dc <= n - 2, degree=dc, claim="< n", derived="<= n-2")
    # quadratic transition with a valid trace (aside: degree < n would still hold)
    sq = lambda p, nx: (p * p - nx) % R
    tq = [3]
    for _ in range(n - 1):
        tq.append(tq[-1] * tq[-1] % R)
    fq_ = interpolate(H, tq)
    Tq = [peval(fq_, x) for x in C]
    cq = [comp_at(C[i], Tq[i], Tq[(i + beta) % L], H, n, sq, [(0, 3)], a1, a2) for i in range(L)]
    record("comp.aside_quadratic_transition_degree", coset_degree(cq, 7, wL) <= n - 1,
           degree=coset_degree(cq, 7, wL), note="degree-2 transitions also give < n; the C7 defect was non-polynomial closures")
    # false statement: one broken transition
    bad = trace[:]
    bad[n - 1] = 12345
    fb = interpolate(H, bad)
    Tb = [peval(fb, x) for x in C]
    cb = [comp_at(C[i], Tb[i], Tb[(i + beta) % L], H, n, dbl, [(0, 1), (n - 1, 12345)], a1, a2)
          for i in range(L)]
    record("comp.broken_transition_not_low_degree", coset_degree(cb, 7, wL) >= n,
           degree=coset_degree(cb, 7, wL))

    # OOD values and DEEP quotient (honest)
    z = random_ood_point(n, L)
    ccoef = coset_coeffs(comp, 7, wL)
    fz, fwz = peval(f, z), peval(f, wn * z % R)
    cz = comp_at(z, fz, fwz, H, n, dbl, boundary, a1, a2)
    record("ood.air_at_z_matches_comp_polynomial_at_z", cz == peval(ccoef, z))
    gam = [rng.randrange(R) for _ in range(3)]
    lam = [rng.randrange(R) for _ in range(2)]
    D = [deep_at(C[i], T[i], T[(i + beta) % L], comp[i], z, (fz, fwz, cz), gam, lam) for i in range(L)]
    dD = coset_degree(D, 7, wL)
    record("deep.honest_D_degree_lt_n", dD <= n - 1, degree=dD, n=n)
    lam0 = [lam[0], 0]
    D0 = [deep_at(C[i], T[i], T[(i + beta) % L], comp[i], z, (fz, fwz, cz), gam, lam0) for i in range(L)]
    record("deep.honest_bracket_degree_lt_n_minus_1", coset_degree(D0, 7, wL) <= n - 2,
           degree=coset_degree(D0, 7, wL))

    # degree-n committed trace f' = f + X^n - 1 (agrees with the trace on H)
    fp = padd(f, [R - 1] + [0] * (n - 1) + [1])
    record("deg_n.f_prime_equals_trace_on_H", all(peval(fp, h) == t % R for h, t in zip(H, trace)))
    Tp = [peval(fp, x) for x in C]
    compp = [comp_at(C[i], Tp[i], Tp[(i + beta) % L], H, n, dbl, boundary, a1, a2) for i in range(L)]
    record("deg_n.composition_still_lt_n", coset_degree(compp, 7, wL) <= n - 1,
           degree=coset_degree(compp, 7, wL))
    oodp = (peval(fp, z), peval(fp, wn * z % R), None)
    czp = comp_at(z, oodp[0], oodp[1], H, n, dbl, boundary, a1, a2)
    oodp = (oodp[0], oodp[1], czp)
    Dp = [deep_at(C[i], Tp[i], Tp[(i + beta) % L], compp[i], z, oodp, gam, lam) for i in range(L)]
    Dp0 = [deep_at(C[i], Tp[i], Tp[(i + beta) % L], compp[i], z, oodp, gam, lam0) for i in range(L)]
    record("deg_n.adjusted_D_has_degree_n_fails_bound", coset_degree(Dp, 7, wL) == n,
           degree=coset_degree(Dp, 7, wL))
    record("deg_n.lambda1_zero_D_has_degree_n_minus_1_passes_bound", coset_degree(Dp0, 7, wL) == n - 1,
           degree=coset_degree(Dp0, 7, wL),
           note="probability ~1/r; the witness on H is still valid, so no false statement is accepted")

    # FRI fold: evaluation formula == coefficient fold; log2 n folds -> beta values
    alpha = rng.randrange(R)
    Dcoef = coset_coeffs(D, 7, wL)
    F1, dom1 = fold_eval(D, C, alpha)
    record("fri.eval_fold_equals_coeff_fold",
           all(F1[i] == peval(fold_coeffs(Dcoef, alpha), dom1[i]) for i in range(len(F1))))
    folds = int(math.log2(n))
    fin = fri_final_layer(D, C, folds)
    record("fri.deg_lt_n_folds_to_constant_beta_layer", len(fin) == beta and len(set(fin)) == 1,
           final_size=len(fin))
    finp = fri_final_layer(Dp, C, folds)
    record("fri.deg_n_does_not_fold_to_constant", len(set(finp)) > 1, final_size=len(finp))
    finb = fri_final_layer([rng.randrange(R) for _ in range(L)], C, int(math.log2(L)))
    record("fri.control_any_table_folds_to_one_value_with_log2_L_folds", len(finb) == 1,
           note="this is the degree-bound-free FRI that the verifier's layer-count check (stark_v2.rs:766) excludes")
    finb2 = fri_final_layer([rng.randrange(R) for _ in range(L)], C, folds + 1)
    record("fri.control_random_table_with_one_extra_fold_is_not_constant", len(set(finb2)) > 1,
           final_size=len(finb2))


# ── 5. soundness arithmetic (module docs "Soundness") ────────────────
def soundness():
    out = {}
    for name, beta, q in (("default", 8, 80), ("fast", 4, 20)):
        out[f"query_term_log2_{name}"] = -q * math.log2(beta)
    record("eps.query_term_default_2^-240", out["query_term_log2_default"] == -240.0,
           log2=out["query_term_log2_default"])
    record("eps.query_term_fast_2^-40", out["query_term_log2_fast"] == -40.0,
           log2=out["query_term_log2_fast"])

    def stated(n, L, k):
        return (Fraction(k + 1, R) + Fraction(2 * n + k, R - n - L)
                + Fraction((5 + int(math.log2(n))) * L, R))

    def derived(n, L, k, lambda1_zero=False):
        # ALI pole cancellation: a nonzero polynomial of degree <= max(1, k-1) in (a1, a2)
        # OOD: Comp*Z*prod(X-w^p) - N has degree <= 2n+k-2 (2n+k-1 if deg f may be n)
        # proximity: 3 gammas + 2 lambdas + log2 n folds at L/r each (unique-decoding form)
        ood_deg = 2 * n + k - (1 if lambda1_zero else 2)
        return (Fraction(max(1, k - 1), R) + Fraction(ood_deg, R - n - L)
                + Fraction((5 + int(math.log2(n))) * L, R))

    worst = None
    rows = []
    for logL in range(2, 33):
        L = 2 ** logL
        for logn in range(1, logL):
            n = 2 ** logn
            for k in (1, n):
                s = float(stated(n, L, k))
                d = float(derived(n, L, k, lambda1_zero=True))
                if worst is None or s > worst[0]:
                    worst = (s, n, L, k, d)
                if logL == 32 and logn in (1, 16, 31):
                    rows.append({"n": n, "L": L, "k": k, "stated_log2": math.log2(s), "derived_log2": math.log2(d)})
    s, n, L, k, d = worst
    out["field_term_worst"] = {"n": n, "L": L, "k": k, "stated_log2": math.log2(s), "derived_log2": math.log2(d)}
    out["field_term_rows"] = rows
    record("eps.field_term_below_2^-215_for_k_le_n", math.log2(s) < -215,
           worst_log2=round(math.log2(s), 3), at={"n": n, "L": L, "k": k},
           derived_tighter_log2=round(math.log2(d), 3))
    # the code does not bound k (statement_transcript accepts any number of boundaries,
    # repeated positions allowed): smallest k with stated eps_field >= 2^-215 at L=2^32, n=2^31
    n, L = 2 ** 31, 2 ** 32
    target = Fraction(1, 2 ** 215)
    base = stated(n, L, 0)
    per_k = Fraction(1, R) + Fraction(1, R - n - L)
    k_star = math.ceil((target - base) / per_k)
    out["k_threshold_for_2^-215"] = k_star
    record("eps.k_threshold_where_2^-215_fails", True, k_star=k_star, log2_k_star=round(math.log2(k_star), 2),
           note="unstated in the docs; ~2^38.5 boundary constraints, far beyond memory for this BigUint code")
    # challenge bias: SHA-256 output mod r
    pre = (2 ** 256 - 1) // R + 1
    bias = pre * R / 2 ** 256
    out["challenge_max_preimages"] = pre
    out["challenge_bias_factor_vs_uniform"] = bias
    record("eps.sha256_mod_r_bias_factor", bias < 1.4, max_preimages=pre, factor=round(bias, 4),
           log2_factor=round(math.log2(bias), 3), note="multiplies each field term; immaterial to 2^-215")
    # sensitivity (recalled, not load-bearing): per-challenge L^2/r instead of L/r
    n, L = 2 ** 31, 2 ** 32
    sens = Fraction((5 + 31) * L * L, R)
    out["sensitivity_L2_over_r_log2"] = math.log2(float(sens))
    record("eps.sensitivity_if_proximity_term_were_L^2/r", True, log2=round(math.log2(float(sens)), 2),
           note="shows the 2^-215 figure depends on the L/r-per-challenge form")
    # hash cap
    out["sha256_collision_cap_bits"] = 128
    out["effective_conjectured_bits_default"] = min(240, 128)
    out["effective_conjectured_bits_fast"] = min(40, 128)
    RESULTS["soundness"] = out


# ── 6. v1 spot-check arithmetic (prior finding V3) ────────────────────
def v1_spot_check():
    out = {}
    out["escape_one_bad_row_n8_q20"] = (7 / 8) ** 20
    out["escape_two_bad_rows_n8_q20"] = (6 / 8) ** 20
    out["expected_grind_attempts_two_rows_q20"] = 1 / (6 / 8) ** 20
    per_query = -math.log2(1 - 1 / 8)
    out["spot_check_queries_n8_64bits"] = math.ceil(64 / per_query)
    out["q_over_n_at_q20_n8"] = 20 / 8
    RESULTS["v1"] = out
    record("v1.spot_check_queries_n8_64_is_333", out["spot_check_queries_n8_64bits"] == 333,
           q=out["spot_check_queries_n8_64bits"])
    record("v1.two_row_grind_q20_few_hundred_attempts", 100 < out["expected_grind_attempts_two_rows_q20"] < 1000,
           expected_attempts=round(out["expected_grind_attempts_two_rows_q20"], 1),
           escape=round(out["escape_two_bad_rows_n8_q20"], 5))
    record("v1.old_q_over_n_exceeds_one_new_text_is_a_probability", out["q_over_n_at_q20_n8"] > 1,
           q_over_n=out["q_over_n_at_q20_n8"], new_catch_prob=round(1 - out["escape_one_bad_row_n8_q20"], 4))


if __name__ == "__main__":
    field_facts()
    for n_, b_ in ((8, 4), (16, 8)):
        CTX[0] = f"n{n_}b{b_}."
        deep_algebra(n_, b_)
    for n_, b_ in ((8, 4), (8, 8), (16, 8)):
        CTX[0] = f"n{n_}b{b_}."
        degree_checks(n_, b_)
    CTX[0] = ""
    soundness()
    v1_spot_check()
    fails = [k for k, v in RESULTS["checks"].items() if not v["ok"]]
    RESULTS["summary"] = {"checks": len(RESULTS["checks"]), "failed": fails}
    with open(os.path.join(OUT_DIR, "stark_rederive.json"), "w") as fh:
        json.dump(RESULTS, fh, indent=1, default=str)
    print(f"summary: {len(RESULTS['checks'])} checks, failed: {fails}")

#!/usr/bin/env python3
"""Blind re-derivation for REVIEW-CZLIFT-BDAE69-20261022 (joint J3).

Written by the validator of TASK-20261022-2d255e from
experiments/EXP-CZLIFT-bdae69/specification.yaml, trial-plan.json,
ledger/hypotheses/H-CZLIFT-d37231.yaml and general mathematics only.
No file in review_plan.blind_rederivation.blind_from was opened.

Quantity (task card): for the primes in the specification, the expected
success count of the naive section from pairs with g^d < p plus the random
rate on the rest, computed from an own Fermat-quotient implementation.

Mathematics
-----------
naive section s(x) = integer representative of x in [1, p-1], read in Z_p.
L(x) = log_p(s(x)^(p-1)), precision 4 (mod p^4). Since s^(p-1) = 1 + p*u,
L(x) = p*u - (p*u)^2/2 + (p*u)^3/3 mod p^4 (terms n >= 4 vanish for p > 4),
so L(x)/p == u == q_p(s(x)) (mod p), the Fermat quotient
q_p(a) = (a^(p-1) - 1)/p mod p.
Smart-style ratio R(d) = L(g^d)/L(g) is defined iff q_p(g) != 0 mod p and then
R(d) == q_p(r_d)/q_p(g) (mod p) with r_d = g^d mod p in [1, p-1].
q_p is additive on integers (q_p(ab) == q_p(a)+q_p(b) mod p), so if g^d < p
(r_d = g^d as integers) then q_p(r_d) == d*q_p(g) and R(d) == d: certain success.
Otherwise write g^d = r_d + k*p; q_p(a + k*p) == q_p(a) - k/a (mod p) gives
R(d) == d - k/(r_d*q_p(g)) (mod p), so success iff k == 0 mod p, i.e. iff
g^d mod p^2 < p: a deterministic event of heuristic probability 1/p.
Hence E[successes] = #{pairs: g^d < p} + sum_{other pairs} 1/p.

Readings forced by under-specification (reported, not resolved by looking):
  * generator: the spec/hypothesis say "generator g" without the rule;
    reading A = smallest primitive root, reading B = uniform random primitive root.
  * prime sampling: "40 seeded primes in (50, 2000)"; the RNG procedure is not
    stated, so the per-seed prime list cannot be reproduced from the statement.
    The population expectation (uniform over primes in (50,2000)) is reported.
  * d: uniform on [2, p-3] (hypothesis assumption), 40 pairs per prime.
  * success: R(d) == d (mod p), against the 1/p reference (specification objective).
"""
from __future__ import annotations

import json
import math
import random
import sys


def primes_in(lo: int, hi: int) -> list[int]:
    sieve = bytearray([1]) * (hi + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(hi ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    return [n for n in range(lo + 1, hi) if sieve[n]]


def factor_primes(n: int) -> list[int]:
    out, f = [], 2
    while f * f <= n:
        if n % f == 0:
            out.append(f)
            while n % f == 0:
                n //= f
        f += 1
    if n > 1:
        out.append(n)
    return out


def is_primitive_root(g: int, p: int) -> bool:
    return all(pow(g, (p - 1) // q, p) != 1 for q in factor_primes(p - 1))


def smallest_primitive_root(p: int) -> int:
    g = 2
    while not is_primitive_root(g, p):
        g += 1
    return g


def fermat_quotient(a: int, p: int) -> int:
    """q_p(a) = (a^(p-1) - 1)/p mod p, for gcd(a, p) = 1."""
    t = pow(a, p - 1, p * p)
    assert (t - 1) % p == 0
    return ((t - 1) // p) % p


def padic_log_unit(a: int, p: int, prec: int = 4) -> int:
    """log_p(a) mod p^prec for a == 1 mod p, by the series (independent check)."""
    N = p ** prec
    x = (a - 1) % N
    assert x % p == 0
    total, xn = 0, x
    for n in range(1, 4 * prec + 2):
        # (x^n)/n with v_p(x^n) >= n; exact division by the p-part of n
        vn, nn = 0, n
        while nn % p == 0:
            nn //= p
            vn += 1
        num = pow(x, n, p ** (prec + vn))
        assert num % (p ** vn) == 0
        term = (num // (p ** vn)) * pow(nn, -1, N)
        total = (total + (term if n % 2 == 1 else -term)) % N
    return total


def naive_ratio_padic(p: int, g: int, d: int, prec: int = 4):
    """Smart-style ratio of the naive section via the p-adic log; None if undefined."""
    N = p ** prec
    lg = padic_log_unit(pow(g, p - 1, N), p, prec)
    r = pow(g, d, p)
    lr = padic_log_unit(pow(r, p - 1, N), p, prec)
    if lg % (p * p) == 0:
        return None
    # both divisible by p; divide by p and invert the unit part mod p^(prec-1)
    M = p ** (prec - 1)
    return ((lr // p) * pow((lg // p) % M, -1, M)) % M


def small_power(g: int, d: int, p: int) -> bool:
    """g^d < p as integers (g >= 2)."""
    return d * math.log(g) < math.log(p) - 1e-12 and g ** d < p


def naive_success_exact(p: int, g: int, d: int):
    """Exact naive success indicator from the Fermat quotient; None if ratio undefined."""
    qg = fermat_quotient(g, p)
    if qg == 0:
        return None
    r = pow(g, d, p)
    return fermat_quotient(r, p) == (d * qg) % p


def expected_count(tuples):
    """Blind quantity on explicit (p, g, d) tuples:
    sum over pairs of [g^d < p] + [g^d >= p]/p, plus diagnostics."""
    n_small = 0
    exp = 0.0
    null = 0.0
    var_null = 0.0
    exact = 0
    undefined = 0
    for p, g, d in tuples:
        null += 1.0 / p
        var_null += (1.0 / p) * (1 - 1.0 / p)
        if small_power(g, d, p):
            n_small += 1
            exp += 1.0
        else:
            exp += 1.0 / p
        s = naive_success_exact(p, g, d)
        if s is None:
            undefined += 1
        elif s:
            exact += 1
    return {
        "pairs": len(tuples),
        "pairs_g_pow_d_lt_p": n_small,
        "expected_success_count": exp,
        "null_expected_count_sum_inv_p": null,
        "null_sd": math.sqrt(var_null),
        "expected_z_under_model": (exp - null) / math.sqrt(var_null) if var_null else None,
        "exact_fermat_quotient_success_count": exact,
        "ratio_undefined_pairs": undefined,
    }


def per_prime_table(primes, gen_rule="smallest"):
    rows = []
    for p in primes:
        g = smallest_primitive_root(p)
        qg = fermat_quotient(g, p)
        n_d = p - 4  # d in [2, p-3]
        n_small = 0
        n_exact = 0
        gp2 = pow(g, 2, p * p)
        for d in range(2, p - 2):
            if small_power(g, d, p):
                n_small += 1
            if qg != 0 and gp2 < p:  # g^d mod p^2 < p  <=> success
                n_exact += 1
            gp2 = (gp2 * g) % (p * p)
        rows.append({
            "p": p,
            "g": g,
            "q_p_g": qg,
            "n_d": n_d,
            "n_g_pow_d_lt_p": n_small,
            "n_exact_success_all_d": n_exact,
            "rate_model": (n_small + (n_d - n_small) / p) / n_d,
            "rate_exact": n_exact / n_d,
            "inv_p": 1.0 / p,
        })
    return rows


def random_generator_small_count(p: int) -> float:
    """Reading B: expected #{d in [2,p-3]: g^d < p} for g uniform over primitive roots."""
    roots = [g for g in range(2, p) if is_primitive_root(g, p)]
    tot = 0
    for g in roots:
        d = 2
        while d <= p - 3 and g ** d < p:
            tot += 1
            d += 1
    return tot / len(roots)


def main(out_path: str):
    P = primes_in(50, 2000)
    # 1. cross-check Fermat-quotient criterion against the p-adic log ratio
    xcheck = {"primes": [], "pairs_checked": 0, "mismatches": 0}
    for p in [53, 97, 211, 1031, 1999]:
        g = smallest_primitive_root(p)
        for d in range(2, p - 2):
            R = naive_ratio_padic(p, g, d)
            s_padic = R is not None and R % p == d % p
            s_fq = naive_success_exact(p, g, d)
            s_mod = pow(g, d, p * p) < p
            xcheck["pairs_checked"] += 1
            if not (s_padic == bool(s_fq) == s_mod):
                xcheck["mismatches"] += 1
        xcheck["primes"].append([p, g])
    # 2. per-prime table, reading A
    rows = per_prime_table(P)
    nP = len(P)
    mean_model = sum(r["rate_model"] for r in rows) / nP
    mean_exact = sum(r["rate_exact"] for r in rows) / nP
    mean_inv = sum(r["inv_p"] for r in rows) / nP
    wieferich_g = [r["p"] for r in rows if r["q_p_g"] == 0]
    pairs = 40 * 40
    var_null = 40 * sum((1 / p) * (1 - 1 / p) for p in P) / nP * 40
    popA = {
        "primes_in_range": nP,
        "pairs_per_seed": pairs,
        "E_success_count_model": pairs * mean_model,
        "E_success_count_exact_fq": pairs * mean_exact,
        "E_null_count_sum_inv_p": pairs * mean_inv,
        "E_excess_over_null_model": pairs * (mean_model - mean_inv),
        "approx_null_sd": math.sqrt(var_null),
        "approx_expected_z_model": pairs * (mean_model - mean_inv) / math.sqrt(var_null),
        "primes_with_q_p_g_zero": wieferich_g,
    }
    # 3. Monte Carlo over the sampling (40 primes w/o replacement, 40 d's each)
    rng = random.Random(0xB1D)  # validator's own MC seed, unrelated to the producer seeds
    S_model, S_exact, Z_model, Z_exact = [], [], [], []
    by_p = {r["p"]: r for r in rows}
    for _ in range(2000):
        ps = rng.sample(P, 40)
        tuples = [(p, by_p[p]["g"], rng.randint(2, p - 3)) for p in ps for _ in range(40)]
        null = sum(1 / p for p, _, _ in tuples)
        sd = math.sqrt(sum((1 / p) * (1 - 1 / p) for p, _, _ in tuples))
        sm = sum(1.0 if small_power(g, d, p) else 1 / p for p, g, d in tuples)
        se = sum(1 for p, g, d in tuples if pow(g, d, p * p) < p)
        S_model.append(sm)
        S_exact.append(se)
        Z_model.append((sm - null) / sd)
        Z_exact.append((se - null) / sd)

    def q(xs, a):
        ys = sorted(xs)
        return ys[min(len(ys) - 1, int(a * len(ys)))]

    mc = {
        "draws": 2000,
        "mc_seed": "0xB1D",
        "S_model_mean": sum(S_model) / len(S_model),
        "S_model_q05_q50_q95": [q(S_model, .05), q(S_model, .5), q(S_model, .95)],
        "S_exact_mean": sum(S_exact) / len(S_exact),
        "S_exact_q05_q50_q95": [q(S_exact, .05), q(S_exact, .5), q(S_exact, .95)],
        "z_model_mean": sum(Z_model) / len(Z_model),
        "z_model_q05_q50_q95": [q(Z_model, .05), q(Z_model, .5), q(Z_model, .95)],
        "z_exact_q05_q50_q95": [q(Z_exact, .05), q(Z_exact, .5), q(Z_exact, .95)],
        "P_z_exact_gt_4": sum(1 for z in Z_exact if z > 4) / len(Z_exact),
    }
    # 4. reading B: random primitive root
    small_B = [random_generator_small_count(p) for p in P]
    mean_rate_B = sum((nb + (p - 4 - nb) / p) / (p - 4) for nb, p in zip(small_B, P)) / nP
    popB = {
        "E_success_count_model": pairs * mean_rate_B,
        "E_null_count_sum_inv_p": pairs * mean_inv,
        "approx_expected_z_model": pairs * (mean_rate_B - mean_inv) / math.sqrt(var_null),
    }
    out = {
        "quantity": "expected naive-section success count = #{g^d<p} + sum_{rest} 1/p",
        "derivation": "see module docstring; success iff g^d mod p^2 < p (Fermat quotient)",
        "crosscheck_fq_vs_padic_log_prec4": xcheck,
        "readingA_smallest_primitive_root_population": popA,
        "readingA_monte_carlo": mc,
        "readingB_random_primitive_root_population": popB,
        "per_prime_table_readingA": rows,
        "underspecified": [
            "generator rule not stated (reading A vs B differ by ~an order of magnitude in excess)",
            "seeded prime-sampling procedure not stated; per-seed prime list not derivable from the statement",
            "pair sampling procedure (with/without replacement of d) not stated; d uniform on [2,p-3] assumed",
            "z-score formula not stated beyond 'within 4 standard errors of the mean of 1/p'",
        ],
    }
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    summ = {k: out[k] for k in out if k != "per_prime_table_readingA"}
    print(json.dumps(summ, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1])

#!/usr/bin/env python3
"""Blind re-derivation (joint J3) for EXP-CZLIFT-7c8d73, validator task TASK-20261022-d7d57f.

Written from the specification, the trial plan, the hypothesis record and general
mathematics only (Silverman, AEC ch. IV).  No producer code or raw result was read.

Quantity (review_plan.blind_rederivation): the first k+1 coefficients of the formal
logarithm of y^2 = x^3 + B in z = -x/y, obtained from the invariant differential,
at one anomalous prime and the specification's precision (k = 6).

Method
  1. w(z) = -1/y as a power series in z = -x/y from the fixed point
       w = z^3 + a1 z w + a2 z^2 w + a3 w^2 + a4 z w^2 + a6 w^3
     (here a1 = a2 = a3 = 0, a4 = A, a6 = B; A = 0 is the statement's family,
     A != 0 is computed only as context).
  2. x = z/w, y = -1/w, omega = dx / (2y + a1 x + a3) = (z w' - w) / (2 w) dz.
  3. log_F(z) = integral of omega; exp_F = series reversion of log_F.
  4. Coefficients are exact polynomials in (A, B) over Q.
  5. Independent checks:
       (a) automorphism check: for A = 0, [zeta_6] acts by z -> zeta_6 z, so only
           z^n with n = 1 mod 6 may appear in log_F;
       (b) numeric additivity: for points of E1(Q_p) built from z in pZ, the chord
           law in the (z, w) plane gives z(P1+P2); check
           v_p(log z1 + log z2 - log z3) is at least the truncation precision;
           a deliberately wrong log is run through the same check as a negative control;
       (c) exp_F(log_F(z)) = z as series.
  6. Anomalous primes for y^2 = x^3 + B (trace 1) with p <= 1500 by direct point
     count over the six sextic twists; coefficients reduced mod p^6.

Two readings of "first k+1 coefficients" are sealed:
  reading_a: coefficients of z^0 .. z^k of log_F (k+1 numbers; the series truncated
             at degree k, the reading consistent with the hypothesis assumption
             'precision k = 6 < p so every series coefficient has unit denominators').
  reading_b: coefficients of z^1 .. z^(k+1) (the first k+1 nonzero-index terms).
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction

K = 6            # specification: inputs.precision = 6 ; hypothesis: precision k = 6 < p
NTERMS = 26      # series computed mod z^NTERMS for context and checks
PMAX = 1500      # specification: anomalous_cm_curves(1500)

# ---------------------------------------------------------------------------
# polynomials in (A, B) over Q: dict {(i, j): Fraction}  meaning sum c A^i B^j
# ---------------------------------------------------------------------------

def padd(p, q):
    r = dict(p)
    for k, v in q.items():
        r[k] = r.get(k, 0) + v
        if r[k] == 0:
            del r[k]
    return r


def pmul(p, q):
    r = {}
    for (i1, j1), v1 in p.items():
        for (i2, j2), v2 in q.items():
            k = (i1 + i2, j1 + j2)
            r[k] = r.get(k, 0) + v1 * v2
            if r[k] == 0:
                del r[k]
    return r


def pscale(p, c):
    if c == 0:
        return {}
    return {k: v * c for k, v in p.items()}


ONE = {(0, 0): Fraction(1)}
APOL = {(1, 0): Fraction(1)}
BPOL = {(0, 1): Fraction(1)}

# power series: list of polynomials, index = power of z, truncated at NTERMS

def szero():
    return [dict() for _ in range(NTERMS)]


def sadd(s, t):
    return [padd(a, b) for a, b in zip(s, t)]


def smul(s, t):
    r = szero()
    for i, a in enumerate(s):
        if not a:
            continue
        for j in range(NTERMS - i):
            b = t[j]
            if b:
                r[i + j] = padd(r[i + j], pmul(a, b))
    return r


def sscale(s, c):
    return [pscale(a, c) for a in s]


def spolmul(s, poly):
    return [pmul(a, poly) if a else {} for a in s]


def sshift(s, n):
    """multiply by z^n"""
    r = szero()
    for i in range(NTERMS - n):
        r[i + n] = dict(s[i])
    return r


def sinv(s):
    """inverse of a series with constant term exactly 1 (as a polynomial)."""
    assert s[0] == ONE, s[0]
    r = szero()
    r[0] = dict(ONE)
    for n in range(1, NTERMS):
        acc = {}
        for i in range(1, n + 1):
            if s[i] and r[n - i]:
                acc = padd(acc, pmul(s[i], r[n - i]))
        r[n] = pscale(acc, -1)
    return r


def sderiv(s):
    r = szero()
    for i in range(1, NTERMS):
        r[i - 1] = pscale(s[i], i)
    return r


def formal_w():
    """w(z) mod z^NTERMS for y^2 = x^3 + A x + B (a1=a2=a3=0)."""
    z3 = szero()
    z3[3] = dict(ONE)
    w = z3
    for _ in range(NTERMS):
        w2 = smul(w, w)
        w3 = smul(w2, w)
        new = sadd(z3, sadd(spolmul(sshift(w2, 1), APOL), spolmul(w3, BPOL)))
        if new == w:
            break
        w = new
    return w


def invariant_differential(w):
    """omega/dz = (z w' - w) / (2 w).  w = z^3 u, u(0)=1."""
    # u = w / z^3
    u = szero()
    for i in range(3, NTERMS):
        u[i - 3] = dict(w[i])
    # (z w' - w) = z^3 (3u + z u' - u) = z^3 (2u + z u')
    num = sadd(sscale(u, 2), sshift(sderiv(u), 1))
    om = sscale(smul(num, sinv(u)), Fraction(1, 2))
    return om


def integrate(om):
    lg = szero()
    for i in range(NTERMS - 1):
        lg[i + 1] = pscale(om[i], Fraction(1, i + 1))
    return lg


def compose(f, g):
    """f(g(z)), g(0)=0."""
    r = szero()
    gp = szero()
    gp[0] = dict(ONE)
    for i in range(NTERMS):
        if i > 0:
            gp = smul(gp, g)
        if f[i]:
            r = sadd(r, [pmul(f[i], c) if c else {} for c in gp])
    return r


def reversion(f):
    """series inverse g with f(g(z)) = z, f = z + ...; Newton-free iterative."""
    g = szero()
    g[1] = dict(ONE)
    for n in range(2, NTERMS):
        comp = compose(f, g)
        # coefficient of z^n in f(g) must be 0; g_n enters linearly with coeff 1
        g[n] = padd(g[n], pscale(comp[n], -1))
    return g


def pstr(p):
    if not p:
        return "0"
    parts = []
    for (i, j), v in sorted(p.items()):
        mon = ("" if i == 0 else ("A" if i == 1 else f"A^{i}")) + (
            "" if j == 0 else ("B" if j == 1 else f"B^{j}"))
        coef = str(v)
        parts.append(f"{coef}*{mon}" if mon else coef)
    return " + ".join(parts)


def peval(p, A, B):
    return sum((v * Fraction(A) ** i * Fraction(B) ** j for (i, j), v in p.items()), Fraction(0))


# ---------------------------------------------------------------------------
# p-adic helpers
# ---------------------------------------------------------------------------

def vp(x, p):
    x = Fraction(x)
    if x == 0:
        return float("inf")
    n, d, v = x.numerator, x.denominator, 0
    while n % p == 0:
        n //= p
        v += 1
    while d % p == 0:
        d //= p
        v -= 1
    return v


def modpk(x, p, k):
    """x in Z_(p) -> integer in [0, p^k)."""
    x = Fraction(x)
    m = p ** k
    if x.denominator % p == 0:
        return None  # not p-integral
    return (x.numerator * pow(x.denominator, -1, m)) % m


def anomalous_j0(pmax):
    """all (p, B) with p <= pmax, B a sextic-twist representative in [1, p), #E(F_p) = p
    for E: y^2 = x^3 + B.  Uses direct Legendre-symbol point counts."""
    out = []
    for p in range(5, pmax + 1):
        if any(p % q == 0 for q in range(2, int(p ** 0.5) + 1)):
            continue
        # trace t = 1 forces 4p = 1 + 3 v^2 (CM by Z[zeta_3]); brute force below
        # confirms this filter for p <= 200
        r = (4 * p - 1)
        if r % 3 or int(round((r // 3) ** 0.5)) ** 2 != r // 3:
            continue
        sq = [0] * p
        for t in range(p):
            sq[t * t % p] += 1
        cubes = [x * x % p * x % p for x in range(p)]
        for B in range(1, p):
            n = 1 + sum(sq[(c + B) % p] for c in cubes)
            if n == p:
                out.append((p, B))
                break  # smallest B in [1,p) with trace 1
    return out


def brute_anomalous_j0(pmax):
    """every prime 5 <= p <= pmax and every B in [1,p): list primes with some trace-1 B."""
    found = []
    for p in range(5, pmax + 1):
        if any(p % q == 0 for q in range(2, int(p ** 0.5) + 1)):
            continue
        sq = [0] * p
        for t in range(p):
            sq[t * t % p] += 1
        cubes = [x * x % p * x % p for x in range(p)]
        if any(1 + sum(sq[(c + B) % p] for c in cubes) == p for B in range(1, p)):
            found.append(p)
    return found


# ---------------------------------------------------------------------------
# numeric additivity check in E1(Q_p) via the chord law in (z, w)
# ---------------------------------------------------------------------------

def eval_series_num(s, A, B, z):
    return sum((peval(c, A, B) * Fraction(z) ** i for i, c in enumerate(s) if c), Fraction(0))


def chord_sum_z(A, B, w_ser, z1, z2):
    w1 = eval_series_num(w_ser, A, B, z1)
    w2 = eval_series_num(w_ser, A, B, z2)
    lam = (w2 - w1) / (Fraction(z2) - Fraction(z1))
    nu = w1 - lam * z1
    # substitute w = lam z + nu into z^3 + A z w^2 + B w^3 - w = 0
    c3 = 1 + A * lam ** 2 + B * lam ** 3
    c2 = 2 * A * lam * nu + 3 * B * lam ** 2 * nu
    z3 = -Fraction(z1) - Fraction(z2) - c2 / c3   # third intersection
    return -z3                                     # z(P1+P2) = z(-P3) = -z3 (a1=a3=0)


def main():
    w = formal_w()
    om = invariant_differential(w)
    lg = integrate(om)
    ex = reversion(lg)

    # (c) exp(log(z)) = z
    el = compose(ex, lg)
    exp_log_ok = all((el[i] == (ONE if i == 1 else {})) for i in range(NTERMS))

    # restrict to A = 0 (the statement's family y^2 = x^3 + B)
    def at_A0(p):
        return {k: v for k, v in p.items() if k[0] == 0}

    lg0 = [at_A0(c) for c in lg]
    om0 = [at_A0(c) for c in om]
    ex0 = [at_A0(c) for c in ex]
    w0 = [at_A0(c) for c in w]

    # (a) automorphism check
    sym_ok = all((not c) or (n % 6 == 1) for n, c in enumerate(lg0))
    sym_ok_general = all((not c) or (n % 2 == 1) for n, c in enumerate(lg))
    weight_ok = all(all(4 * i + 6 * j == n - 1 for (i, j) in c) for n, c in enumerate(lg) if c)

    res = {
        "experiment_id": "EXP-CZLIFT-7c8d73",
        "task_id": "TASK-20261022-d7d57f",
        "phase": "blind (J3), sealed before any blind_from path was opened",
        "k_precision": K,
        "series_truncation_internal": NTERMS,
        "curve_family": "y^2 = x^3 + B  (a1=a2=a3=a4=0, a6=B); context: y^2 = x^3 + A x + B",
        "w_series_A0": {str(n): pstr(c) for n, c in enumerate(w0) if c},
        "omega_over_dz_A0": {str(n): pstr(c) for n, c in enumerate(om0) if c},
        "log_F_A0": {str(n): pstr(c) for n, c in enumerate(lg0) if c},
        "exp_F_A0": {str(n): pstr(c) for n, c in enumerate(ex0) if c},
        "log_F_general_AB": {str(n): pstr(c) for n, c in enumerate(lg) if c and n <= 13},
        "exp_F_general_AB": {str(n): pstr(c) for n, c in enumerate(ex) if c and n <= 13},
        "checks": {
            "exp_F(log_F(z)) == z mod z^%d" % NTERMS: exp_log_ok,
            "A=0: only z^n with n = 1 mod 6 in log_F (Aut = mu_6)": sym_ok,
            "general A,B: only odd n in log_F ([-1] acts by z -> -z)": sym_ok_general,
            "weight: coefficient of z^n has weight n-1 (wt A=4, wt B=6)": weight_ok,
        },
    }

    readings = {
        "reading_a_z0_to_zk": [pstr(lg0[n]) for n in range(0, K + 1)],
        "reading_b_z1_to_zk+1": [pstr(lg0[n]) for n in range(1, K + 2)],
        "omega_first_k+1_z0_to_zk": [pstr(om0[n]) for n in range(0, K + 1)],
    }
    res["blind_quantity_symbolic"] = readings

    # anomalous primes for the j = 0 family
    anom = anomalous_j0(PMAX)
    res["anomalous_j0_primes_le_1500"] = [{"p": p, "B_smallest": B} for p, B in anom]
    brute = brute_anomalous_j0(200)
    res["brute_force_filter_check_p_le_200"] = {
        "brute": brute, "filtered": [p for p, _ in anom if p <= 200],
        "agree": brute == [p for p, _ in anom if p <= 200]}
    res["note_D_minus_4"] = ("y^2 = x^3 + A x has even trace for p = 1 mod 4 and is supersingular for p = 3 mod 4, "
                             "so no D=-4 curve is anomalous; not used here.")

    designated = []
    for p, B in anom:
        if p <= K:
            continue
        ra = [modpk(peval(lg0[n], 0, B), p, K) for n in range(0, K + 1)]
        rb = [modpk(peval(lg0[n], 0, B), p, K) for n in range(1, K + 2)]
        designated.append({"p": p, "B": B, "mod_p^6_reading_a": ra, "mod_p^6_reading_b": rb,
                           "v_p_coeff_z^7": vp(peval(lg0[7], 0, B), p)})
    res["mod_p6_tables"] = designated
    res["designated_prime"] = designated[0] if designated else None

    # (b) numeric additivity check at the designated prime and at a second prime
    add_checks = []
    for p, B in [(d["p"], d["B"]) for d in designated[:3]]:
        for (a1, a2) in [(1, 2), (3, 5)]:
            z1, z2 = p * a1, p * a2
            zs = chord_sum_z(0, B, w0, z1, z2)
            L = lambda z, ser: eval_series_num(ser, 0, B, z)
            defect = L(z1, lg0) + L(z2, lg0) - L(zs, lg0)
            # negative control: a wrong 'log' z + z^3/3 (the log of the multiplicative-ish
            # shape) must fail additivity at low valuation
            wrong = szero()
            wrong[1] = dict(ONE)
            wrong[3] = {(0, 0): Fraction(1, 3)}
            dwrong = L(z1, wrong) + L(z2, wrong) - L(zs, wrong)
            # truncated-at-k log (= z for A=0): additivity holds mod p^(k+1)?
            trunc = szero()
            for n in range(K + 1):
                trunc[n] = dict(lg0[n])
            dtr = L(z1, trunc) + L(z2, trunc) - L(zs, trunc)
            add_checks.append({"p": p, "B": B, "z1": z1, "z2": z2,
                               "v_p(z(P1+P2) - z1 - z2)": vp(zs - z1 - z2, p),
                               "v_p(additivity defect, full log mod z^%d)" % NTERMS: vp(defect, p),
                               "v_p(defect, truncated log deg<=k)": vp(dtr, p),
                               "v_p(defect, WRONG log z+z^3/3) [negative control]": vp(dwrong, p)})
    res["numeric_additivity_checks"] = add_checks

    json.dump(res, sys.stdout, indent=1, default=str)
    print()


if __name__ == "__main__":
    main()

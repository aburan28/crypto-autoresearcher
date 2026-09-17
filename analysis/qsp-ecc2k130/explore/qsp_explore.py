#!/usr/bin/env python3
"""Pre-compute audits for the four RQ-QSP-f9bbdb proposals (section 8 of
docs/inventor-protocol.md).  Pure GF(2)[X] arithmetic on bit-packed Python
integers; no curve is touched, no experiment is run, nothing here is evidence.

Audits implemented (proposal -> stage):
  IDEA-20260916-3f7a1c  Stage 0 hand check (n=4, n'=3), Stage 1 exhaustive toy
                        fixtures (brute count == injection count, bound holds),
                        Stage 2 census at n=131, n' in {33,44,66} for every
                        lambda in F_2[X] of degree 3..7, Stage 3 brute cross-check
                        at n=131, n' in {11,12}, Stage 4 proves-too-much fixtures.
  IDEA-20260916-5c9d6e  general-coefficient (twisted) bound checked on random
                        lambda in F_{2^n}[X] at n=11 and 13; complete-splitting
                        sweep at prime n <= 31, n' <= 15, d <= 8 against
                        beta >= n/(n + n' - r); the n=131 bound table.
  IDEA-20260916-a17f43  toy census of the conjugate-degree-2 shape
                        L_R = X^{2^{a+1}} + c(X) X^{2^a} + e(X) at prime n in
                        {23, 29, 31}, admissible a (r <= q), deg c, deg e <= d0,
                        with the Type 2 fixtures at n=7 and n=31.
  IDEA-20260916-b84e2d  engine availability only (no chain system is solved).

Polynomials over F_2 are Python ints (bit i = coefficient of X^i).
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
import time

# ----------------------------------------------------------------------------
# F_2[X] on bit-packed ints
# ----------------------------------------------------------------------------
def deg(a: int) -> int:
    return a.bit_length() - 1


def clmul(a: int, b: int) -> int:
    """Carry-less product.  Loops over the set bits of the sparser operand."""
    if a.bit_count() > b.bit_count():
        a, b = b, a
    r = 0
    while a:
        low = a & -a
        r ^= b << (low.bit_length() - 1)
        a ^= low
    return r


_SPREAD_MASKS: dict[int, list[tuple[int, int]]] = {}


def square(a: int) -> int:
    """a(X)^2 = a(X^2) over F_2: spread the bits with zeros in between."""
    if a == 0:
        return 0
    nbits = a.bit_length()
    w = 1
    while w < nbits:
        w <<= 1
    key = w
    if key not in _SPREAD_MASKS:
        masks = []
        s = w
        while s >= 1:
            # mask selecting the low s bits of every 2s-bit block, over 2w bits
            block = (1 << s) - 1
            m = 0
            for i in range(0, 2 * w, 2 * s):
                m |= block << i
            masks.append((s, m))
            s >>= 1
        _SPREAD_MASKS[key] = masks
    x = a
    for s, m in _SPREAD_MASKS[key]:
        if s == w:
            continue
        x = (x | (x << s)) & m
    return x


def polymod(a: int, m: int) -> int:
    dm = deg(m)
    while a and deg(a) >= dm:
        a ^= m << (deg(a) - dm)
    return a


def polymod_sparse_tail(a: int, np2: int, lam: int) -> int:
    """Reduce a modulo L = X^{np2} + lam(X) with deg lam < np2, using the
    substitution X^{np2} -> lam(X) on the high part (fast when lam is sparse
    relative to np2)."""
    assert deg(lam) < np2, "tail degree must be below the leading exponent"
    mask = (1 << np2) - 1
    while a >> np2:
        high = a >> np2
        a = (a & mask) ^ clmul(high, lam)
    return a


def gcd(a: int, b: int) -> int:
    while b:
        a = polymod(a, b)
        a, b = b, a
    return a


def polydivmod(a: int, m: int) -> tuple[int, int]:
    q = 0
    dm = deg(m)
    while a and deg(a) >= dm:
        s = deg(a) - dm
        q |= 1 << s
        a ^= m << s
    return q, a


def compose(f: int, g: int) -> int:
    """f(g(X)) over F_2 by Horner."""
    r = 0
    for i in range(deg(f), -1, -1):
        r = clmul(r, g)
        if (f >> i) & 1:
            r ^= 1
    return r


def iterate(lam: int, k: int) -> int:
    r = 0b10  # X
    for _ in range(k):
        r = compose(lam, r)
    return r


def frob_power_mod(k: int, m: int) -> int:
    """X^(2^k) mod m, dense reduction."""
    x = 0b10
    for _ in range(k):
        x = polymod(square(x), m)
    return x


def frob_power_mod_sparse(k: int, np2: int, lam: int) -> int:
    """X^(2^k) mod (X^{np2} + lam) with the sparse reduction."""
    x = 0b10
    for _ in range(k):
        x = polymod_sparse_tail(square(x), np2, lam)
    return x


def root_count_gcd(np_: int, lam: int, n: int) -> int:
    """deg gcd(X^{2^n} - X, X^{2^n'} + lam), i.e. the number of distinct roots
    of L in F_{2^n} (distinct roots are what the gcd counts, X^{2^n} - X being
    squarefree).  `np_` is n' itself; the leading exponent is 2^n'."""
    np2 = 1 << np_
    L = (1 << np2) ^ lam
    h = frob_power_mod_sparse(n, np2, lam) ^ 0b10
    return deg(gcd(L, h)) if h else np2


import os
import subprocess

_GF2RC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gf2rc")


def root_count_batch(n: int, items: list[tuple[int, int]]) -> list[int]:
    """Batch root counts through the C helper gf2rc (same quantity as
    root_count_gcd; word-level arithmetic).  items = [(n', lam), ...]."""
    if not items:
        return []
    inp = "".join(f"{n} {np_} {lam:x}\n" for np_, lam in items)
    out = subprocess.run([_GF2RC], input=inp, capture_output=True, text=True, check=True).stdout.split("\n")
    res = []
    for line in out:
        if line.strip():
            res.append(int(line.split()[-1]))
    assert len(res) == len(items), (len(res), len(items))
    return res


def is_irreducible(f: int) -> bool:
    n = deg(f)
    x = 0b10
    xp = x
    for k in range(1, n // 2 + 1):
        xp = polymod(square(xp), f)
        if gcd(f, xp ^ x) != 1:
            return False
    return True


# ----------------------------------------------------------------------------
# F_{2^n} for small n (elements as ints mod an irreducible), for brute force
# ----------------------------------------------------------------------------
IRRED = {4: 0b10011, 7: 0b10000011, 11: 0b100000000101, 12: 0b1000001010011,
         13: 0b10000000011011, 23: (1 << 23) | (1 << 5) | 1}


def fmul(a: int, b: int, mod: int) -> int:
    return polymod(clmul(a, b), mod)


def fpow2k(a: int, k: int, mod: int) -> int:
    for _ in range(k):
        a = polymod(square(a), mod)
    return a


def feval_f2poly(lam: int, x: int, mod: int) -> int:
    """lambda(x) for lambda in F_2[X], x in F_{2^n}."""
    r = 0
    for i in range(deg(lam), -1, -1):
        r = fmul(r, x, mod)
        if (lam >> i) & 1:
            r ^= 1
    return r


def feval_kpoly(coeffs: list[int], x: int, mod: int) -> int:
    """lambda(x) for lambda with coefficients in F_{2^n} (coeffs[i] of X^i)."""
    r = 0
    for c in reversed(coeffs):
        r = fmul(r, x, mod) ^ c
    return r


def brute_count_f2(lam: int, np_: int, n: int) -> int:
    mod = IRRED[n]
    cnt = 0
    for x in range(1 << n):
        if fpow2k(x, np_, mod) == feval_f2poly(lam, x, mod):
            cnt += 1
    return cnt


def brute_count_k(coeffs: list[int], np_: int, n: int) -> int:
    mod = IRRED[n]
    cnt = 0
    for x in range(1 << n):
        if fpow2k(x, np_, mod) == feval_kpoly(coeffs, x, mod):
            cnt += 1
    return cnt


# ----------------------------------------------------------------------------
# The injection count (IDEA-20260916-3f7a1c / 5c9d6e), F_2 coefficients
# ----------------------------------------------------------------------------
def injection_count_f2(lam: int, np_: int, n: int) -> dict:
    """Exact N_K(L) for lambda in F_2[X], L = X^{2^n'} + lambda, through
    H(Y) = Y^{2^{n'-r}} + lambda^{o(q+1)}(Y): roots y of H in F_{2^n} are found
    as gcd(H, Y^{2^n} - Y); each root orbit is tested in the field F_2[Y]/(g)
    for the closing conditions x = lambda^{oq}(y) satisfies x^{2^r} = y and
    L(x) = 0."""
    q, r = divmod(n, np_)
    Lq = iterate(lam, q)
    H = (1 << (1 << (np_ - r))) ^ compose(lam, Lq)     # Y^{2^{n'-r}} + lambda(Lambda_q(Y))
    if H == 0:
        return {"error": "H identically zero (degenerate)"}
    hY = frob_power_mod(n, H) ^ 0b10
    g = gcd(H, hY) if hY else H
    roots_total = deg(g)
    # split g into F_2-roots and degree-n irreducible factors (n prime assumed
    # for the orbit structure; for composite n we fall back to a full check)
    count = 0
    slack = 0
    orbits_pass = 0
    # F_2 roots: evaluate g at 0 and 1 directly
    g_at_0 = g & 1
    g_at_1 = bin(g).count("1") & 1
    lin_roots = []
    if g_at_0 == 0:
        lin_roots.append(0)
    if g_at_1 == 0:
        lin_roots.append(1)
    for y in lin_roots:
        # x = Lambda_q(y) in F_2
        x = bin(Lq).count("1") & 1 if y == 1 else Lq & 1
        lx = (bin(lam).count("1") & 1) if x == 1 else (lam & 1)
        # L(x) = x^{2^n'} + lam(x) = x + lam(x) in F_2
        if (x ^ lx) == 0 and x == y:  # x^{2^r} = x for x in F_2
            count += 1
        else:
            slack += 1
    # remaining part: divide out the linear factors
    rest = g
    for y in lin_roots:
        rest, rem = polydivmod(rest, 0b10 ^ (0b1 if y == 1 else 0))
        assert rem == 0
    # equal-degree factorisation of rest into degree-n factors (n prime)
    factors = []
    stack = [rest] if deg(rest) > 0 else []
    rng = random.Random(1)
    while stack:
        f = stack.pop()
        if deg(f) == n:
            factors.append(f)
            continue
        if deg(f) % n != 0:
            return {"error": f"unexpected factor degree {deg(f)} (n={n})", "roots_of_H_in_K": roots_total}
        # Cantor-Zassenhaus with the absolute trace over F_2
        while True:
            h = rng.getrandbits(deg(f)) | 1
            t = h
            acc = h
            for _ in range(n - 1):
                t = polymod(square(t), f)
                acc ^= t
            d = gcd(f, acc)
            if 0 < deg(d) < deg(f):
                stack.append(d)
                stack.append(polydivmod(f, d)[0])
                break
    for gf in factors:
        # field F_2[Y]/(gf); y = Y
        y = 0b10
        x = polymod(Lq, gf) if deg(Lq) >= deg(gf) else Lq
        # test x^{2^r} == y
        xr = x
        for _ in range(r):
            xr = polymod(square(xr), gf)
        # test L(x) = x^{2^n'} + lam(x) == 0
        xn = x
        for _ in range(np_):
            xn = polymod(square(xn), gf)
        lx = polymod(compose(lam, x), gf)
        if xr == y and (xn ^ lx) == 0:
            orbits_pass += 1
            count += n
        else:
            slack += n
    return {"N": count, "roots_of_H_in_K": roots_total, "slack": slack, "orbits": orbits_pass,
            "deg_H": deg(H), "bound": max(1 << (np_ - r), (deg(lam)) ** (q + 1))}


def is_linearized(lam: int) -> bool:
    i = 0
    l = lam
    while l:
        if l & 1 and (i & (i - 1)) != 0:
            return False
        l >>= 1
        i += 1
    return True


def polys_of_degree(d: int):
    for low in range(1 << d):
        yield (1 << d) | low


def poly_str(p: int) -> str:
    terms = [("X^%d" % i if i > 1 else ("X" if i == 1 else "1")) for i in range(deg(p), -1, -1) if (p >> i) & 1]
    return " + ".join(terms)


# ----------------------------------------------------------------------------
# audits
# ----------------------------------------------------------------------------
def audit_stage0_hand(out: dict) -> None:
    """n = 4, n' = 3 (q = 1, r = 1): list all 16 elements."""
    res = {}
    for lam in (0b111, 0b1001):   # X^2+X+1, X^3+1
        brute = brute_count_f2(lam, 3, 4)
        inj = injection_count_f2(lam, 3, 4)
        res[poly_str(lam)] = {"brute": brute, "injection": inj}
    out["stage0_n4_np3"] = res


def audit_stage1_toy(out: dict) -> None:
    cells = [(11, 6), (13, 7), (7, 3), (11, 4), (13, 5)]
    res = {}
    for n, np_ in cells:
        q, r = divmod(n, np_)
        rows = []
        worst = 0.0
        attained = []
        mism = 0
        for d in range(2, 8):
            for lam in polys_of_degree(d):
                # "brute" = direct deg gcd(X^{2^n} - X, L) at degree 2^n' (the
                # proposal's brute method); at (11, 6) every fifth candidate is
                # additionally checked by enumerating all 2^11 field elements.
                brute = root_count_gcd(np_, lam, n)
                if n == 11 and np_ == 6 and lam % 5 == 0:
                    enum = brute_count_f2(lam, np_, n)
                    if enum != brute:
                        rows.append({"lambda": poly_str(lam), "enum": enum, "gcd": brute, "kind": "enum_vs_gcd"})
                        mism += 1
                inj = injection_count_f2(lam, np_, n)
                if "error" in inj:
                    continue
                if inj["N"] != brute:
                    mism += 1
                    rows.append({"lambda": poly_str(lam), "brute": brute, "injection": inj})
                bound = max(1 << (np_ - r), d ** (q + 1))
                ratio = brute / bound
                worst = max(worst, ratio)
                if brute == bound:
                    attained.append((poly_str(lam), brute))
        res[f"n{n}_np{np_}"] = {"q": q, "r": r, "candidates": sum(1 << d for d in range(2, 8)),
                                "mismatches": mism, "mismatch_rows": rows[:5],
                                "max_N_over_bound": worst, "bound_attained_by": attained[:10]}
    out["stage1_toy_fixtures"] = res


def audit_k_coefficients(out: dict) -> None:
    """IDEA-20260916-5c9d6e: random lambda in F_{2^n}[X], n = 11, 13, n' = 6, 7."""
    res = {}
    rng = random.Random(20260917)
    for n, np_, d, trials in ((11, 6, 3, 60), (11, 6, 5, 40), (11, 4, 3, 40)):
        q, r = divmod(n, np_)
        bound = max(1 << (np_ - r), d ** (q + 1))
        maxN = 0
        hist = {}
        for _ in range(trials):
            coeffs = [rng.getrandbits(n) for _ in range(d + 1)]
            if coeffs[-1] == 0:
                coeffs[-1] = 1
            N = brute_count_k(coeffs, np_, n)
            maxN = max(maxN, N)
            hist[N] = hist.get(N, 0) + 1
        res[f"n{n}_np{np_}_d{d}"] = {"q": q, "r": r, "bound": bound, "trials": trials, "max_N": maxN,
                                     "bound_holds": maxN <= bound, "histogram": dict(sorted(hist.items()))}
    out["k_coefficient_fixture"] = res


def audit_proves_too_much(out: dict) -> None:
    res = {}
    # Type 2 at n = 7: lambda = X^2 + X, n' = 3 -> 8 roots
    res["type2_n7"] = {"expected": 8, "gcd_count": root_count_gcd(3, 0b110, 7),
                       "injection": injection_count_f2(0b110, 3, 7)}
    # Type 2 at n = 31: L = X^{2^15} + X^{2^7} + X^{2^3} + X^2 + X -> 2^15 roots
    lam31 = (1 << 128) | (1 << 8) | (1 << 2) | (1 << 1)
    res["type2_n31"] = {"expected": 1 << 15, "gcd_count_c": root_count_batch(31, [(15, lam31)])[0]}
    # subfield: n = 12, n' = 6, lambda = X -> 64 roots
    res["subfield_n12"] = {"expected": 64, "gcd_count": root_count_gcd(6, 0b10, 12)}
    # linearized trinomial Theorem 1 equality: X^{p^2} + X^p + X over F_{p^3}, p = 2: n=3, n'=2 -> 4 roots
    res["theorem1_equality_n3"] = {"expected": 4, "gcd_count": root_count_gcd(2, 0b110, 3)}
    out["proves_too_much"] = res


def audit_census_131(out: dict, np_list=(33, 44, 66), dmax=7) -> None:
    res = {}
    for np_ in np_list:
        q, r = divmod(131, np_)
        rows = []
        hist = {}
        t0 = time.time()
        cand = 0
        maxN = 0
        for d in range(3, dmax + 1):
            for lam in polys_of_degree(d):
                if is_linearized(lam):
                    continue
                cand += 1
                inj = injection_count_f2(lam, np_, 131)
                N = inj.get("N", -1)
                hist[N] = hist.get(N, 0) + 1
                maxN = max(maxN, N)
                if N > 2 or "error" in inj:
                    rows.append({"lambda": poly_str(lam), **inj})
        res[f"np{np_}"] = {"q": q, "r": r, "candidates": cand, "max_N": maxN, "bound_max": dmax ** (q + 1),
                           "needed_for_row": 1 << (np_ - 1), "histogram": dict(sorted(hist.items())),
                           "candidates_with_N_gt_2": rows, "seconds": round(time.time() - t0, 1)}
    out["census_n131"] = res


def audit_brute_cross_check_131(out: dict, np_list=(11, 12), dmax=7) -> None:
    """Direct deg gcd(X^{2^131} - X, L) at deg L = 2^11, 2^12 (C helper) for every
    F_2 candidate, with the pure-Python gcd on a subset as the instrument
    cross-check.  NOTE: at these n' the injection polynomial H has degree
    d^{q+1} = d^12 (q = 11 or 10), far above deg L, so the bound of
    IDEA-20260916-3f7a1c (A) is VACUOUS there and its Stage 3 as written
    ("H-based versus brute at n' in {11, 22}") cannot compare the two methods:
    the method is cross-checked at toy n (Stage 1) instead, and here only the
    two brute instruments are compared.  The n' = 22 spot check (q = 5, H of
    degree d^6) compares the injection count with the C brute count at d = 3."""
    res = {}
    for np_ in np_list:
        q, r = divmod(131, np_)
        t0 = time.time()
        lams = [lam for d in range(3, dmax + 1) for lam in polys_of_degree(d) if not is_linearized(lam)]
        brutes = root_count_batch(131, [(np_, lam) for lam in lams])
        hist = {}
        for b in brutes:
            hist[b] = hist.get(b, 0) + 1
        sub = lams[::41][:6]
        py = [root_count_gcd(np_, lam, 131) for lam in sub]
        cb = [brutes[lams.index(lam)] for lam in sub]
        res[f"np{np_}"] = {"q": q, "r": r, "candidates": len(lams), "max_N_brute": max(brutes),
                           "histogram": dict(sorted(hist.items())),
                           "python_gcd_vs_c_on_subset": [{"lambda": poly_str(l), "python": p, "c": c} for l, p, c in zip(sub, py, cb)],
                           "instruments_agree": py == cb,
                           "injection_bound_here": f"d^{q+1} (vacuous: exceeds deg L = 2^{np_})",
                           "seconds": round(time.time() - t0, 1)}
    t0 = time.time()
    spot = [0b1011, 0b1101]
    brutes = root_count_batch(131, [(22, lam) for lam in spot])
    res["np22_spot_d3"] = {"q": 131 // 22, "r": 131 % 22,
                           "rows": [{"lambda": poly_str(l), "brute_c": b, "injection": injection_count_f2(l, 22, 131)} for l, b in zip(spot, brutes)],
                           "seconds": round(time.time() - t0, 1)}
    out["brute_cross_check_n131"] = res


def audit_splitting_sweep(out: dict) -> None:
    """IDEA-20260916-5c9d6e Stage 2: every completely (>= half) splitting
    L = X^{2^n'} + lambda, lambda in F_2[X] of degree 2..8, prime n <= 31,
    n' <= 15 (deg L <= 2^15), n' not dividing n; check beta >= n/(n+n'-r)."""
    res = []
    viol = []
    for n in (7, 11, 13, 17, 19, 23, 29, 31):
        for np_ in range(2, 16):
            if np_ >= n or n % np_ == 0:
                continue
            q, r = divmod(n, np_)
            for d in range(2, min(8, (1 << np_) - 1) + 1):   # deg lambda < 2^n' (the QSP shape)
                lams = list(polys_of_degree(d))
                Ns = root_count_batch(n, [(np_, lam) for lam in lams])
                for lam, N in zip(lams, Ns):
                    if N >= (1 << (np_ - 1)):
                        ell = math.log2(d)
                        beta = ell * n / (np_ * np_)
                        bound_beta = n / (n + np_ - r)
                        row = {"n": n, "n_prime": np_, "q": q, "r": r, "lambda": poly_str(lam), "d": d, "N": N,
                               "complete": N == (1 << np_), "beta": round(beta, 4), "beta_lower_bound": round(bound_beta, 4),
                               "linearized": is_linearized(lam)}
                        res.append(row)
                        if N == (1 << np_) and beta < bound_beta - 1e-12:
                            viol.append(row)
    out["splitting_sweep"] = {"rows": res, "violations_of_beta_bound": viol, "n_rows": len(res)}


def audit_bound_table_131(out: dict) -> None:
    KAPPA = 4.876
    rows = []
    for np_ in range(2, 131):
        q, r = divmod(131, np_)
        b = 131 / (131 + np_ - r)
        ab = 1 / (2 * KAPPA * b)
        rows.append({"n_prime": np_, "q": q, "r": r, "beta_lower_bound": round(b, 4),
                     "prop8_exponent_at_bound": round(1 - ab / 2, 4), "log2_cost_at_bound": round((1 - ab / 2) * 131, 1)})
    mn = min(rows, key=lambda x: x["beta_lower_bound"])
    out["bound_table_131"] = {"min_beta_lower_bound": mn, "kappa_needed_for_alpha_beta_gt_1_at_min": round(1 / (2 * mn["beta_lower_bound"]), 3),
                              "rows_sample": [x for x in rows if x["n_prime"] in (2, 11, 12, 22, 27, 33, 44, 66, 100, 130)]}


def audit_a17f43_census(out: dict) -> None:
    """Toy census of L_R = X^{2^{a+1}} + c(X) X^{2^a} + e(X), c, e in F_2[X],
    deg <= d0, at prime n with a admissible (r <= q, n = q a + r)."""
    res = {}
    fixtures = {}
    # Type 2 fixtures: n=7: L = X^8 + X^2 + X -> a = 2, c = 0, e = X^2 + X, expect 8
    fixtures["type2_n7"] = {"expected": 8, "count": root_count_gcd(3, 0b110, 7)}
    lam31 = (1 << 128) | (1 << 8) | (1 << 2) | (1 << 1)
    fixtures["type2_n31_a14"] = {"expected": 1 << 15, "count_c": root_count_batch(31, [(15, lam31)])[0]}
    res["fixtures"] = fixtures
    cells = {23: [(11, 2), (7, 3), (5, 3), (4, 3), (3, 3)], 29: [(14, 2), (9, 2), (7, 3), (5, 3), (4, 3)],
             31: [(15, 2), (10, 2), (7, 3), (6, 3), (5, 3)]}
    for n, alist in cells.items():
        for a, d0 in alist:
            q, r = divmod(n, a)
            assert r <= q
            t0 = time.time()
            maxN = 0
            hist = {}
            top = []
            cand = 0
            items = []
            for dc in range(0, d0 + 1):
                for c in (range(1 << dc) if dc == 0 else polys_of_degree(dc)):
                    for de in range(0, d0 + 1):
                        for e in (range(1 << de) if de == 0 else polys_of_degree(de)):
                            lam = (clmul(c, 1 << (1 << a))) ^ e if c else e
                            if lam == 0:
                                continue
                            # skip the linearized-trinomial slice (c constant, e linearized) -- decided by Prop 2
                            if deg(c) <= 0 and is_linearized(e):
                                continue
                            items.append((c, e, lam))
            Ns = root_count_batch(n, [(a + 1, lam) for _, _, lam in items])
            for (c, e, lam), N in zip(items, Ns):
                cand += 1
                hist[N] = hist.get(N, 0) + 1
                if N > maxN:
                    maxN = N
                if N >= 2 * n:
                    top.append({"c": poly_str(c) if c else "0", "e": poly_str(e) if e else "0", "N": N})
            bound = d0 ** (q + 1) + (2 ** (q + 1)) * (1 << (a - r))
            res[f"n{n}_a{a}_d0{d0}"] = {"q": q, "r": r, "candidates": cand, "max_N": maxN, "needed": 1 << a,
                                        "correspondence_bound": bound, "bound_holds": maxN <= bound,
                                        "histogram": dict(sorted(hist.items())), "candidates_with_N_ge_2n": top[:10],
                                        "seconds": round(time.time() - t0, 1)}
    out["a17f43_toy_census"] = res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--skip-slow", action="store_true")
    args = ap.parse_args()
    out = {"schema": "crypto.autoresearch.analysis.qsp_explore.v1", "seed": 20260917}
    t = time.time()
    audit_stage0_hand(out); print("stage0", round(time.time() - t, 1), flush=True)
    audit_stage1_toy(out); print("stage1", round(time.time() - t, 1), flush=True)
    audit_k_coefficients(out); print("kcoef", round(time.time() - t, 1), flush=True)
    audit_proves_too_much(out); print("ptm", round(time.time() - t, 1), flush=True)
    audit_bound_table_131(out)
    audit_census_131(out); print("census131", round(time.time() - t, 1), flush=True)
    audit_brute_cross_check_131(out); print("brute131", round(time.time() - t, 1), flush=True)
    if not args.skip_slow:
        audit_splitting_sweep(out); print("sweep", round(time.time() - t, 1), flush=True)
        audit_a17f43_census(out); print("a17f43", round(time.time() - t, 1), flush=True)
    out["seconds_total"] = round(time.time() - t, 1)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(out, fh, indent=1, default=str)
    # compact summary
    print(json.dumps({k: v for k, v in out.items() if k in ("stage0_n4_np3", "proves_too_much", "k_coefficient_fixture", "bound_table_131")}, indent=1, default=str))
    for k in ("stage1_toy_fixtures", "census_n131", "brute_cross_check_n131"):
        if k in out:
            print(k, json.dumps({kk: {x: y for x, y in vv.items() if x not in ("mismatch_rows", "candidates_with_N_gt_2", "rows")} for kk, vv in out[k].items()}, indent=1, default=str))
    if "splitting_sweep" in out:
        print("splitting_sweep rows:", out["splitting_sweep"]["n_rows"], "violations:", len(out["splitting_sweep"]["violations_of_beta_bound"]))
        for row in out["splitting_sweep"]["rows"]:
            print("  ", row)
    if "a17f43_toy_census" in out:
        for k, v in out["a17f43_toy_census"].items():
            print(k, {x: y for x, y in v.items() if x not in ("histogram",)} if isinstance(v, dict) else v)
    return 0


if __name__ == "__main__":
    sys.exit(main())

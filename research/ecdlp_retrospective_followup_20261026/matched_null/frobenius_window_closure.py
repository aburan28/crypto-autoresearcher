#!/usr/bin/env python3
"""How closed under Frobenius is the prefix window {x : deg x < env} of GF(2^n)?

Context.  crypto PR #2591 (orbit-aware double large primes, RESULTS.md section 5)
merged large points that are Frobenius conjugates of each other and found 34
merges at n=31 against 4.4 expected from the random model (2n-2)/(r-1) per pair
of distinct large points.  An independent review attributed 30 of the 34 to exact
Frobenius images of window abscissae: the factor-base abscissae are the integers
x < 2^env read as polynomials in the field's *sparse* modulus, and for a sparse
modulus x^(2^k) of a low-degree polynomial is again of low degree.

This program tests only that structural premise, from the statement alone:

    for each n and the repository's sparse modulus (smallest irreducible
    polynomial of weight <= 5, read from the integer value of its low part, as
    `find_irreducible_sparse` in crypto src/cryptanalysis/koblitz_index_calculus.rs
    describes), count the unordered pairs {w, w'} of distinct window abscissae
    with w' = w^(2^k) for some 1 <= k < n,

and compares the count with the expectation for a uniform subset of the
2^n - 2 non-F_2 elements.  Because n is prime, every element in this universe
has exactly n - 1 distinct non-self Frobenius conjugates, so the probability
for an unordered pair is (n - 1)/(2^n - 3).  It does not read PR #2591's receipts, so it does not
reproduce "30 of 34"; it shows whether a window that closed would exist at all.

Usage: python3 frobenius_window_closure.py --out OUTPUT.json
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from itertools import combinations


def pdeg(a: int) -> int:
    return a.bit_length() - 1


def pmod(a: int, f: int) -> int:
    df = pdeg(f)
    while a.bit_length() > df:
        a ^= f << (a.bit_length() - 1 - df)
    return a


def pmulmod(a: int, b: int, f: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a.bit_length() > pdeg(f):
            a ^= f
    return r


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def is_irreducible(f: int) -> bool:
    n = pdeg(f)
    # Rabin: x^(2^n) = x mod f, and gcd(x^(2^(n/p)) - x, f) = 1 for each prime p | n
    def x2k(k: int) -> int:
        t = 2
        for _ in range(k):
            t = pmulmod(t, t, f)
        return t

    if x2k(n) != 2:
        return False
    p, m, primes = 2, n, set()
    while m > 1:
        while m % p == 0:
            primes.add(p)
            m //= p
        p += 1
    return all(pgcd(f, x2k(n // q) ^ 2) == 1 for q in primes)


def sparse_modulus(n: int) -> int:
    """Smallest `low` (as an integer) with bit 0 set and at most 3 further bits
    below n such that x^n + low is irreducible over GF(2)."""
    cands = {1}
    for i in range(1, n):
        cands.add(1 | 1 << i)
        for j in range(i + 1, n):
            cands.add(1 | 1 << i | 1 << j)
            for k in range(j + 1, n):
                cands.add(1 | 1 << i | 1 << j | 1 << k)
    for low in sorted(cands):
        if is_irreducible((1 << n) | low):
            return (1 << n) | low
    raise RuntimeError("no sparse irreducible found")


def square(a: int, f: int) -> int:
    return pmulmod(a, a, f)


def random_frobenius_pair_expectation(size: int, n: int) -> float:
    """Expected conjugate pairs in a uniform size-subset of GF(2^n) minus F_2."""
    universe_size = 2 ** n - 2
    if size < 0 or size > universe_size or n < 2:
        raise ValueError("invalid subset size or field degree")
    if any(n % divisor == 0 for divisor in range(2, n)):
        raise ValueError("the formula assumes prime field degree")
    return size * (size - 1) / 2 * (n - 1) / (universe_size - 1)


def poly_str(f: int) -> str:
    return " + ".join(("x^%d" % i if i > 1 else ("x" if i == 1 else "1"))
                      for i in range(pdeg(f), -1, -1) if f >> i & 1)


def pinv(a: int, f: int) -> int:
    """a^(2^n - 2) by square-and-multiply (a != 0)."""
    n = pdeg(f)
    r, e = 1, (1 << n) - 2
    while e:
        if e & 1:
            r = pmulmod(r, a, f)
        a = pmulmod(a, a, f)
        e >>= 1
    return r


def trace(c: int, f: int) -> int:
    t, s_ = 0, c
    for _ in range(pdeg(f)):
        t ^= s_
        s_ = pmulmod(s_, s_, f)
    assert t in (0, 1)
    return t


def has_point(x: int, a_coef: int, b_coef: int, f: int) -> bool:
    """y^2 + xy = x^3 + a x^2 + b has a point over GF(2^n) with this abscissa
    (a, b in F_2).  x = 0: always (y = sqrt b).  Else z^2+z = x + a + b/x^2, Tr = 0."""
    if x == 0:
        return True
    c = x ^ a_coef ^ (pmulmod(pinv(pmulmod(x, x, f), f), 1, f) if b_coef else 0)
    return trace(c, f) == 0


def window_closure(n: int, env: int, a_coef: int, small: int) -> dict:
    f = sparse_modulus(n)
    W = set(range(1 << env))
    W.discard(0)
    W.discard(1)  # F_2 is fixed by Frobenius
    pairs, ks = set(), {}
    for w in sorted(W):
        t = w
        for k in range(1, n):
            t = square(t, f)
            if t in W and t != w:
                pair = (min(w, t), max(w, t))
                pairs.add(pair)
                ks.setdefault(pair, k)
    size = len(W)
    # Every non-F_2 element has n-1 distinct non-self conjugates when n is prime.
    # For an unordered pair from M=2^n-2 elements, the probability is (n-1)/(M-1).
    rand_pairs = random_frobenius_pair_expectation(size, n)
    # points in window involved in at least one conjugate pair
    involved = {a for p in pairs for a in p}
    deg_hist = {}
    for p in pairs:
        d = pdeg(p[0])
        deg_hist[d] = deg_hist.get(d, 0) + 1
    # merges PR #2591 would see from exact Frobenius images only: large window
    # abscissae (x >= 2^small) that carry a point, grouped into classes under
    # x -> x^2; merges = elements - classes.
    large = [w for w in range(1 << small, 1 << env) if has_point(w, a_coef, 1, f)]
    lset, seen, classes, merged_pairs = set(large), set(), 0, 0
    for w in large:
        if w in seen:
            continue
        orbit, t = {w}, w
        for _ in range(1, n):
            t = square(t, f)
            if t in lset:
                orbit.add(t)
        seen |= orbit
        classes += 1
    exact_merges = len(large) - classes
    return dict(n=n, modulus=poly_str(f), modulus_int=hex(f), env=env, a_coef=a_coef,
                small_dimension=small, large_abscissae_with_a_point=len(large),
                exact_frobenius_merges_among_large=exact_merges,
                window_elements_excluding_F2=size,
                conjugate_pairs_in_window=len(pairs),
                random_expectation_for_unordered_pairs=rand_pairs,
                window_elements_in_a_pair=len(involved),
                fraction_of_window_in_a_pair=len(involved) / size,
                low_degree_member_histogram=dict(sorted(deg_hist.items())),
                example_pairs=[(a, b, ks[(a, b)]) for (a, b) in sorted(pairs)[:5]])


# PR #2591 primary series: K_1 at n = 17, 19, 23, 29 and K_0 at n = 31; small
# dimension from its pilot calibration (RESULTS.md section 3: S+1 columns).
AA = {17: 1, 19: 1, 23: 1, 29: 1, 31: 0}
SM = {17: 5, 19: 6, 23: 7, 29: 7, 31: 7}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--env", type=int, default=10)
    ap.add_argument("--ns", default="17,19,23,29,31")
    a = ap.parse_args()
    res = dict(program=dict(file="frobenius_window_closure.py", python=platform.python_version(),
                            argv=sys.argv),
               random_expectation_formula="C(size, 2) * (n - 1) / (2^n - 3); n is prime and the sampled universe excludes F_2",
               cells=[window_closure(int(n), a.env, AA[int(n)], SM[int(n)])
                      for n in a.ns.split(",")])
    json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
    for c in res["cells"]:
        print(c["n"], c["modulus"], "large-with-point", c["large_abscissae_with_a_point"],
              "exact-Frobenius merges", c["exact_frobenius_merges_among_large"],
              "pairs", c["conjugate_pairs_in_window"],
              "random", round(c["random_expectation_for_unordered_pairs"], 4),
              "in-pair fraction", round(c["fraction_of_window_in_a_pair"], 3))
    return 0


if __name__ == "__main__":
    sys.exit(main())

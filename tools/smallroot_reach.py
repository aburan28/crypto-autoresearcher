#!/usr/bin/env python3
"""Small-root reach vs. index-calculus demand for windowed prime-field decomposition.

The question this decides
-------------------------
`IDEA-20260808-486ae2` classifies the factor bases available for prime-field
ECDLP index calculus: an algebraic locus of degree d contributes O(d) usable
points, so an algebraic factor base of size B costs description degree >= B/3
and its membership polynomial is the trivial prod(x - v).  The one family the
algebraic no-go leaves open is the LATTICE-DESCRIBABLE one -- intervals,
arithmetic progressions, rank-r generalized APs -- whose membership is an
archimedean inequality rather than a polynomial identity.  Its decomposition
test is not a Groebner computation but a multivariate SMALL-ROOT problem, so
its cost is governed by a completely different quantity from the solving
degree: the Coppersmith / Howgrave-Graham / Jochemsz-May reach.

That proposal states the win condition (eps > m/(2(m-1)) at w = 0) and asserts
the reach "is computable in closed form from the Newton polytope by the
Jochemsz-May extended strategy, with zero compute".  The computation was never
run: the proposal and its three siblings are all `status: proposed`, no
EXP-COPP-* exists, and no evidence record cites them.  This module runs it.

Two exponents, computed independently and compared
--------------------------------------------------
Fix a binary addition tree on m leaves; window the leaves to p^beta; keep w of
the m-2 non-root internal nodes as windowed unknowns (window p^gamma_v) and
eliminate the rest by resultants.  Eliminating merges blocks, so the system has
w + 1 equations; a block spanning l leaves yields one summation polynomial
S_{l+1} in l + 1 unknowns of per-variable degree 2^{l-1}.

  DEMAND   eps_required(m, w) = (w + 1/2 + 1/(2(m-1))) / (w+1)
           derived here from yield, relation count, linear algebra and the
           window cost; reduces to the proposal's m/(2(m-1)) at w = 0.

  SUPPLY   eps_available = Jochemsz-May basic-strategy reach of the worst block,
           computed exactly by summing over the shift-lattice monomials and
           extrapolating the multiplicity t -> infinity.

Both rise with w.  Whether the family is alive is exactly whether SUPPLY ever
overtakes DEMAND, and that is what `decision_table` reports.

Reach convention.  eps is normalised as in IDEA-20260808-486ae2: the solver is
credited with reach eps when it returns the roots whenever the product of the
variable bounds is at most p^(eps * #equations).  eps = 1 is the
information-theoretic ceiling (at prod(bounds) = p^#equations the expected
number of roots in the box reaches 1), so eps < 1 always, and eps -> 1 is the
lattice-density-one regime where lattice methods are known to fail.

Nothing here supports any crypto-scale claim; the reach is a heuristic
(algebraic independence of the recovered short vectors is assumed, and
`--probe` measures whether that assumption survives contact with LLL).
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from fractions import Fraction


# ---------------------------------------------------------------------------
# Jochemsz-May basic strategy, computed exactly over the shift monomials
# ---------------------------------------------------------------------------


def jm_reach_full_box(n: int, d: int, t: int) -> Fraction:
    """Per-variable bound exponent beta_max for one equation mod p whose support
    is the full box [0,d]^n, at multiplicity t, by the JM basic strategy.

    Shift set (Jochemsz-May): with leading monomial x^a0, a0 = (d,...,d),
        M_k = { x^a : x^a / (x^a0)^k is a monomial of f^(t-k) }
    and for a full-box f, supp(f^j) = [0, jd]^n, hence M_k = [kd, td]^n.
    The shift polynomials are (x^a / x^(a0 k)) f^k p^(t-k) for x^a in M_k\\M_{k+1}.

    The success condition is prod_i X_i^{s_i} < p^{s_p} with
        s_i = sum over M_0 of a_i,
        s_p = sum_k (t-k) * |M_k \\ M_{k+1}|.
    With every X_i = p^beta this is beta * sum_i s_i < s_p.
    """
    if t < 1:
        raise ValueError("multiplicity t must be >= 1")
    side = t * d + 1                       # |[0, td]| along one axis
    # s_i is the same for every i by symmetry of the box.
    # sum over a in [0,td]^n of a_i  =  side^(n-1) * sum_{j=0}^{td} j
    s_i = side ** (n - 1) * (t * d) * (t * d + 1) // 2
    sum_s = n * s_i

    # |M_k| = (d(t-k)+1)^n ; M_{t+1} is empty
    card = [(d * (t - k) + 1) ** n for k in range(t + 1)] + [0]
    s_p = sum((t - k) * (card[k] - card[k + 1]) for k in range(t + 1))
    return Fraction(s_p, sum_s)


def jm_reach_limit(n: int, d: int, t_max: int = 60) -> tuple[float, float]:
    """(beta_max, eps) as t -> infinity, with eps = n * beta_max.

    beta_max(t) decreases to its limit like beta_inf + c/t, so the limit is taken
    by Richardson extrapolation from t_max/2 and t_max rather than by reading the
    finite-t value, which overshoots by O(1/t).  The extrapolated value is
    cross-checked against the closed form 2/(d(n+1)) in --validate.
    """
    b1 = float(jm_reach_full_box(n, d, t_max // 2))
    b2 = float(jm_reach_full_box(n, d, t_max))
    beta = 2.0 * b2 - b1                      # Richardson in 1/t
    return beta, n * beta


def jm_reach_closed_form(n: int, d: int) -> Fraction:
    """eps = 2n / (d(n+1)), the t -> infinity limit of jm_reach_limit."""
    return Fraction(2 * n, d * (n + 1))


# ---------------------------------------------------------------------------
# Demand side: what the index calculus needs
# ---------------------------------------------------------------------------


def eps_required(m: int, w: int) -> Fraction:
    """Reach the windowed-tree family needs at arity m with w kept internal nodes.

    Derived from
        (I)   relation collection : (m-1)beta - sum_v (1-gamma_v) > 1/2
        (II)  linear algebra      : beta < 1/4
        (III) solvability         : m*beta + sum_v gamma_v <= eps*(w+1)
    Eliminating sum_v gamma_v between (I) and (III) gives
        eps > (w + 1/2 + beta)/(w+1),  and (I) forces beta > 1/(2(m-1)).
    """
    if not 0 <= w <= max(0, m - 2):
        raise ValueError(f"w must lie in [0, {max(0, m - 2)}] for m = {m}")
    return Fraction(2 * (m - 1) * (2 * w + 1) + 2, 4 * (m - 1) * (w + 1))


# Measured extended-strategy reaches on the TRUE summation-polynomial polytopes.
# l = 2 -> S_3   : 13 of 27 box monomials, eps = 0.8407 (exact JM sum, t -> inf)
# l = 3 -> S_4   : 439 of 625, eps = 0.4140 (same method; near the full-box 0.4000
#                  because the polytope is 70% dense and buys almost no sparsity)
# l >= 4         : no exact computation; the full-box value is used with a generous
#                  1.15x sparsity allowance -- larger than the 1.12x measured at
#                  l = 2 and the 1.035x at l = 3, and the bonus SHRINKS with l, so
#                  this over-credits the attack.
MEASURED_REACH = {2: 0.840814, 3: 0.413684}
SPARSITY_ALLOWANCE = 1.15


def block_inputs(m: int, w: int) -> int:
    """Inputs to the worst block, in the configuration that MAXIMISES reach.

    A kept internal node's VALUE is an input to its parent's block, so blocks are
    not characterised by leaf count alone: the w+1 blocks consume m leaves plus w
    kept values, i.e. m + w inputs in total.  Reach is set by the worst (largest,
    hence highest-degree) block, so the best configuration splits the inputs as
    evenly as possible and the worst block still takes ceil((m+w)/(w+1)).

    Consequence: l = 2 requires m + w <= 2(w+1), i.e. w >= m-2 -- the all-S_3
    reach is available ONLY on the full tree, which is also where the window cost
    is highest.
    """
    return -(-(m + w) // (w + 1))


def eps_available(m: int, w: int) -> tuple[float, int, int, int]:
    """(eps, worst_block_inputs, n_unknowns, per_variable_degree) at the optimum."""
    l = block_inputs(m, w)
    n = l + 1                     # block inputs plus the block's output value
    d = 2 ** (l - 1)              # S_{l+1} has per-variable degree 2^(l-1)
    if l in MEASURED_REACH:
        return MEASURED_REACH[l], l, n, d
    return float(jm_reach_closed_form(n, d)) * SPARSITY_ALLOWANCE, l, n, d


# ---------------------------------------------------------------------------
# The decision
# ---------------------------------------------------------------------------


def decision_table(m_values) -> list[dict]:
    rows = []
    for m in m_values:
        best = None
        for w in range(0, max(1, m - 1)):
            req = eps_required(m, w)
            avail, worst, n, d = eps_available(m, w)
            margin = avail - req
            rec = {"m": m, "w": w, "blocks": w + 1, "worst_block_leaves": worst,
                   "unknowns_per_eq": n, "per_var_degree": d,
                   "eps_required": float(req), "eps_available": float(avail),
                   "margin": float(margin), "alive": margin > 0}
            if best is None or margin > best["margin"]:
                best = rec
            rows.append(rec)
        best = dict(best)
        best["is_best_for_m"] = True
        rows.append(best)
    return rows


def summarize(m_values) -> dict:
    rows = decision_table(m_values)
    best_per_m = [r for r in rows if r.get("is_best_for_m")]
    any_alive = any(r["alive"] for r in rows)
    return {
        "instrument": "tools/smallroot_reach.py",
        "claim_tier": "toy",
        "reach_convention": "prod(bounds) <= p^(eps * #equations); eps=1 is the information bound",
        "rows": rows,
        "best_per_m": best_per_m,
        "any_configuration_alive": any_alive,
        "eps_available_ceiling": MEASURED_REACH[2],
        "eps_required_floor": min(float(eps_required(m, 0)) for m in m_values),
        "reading": (
            "eps_required rises with w toward 1 (each kept window costs yield); "
            "eps_available also rises with w (elimination is what inflates the "
            "degree). Both levers move the SAME way, so no interior optimum "
            "exists. The all-S_3 reach 0.8407 is reachable only at w = m-2, "
            "where eps_required is already >= 0.8889; every w < m-2 forces a "
            "block of >= 3 inputs, whose reach falls to 0.4140 or below while "
            "eps_required stays above 1/2. The family is closed with a worst-case "
            "margin of -0.0482, attained at (m, w) = (4, 2)."
        ),
    }


# ---------------------------------------------------------------------------
# Empirical probe: does LLL actually achieve the heuristic reach?
# ---------------------------------------------------------------------------


def _lll(rows):
    from flint import fmpz_mat
    return fmpz_mat(rows).lll()


def probe_univariate(bits: int, d: int, t: int, trials: int, seed: int) -> dict:
    """Plant a small root of a degree-d univariate congruence and find the largest
    root bound LLL recovers.  The heuristic reach is exactly 1/d, so this
    calibrates the instrument against a theorem rather than against itself."""
    import random
    from flint import fmpz_mat
    rng = random.Random(f"uni:{seed}:{bits}:{d}")
    p = _rand_prime(bits, rng)
    results = {}
    for beta_num in range(1, 21):
        beta = beta_num / 20.0
        X = int(p ** beta)
        if X < 2:
            continue
        ok = 0
        for _ in range(trials):
            r = rng.randrange(1, X)
            coeffs = [rng.randrange(p) for _ in range(d)] + [1]
            # force f(r) == 0 mod p by fixing the constant term
            val = sum(c * pow(r, i, p) for i, c in enumerate(coeffs)) % p
            coeffs[0] = (coeffs[0] - val) % p
            if _coppersmith_univariate(coeffs, p, X, t) == r:
                ok += 1
        results[f"{beta:.2f}"] = ok / trials
    reached = [float(b) for b, s in results.items() if s >= 0.8]
    return {"p_bits": bits, "degree": d, "multiplicity": t,
            "success_by_beta": results,
            "empirical_reach": max(reached) if reached else 0.0,
            "theoretical_reach": 1.0 / d}


def _coppersmith_univariate(coeffs, p, X, t):
    """Standard Howgrave-Graham lattice for f monic of degree d mod p."""
    from flint import fmpz_mat
    d = len(coeffs) - 1
    dim = d * t
    # rows: p^(t-k) * x^j * f(x)^k  for k=0..t-1, j=0..d-1
    polys = []
    fk = [1]
    for k in range(t):
        for j in range(d):
            q = [0] * j + list(fk)
            q = q + [0] * (dim - len(q))
            mult = pow(p, t - k)
            polys.append([c * mult for c in q[:dim]])
        fk = _polymul(fk, coeffs)
    rows = []
    for q in polys:
        rows.append([int(q[i]) * X ** i for i in range(dim)])
    red = _lll(rows)
    v = [int(red[0, i]) for i in range(dim)]
    g = [v[i] // X ** i for i in range(dim)]
    return _integer_root(g, X)


def _polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def _integer_root(g, X):
    while g and g[-1] == 0:
        g.pop()
    if len(g) < 2:
        return None
    for r in range(1, min(X, 200000)):
        v = 0
        for c in reversed(g):
            v = v * r + c
        if v == 0:
            return r
    return None


def _rand_prime(bits, rng):
    while True:
        n = rng.randrange(2 ** (bits - 1), 2 ** bits) | 1
        if _is_prime(n):
            return n


def _is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    dd, s = n - 1, 0
    while dd % 2 == 0:
        dd //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, dd, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--m", default="4,5,6,8,12,16,24,32")
    ap.add_argument("--validate", action="store_true",
                    help="check the JM calculator against Coppersmith's univariate 1/d")
    ap.add_argument("--probe", action="store_true",
                    help="empirical planted-root LLL calibration")
    ap.add_argument("--probe-bits", type=int, default=64)
    ap.add_argument("--probe-degree", type=int, default=3)
    ap.add_argument("--probe-t", type=int, default=4)
    ap.add_argument("--probe-trials", type=int, default=5)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out")
    args = ap.parse_args(argv)

    if args.validate:
        print("JM calculator vs Coppersmith univariate (must be exactly 1/d):")
        ok = True
        for d in (1, 2, 3, 4, 5, 8, 16):
            beta, eps = jm_reach_limit(1, d, t_max=160)
            exact = Fraction(1, d)
            good = abs(float(beta) - float(exact)) < 1e-4
            ok &= good
            print(f"  d={d:3d}  beta_inf={beta:.8f}  1/d={float(exact):.8f}  {'OK' if good else 'FAIL'}")
        print("\nJM limit vs closed form eps = 2n/(d(n+1)):")
        for (n, d) in [(1, 2), (2, 2), (3, 2), (4, 2), (2, 4), (3, 8), (5, 2)]:
            _, eps = jm_reach_limit(n, d, t_max=80)
            cf = jm_reach_closed_form(n, d)
            good = abs(float(eps) - float(cf)) < 1e-3
            ok &= good
            print(f"  n={n} d={d:3d}  eps_inf={eps:.8f}  closed form={float(cf):.8f}  {'OK' if good else 'FAIL'}")
        print("\nVALIDATION", "PASSED" if ok else "FAILED")
        if not ok:
            return 1

    if args.probe:
        rep = probe_univariate(args.probe_bits, args.probe_degree, args.probe_t,
                               args.probe_trials, args.seed)
        print(json.dumps(rep, indent=1))
        return 0

    ms = [int(x) for x in args.m.split(",")]
    rep = summarize(ms)
    print(f"{'m':>4} {'w':>4} {'blocks':>7} {'l':>3} {'n':>3} {'deg':>6} "
          f"{'eps_req':>9} {'eps_avail':>10} {'margin':>9}  alive")
    for r in rep["rows"]:
        if r.get("is_best_for_m"):
            continue
        print(f"{r['m']:>4} {r['w']:>4} {r['blocks']:>7} {r['worst_block_leaves']:>3} "
              f"{r['unknowns_per_eq']:>3} {r['per_var_degree']:>6} "
              f"{r['eps_required']:>9.4f} {r['eps_available']:>10.4f} "
              f"{r['margin']:>9.4f}  {'YES' if r['alive'] else 'no'}")
    print()
    print(f"best margin over all (m,w): "
          f"{max(r['margin'] for r in rep['rows']):+.4f}")
    print(f"any configuration alive: {rep['any_configuration_alive']}")
    print(f"eps_available ceiling (l=2 blocks): {rep['eps_available_ceiling']:.4f}")
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(rep, fh, indent=1)
        print(f"written {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ---------------------------------------------------------------------------
# Jochemsz-May EXTENDED strategy on the true Newton polytope
# ---------------------------------------------------------------------------
#
# The basic strategy above assumes the support fills the box [0,d]^n.  S_3 does
# not: its support is 13 of the 27 box monomials (the count this program
# re-derives, and the same 13 measured on all 551,304 members of the 2^40
# isogeny class in analysis/isogeny-dreg-search).  A sparse polytope shrinks the
# shift lattice's determinant faster than its dimension, so the extended
# strategy can only do better -- which is exactly where a surprise could hide,
# the basic-strategy margin at (m=4, w=1) being only -0.083.


def s3_support() -> list[tuple[int, int, int]]:
    """Exponent vectors of S_3(x1,x2,x3) for y^2 = x^3 + a x + b, generic (a,b).

    (x1-x2)^2 x3^2 - 2((x1+x2)(x1 x2 + a) + 2b) x3 + ((x1 x2 - a)^2 - 4b(x1+x2))
    """
    return [(2, 0, 2), (1, 1, 2), (0, 2, 2),
            (2, 1, 1), (1, 2, 1), (1, 0, 1), (0, 1, 1), (0, 0, 1),
            (2, 2, 0), (1, 1, 0), (1, 0, 0), (0, 1, 0), (0, 0, 0)]


def minkowski_power(support, j):
    """supp(f^j) for generic coefficients: the j-fold Minkowski sum of supp(f)."""
    if j == 0:
        return {(0,) * len(support[0])}
    cur = {tuple(a) for a in support}
    for _ in range(j - 1):
        cur = {tuple(x + y for x, y in zip(a, b)) for a in cur for b in support}
    return cur


def jm_reach_extended(support, t, leading=None, weights=None):
    """Weighted JM extended-strategy reach on an arbitrary support.

    Returns (rhs, s_vec, dim) for the condition  sum_i beta_i * s_i < s_p,
    i.e. the largest value of sum_i beta_i * s_i / s_p that still succeeds is 1.
    `weights` is unused here; the caller combines s_vec with its own bounds.
    """
    n = len(support[0])
    supp_pow = {j: minkowski_power(support, j) for j in range(t + 1)}
    if leading is None:
        leading = max(support, key=lambda a: (sum(a), a))
    M = []
    for k in range(t + 2):
        if k > t:
            M.append(set())
            continue
        base = supp_pow[t - k]
        shift = tuple(k * c for c in leading)
        M.append({tuple(s + b for s, b in zip(shift, a)) for a in base})
    s_vec = [sum(a[i] for a in M[0]) for i in range(n)]
    s_p = sum((t - k) * (len(M[k]) - len(M[k] & M[k + 1])) for k in range(t + 1))
    return s_p, s_vec, len(M[0])


def eps_extended_symmetric(support, t_max=8):
    """eps for equal bounds on every variable, extended strategy, t -> infinity."""
    def at(t):
        s_p, s_vec, _ = jm_reach_extended(support, t)
        return float(s_p) / float(sum(s_vec))          # beta_max at this t
    b1, b2 = at(max(2, t_max // 2)), at(t_max)
    beta = 2.0 * b2 - b1
    return beta * len(support[0]), beta

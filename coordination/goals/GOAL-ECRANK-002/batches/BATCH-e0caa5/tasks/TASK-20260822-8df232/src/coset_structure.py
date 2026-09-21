#!/usr/bin/env python3
"""TASK-20260822-8df232 -- coset structure of the GOAL-ECRANK-001 twist family.

MEASUREMENT ONLY.  This module computes numbers; it draws no conclusion about
whether degree 8 is reachable.

What it computes, and from what
-------------------------------
Everything here is derived from COMMITTED artifacts of EXP-ECRANK-e1e30e:

  runs/RUN-ECRANK-e1e30e-001/pool.json          base-curve pool (497 distinct j)
  runs/RUN-ECRANK-e1e30e-001/subspace_scan.json per-curve k=3..6 optima (502 rows)
  certificates/cert_deg*.json                   per-class points + PARI r_low

It uses the PYTHON STANDARD LIBRARY ONLY.  In particular it never calls PARI.
That is not a stylistic choice: cypari/PARI is ABSENT from the execution
environment of this task and the task forbids network access, so no new
`ellrank` descent could be run.  Every quantity below is therefore either

  (a) recomputed exactly from committed per-class certificate data
      (points, PARI r_low), with the points re-verified independently here, or
  (b) re-derived from the committed scan table subspace_scan.json,

and any quantity that would require a NEW descent is reported as blocked, never
estimated.

Mathematics recap (see experiments/EXP-ECRANK-e1e30e/source/twist_family.py)
---------------------------------------------------------------------------
For E : y^2 = x^3 + A x + B over Q and squarefree d, the twist
E^(d) : v^2 = u^3 + A d^2 u + B d^3 injects into E(K_V) as the chi_d
eigenvector, so over K_V = Q(sqrt(d) : d in V), dim_F2 V = k,

    rank E(K_V) = sum_{d in V} rank E^(d)(Q).

CERTIFIED count of a class, per the frozen convention of the committed run:

    certified(d) = min(r_low(d), #points exhibited for d)   if r_low >= 0
    certified(d) = 0 and timed_out(d) = True                if r_low < 0

A descent timeout contributes ZERO and is counted separately.  It is never
rank 0.

Coset transport.  If a coset representative d0 shares primes with a class v,
then the squarefree class value d = squarefree(d0*v) differs from d0*v by a
square t^2, and points must be transported between the two models by

    (u, v) -> (u t^2, v t^3)

which sends E^(D) to E^(D t^2).  `transport` implements it and
`self_test_transport` checks it on exact rational points.

Subcommands
-----------
  selftest   arithmetic self-tests (transport, subspace enumeration counts)
  verify     independent exact re-verification of the committed certificates
  fixture    the k=3 regression fixture, at every level it can be checked here
  cosets     k=3 coset decomposition table: total vs max single class
  relation   fitted relations and the base rank that 31 at k=3 would require
  all        run everything and emit coset_structure.json

Usage:
  PYTHONHASHSEED=0 python3 coset_structure.py all --repo <REPO> --out <PATH>
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import platform
import random
import sys
from fractions import Fraction

SUPPORT_COMMITTED = [-1, 2, 3, 5, 7, 11, 13]

# Fixed, recorded sources of randomness.  The measurement itself is fully
# deterministic; the only RNG in this module drives the transport self-test.
SELFTEST_SEED = 20260904

# Seed curves prepended to the pool by the committed scan_pool.py, with the
# base ranks it recorded there.  Copied verbatim from
# experiments/EXP-ECRANK-e1e30e/source/scan_pool.py.
SEED_CURVES = {
    (1, -1, 1, 0, 0): 1,
    (0, 0, 1, -7, 6): 3,
    (0, 1, 1, -2, 0): 2,
    (1, -1, 0, -79, 289): 4,
    (1, 1, 1, -2, 0): 3,
}

CERT_FILES = [
    "cert_deg8_control.json",
    "cert_deg16_multiplicity.json",
    "cert_deg32_multiplicity.json",
    "cert_deg32_eigenspace.json",
    "cert_deg64_eigenspace.json",
]


# --------------------------------------------------------------------------
# exact model arithmetic (no PARI)
# --------------------------------------------------------------------------
def short_model_from_ainvs(ai):
    """(A, B) with y^2 = x^3 + A x + B isomorphic over Q to E(a1..a6).

    Standard c4/c6 formulas, integer arithmetic only.  This replaces the
    PARI call in twist_family.short_model, and agreement with the committed
    certificates' base_curve fields is one of the checks in `verify`.
    """
    a1, a2, a3, a4, a6 = ai
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    c4 = b2 * b2 - 24 * b4
    c6 = -b2 * b2 * b2 + 36 * b2 * b4 - 216 * b6
    return -27 * c4, -54 * c6


def on_curve(A, B, pt):
    x, y = Fraction(pt[0]), Fraction(pt[1])
    return y * y == x * x * x + A * x + B


def ec_add(A, P, Q):
    """Group law on y^2 = x^3 + A x + B over Q.  None is the identity."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y1 != y2 or y1 == 0:
            return None
        lam = (3 * x1 * x1 + A) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)


def ec_mul(A, m, P):
    R = None
    Q = P
    while m:
        if m & 1:
            R = ec_add(A, R, Q)
        Q = ec_add(A, Q, Q)
        m >>= 1
    return R


def is_non_torsion(A, B, pt):
    """Mazur: E(Q)_tors has order in {1..10, 12}, so m*P != O for m = 1..12
    forces P of infinite order."""
    P = (Fraction(pt[0]), Fraction(pt[1]))
    for m in range(1, 13):
        if ec_mul(A, m, P) is None:
            return False
    return True


def transport(pt, t):
    """(u, v) -> (u t^2, v t^3): E^(D) -> E^(D t^2)."""
    x, y = Fraction(pt[0]), Fraction(pt[1])
    return (x * t * t, y * t * t * t)


def squarefree_part(n):
    """Signed squarefree kernel of a nonzero integer, by trial division."""
    if n == 0:
        raise ValueError("zero has no squarefree part")
    s = -1 if n < 0 else 1
    n = abs(n)
    out = 1
    p = 2
    while p * p <= n:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        if e % 2:
            out *= p
        p += 1 if p == 2 else 2
    return s * out * n


def mask_of(d, support):
    """F_2 bitmask of a squarefree d over `support`, or None if unsupported."""
    m = 0
    v = d
    if v < 0:
        if -1 not in support:
            return None
        m |= 1 << support.index(-1)
        v = -v
    for i, g in enumerate(support):
        if g > 0 and v % g == 0:
            v //= g
            m |= 1 << i
    return m if v == 1 else None


def class_value(mask, support):
    d = 1
    for i, g in enumerate(support):
        if mask >> i & 1:
            d *= g
    return d


# --------------------------------------------------------------------------
# F_2 subspace geometry (independent reimplementation)
# --------------------------------------------------------------------------
def subspaces(n, k):
    """Every k-dim subspace of F_2^n exactly once, via reduced row echelon form."""
    out = []
    for pivots in itertools.combinations(range(n), k):
        free = [j for j in range(n) if j not in pivots]
        slots = [[j for j in free if j > piv] for piv in pivots]
        grids = [list(itertools.product([0, 1], repeat=len(s))) for s in slots]
        for choice in itertools.product(*grids):
            basis = []
            for i, piv in enumerate(pivots):
                v = 1 << piv
                for bit, j in zip(choice[i], slots[i]):
                    if bit:
                        v |= 1 << j
                basis.append(v)
            span = [0]
            for b in basis:
                span += [x ^ b for x in span]
            out.append(sorted(span))
    return out


def affine_subspaces(n, k):
    """Every coset m0 + V of every k-dim V <= F_2^n, deduplicated."""
    out = []
    for V in subspaces(n, k):
        reps = {min(m ^ v for v in V) for m in range(1 << n)}
        for m0 in sorted(reps):
            out.append((m0, V))
    return out


def gaussian_binomial(n, k, q=2):
    num = den = 1
    for i in range(k):
        num *= q ** n - q ** i
        den *= q ** k - q ** i
    return num // den


# --------------------------------------------------------------------------
# self tests
# --------------------------------------------------------------------------
def self_test_transport(rng):
    """Transport preserves the curve equation and the group law.

    GOAL-ECRANK-001 shipped XOR coset transport wrong once.  This is the direct
    test of the corrected map on exact rational points.
    """
    checks = []
    # A concrete twisted point taken from the committed deg8 control, moved by
    # an explicit t, plus randomised (A, B, D, t) instances.
    A0, B0 = short_model_from_ainvs([0, -1, 1, 8, -50])
    for _ in range(200):
        D = rng.choice([1, -1, 2, -3, 5, -7, 11, 13, -15, 21, 330])
        t = rng.choice([1, 2, 3, 5, 7, 11, -2, -6])
        x = Fraction(rng.randint(-50, 50), rng.choice([1, 2, 4, 9]))
        AD, BD = A0 * D * D, B0 * D ** 3
        y2 = x * x * x + AD * x + BD
        # work with the point (x, sqrt(y2)) formally: check the identity on the
        # coordinates by comparing both sides of the transported equation.
        xp = x * t * t
        lhs = y2 * (t ** 6)
        ADt, BDt = A0 * (D * t * t) ** 2, B0 * (D * t * t) ** 3
        rhs = xp * xp * xp + ADt * xp + BDt
        checks.append(lhs == rhs)
    ok_eq = all(checks)

    # group-law compatibility on a genuine rational point of the deg8 control
    P = (Fraction(132), Fraction(1188))
    assert on_curve(A0, B0, P)
    ok_hom = True
    for t in (1, 2, 3, 5, -7):
        At, Bt = A0 * (t * t) ** 2, B0 * (t * t) ** 3
        Pt = transport(P, t)
        if not on_curve(At, Bt, Pt):
            ok_hom = False
        if transport(ec_mul(A0, 3, P), t) != ec_mul(At, 3, Pt):
            ok_hom = False
    return {
        "curve_equation_preserved": ok_eq,
        "group_law_preserved": ok_hom,
        "instances": len(checks),
        "rng_seed": SELFTEST_SEED,
    }


def self_test_subspaces():
    out = {}
    ok = True
    for n, k in [(4, 3), (5, 3), (6, 3), (7, 3), (5, 4), (6, 4), (7, 4)]:
        S = subspaces(n, k)
        exp = gaussian_binomial(n, k)
        cos = len(affine_subspaces(n, k))
        exp_cos = exp * (2 ** n // 2 ** k)
        good = len(S) == exp and len(set(map(tuple, S))) == exp and cos == exp_cos
        ok = ok and good
        out["n%d_k%d" % (n, k)] = {
            "subspaces": len(S), "expected_gaussian_binomial": exp,
            "cosets": cos, "expected_cosets": exp_cos, "ok": good,
        }
    out["all_ok"] = ok
    return out


# --------------------------------------------------------------------------
# certificate loading and independent verification
# --------------------------------------------------------------------------
def load_cert(repo, fn):
    with open(os.path.join(repo, "experiments/EXP-ECRANK-e1e30e/certificates", fn)) as f:
        return json.load(f)


def verify_cert(cert):
    """Exact, PARI-free re-verification of one multi-class certificate.

    Checks, all independent of the PARI search that produced the data:
      C1 base curve (A,B) equals the c4/c6 short model of the declared seed
         a-invariants twisted by the declared coset representative;
      C2 every exhibited point lies on E^(d) : v^2 = u^3 + A d^2 u + B d^3;
      C3 every exhibited point is non-torsion by Mazur (m*P != O, m = 1..12);
      C4 the classes are pairwise distinct modulo squares;
      C5 the classes form a coset of a subgroup of the support group, of the
         declared dimension k;
      C6 the declared transport factor t is consistent: squarefree(d0 * d)
         times t^2 equals d0 * d, where d0 is the coset representative.
    """
    A, B = cert["base_curve"]["A"], cert["base_curve"]["B"]
    seed = cert["search"]["seed_a_invariants"]
    d0 = cert["search"]["twist_coset_representative"]
    support = cert["search"]["support"]
    k = cert["field"]["k"]

    A0, B0 = short_model_from_ainvs(seed)
    c1 = (A0 * d0 * d0 == A) and (B0 * d0 ** 3 == B)

    c2 = c3 = True
    c6 = True
    npts = 0
    per_class = []
    timed_out = 0
    for tw in cert["twists"]:
        d = tw["d"]
        Ad, Bd = A * d * d, B * d ** 3
        for pt in tw["points"]:
            npts += 1
            if not on_curve(Ad, Bd, pt):
                c2 = False
            elif not is_non_torsion(Ad, Bd, pt):
                c3 = False
        t = tw.get("transport_factor_t", 1)
        prod = d0 * d
        if squarefree_part(prod) * t * t != prod:
            c6 = False
        rl = tw["pari_r_low"]
        if rl < 0:
            timed_out += 1
            cval = 0
        else:
            cval = min(rl, len(tw["points"]))
        per_class.append({"d": d, "r_low": rl, "n_points": len(tw["points"]),
                          "certified": cval, "timed_out": rl < 0,
                          "transport_factor_t": t})

    ds = [tw["d"] for tw in cert["twists"]]
    c4 = len(set(squarefree_part(d) for d in ds)) == len(ds)

    masks = [mask_of(squarefree_part(d), support) for d in ds]
    if None in masks:
        c5 = False
        V = None
    else:
        m0 = masks[0]
        V = sorted(m ^ m0 for m in masks)
        c5 = (len(set(V)) == 2 ** k and
              all((a ^ b) in set(V) for a in V for b in V))

    score = sum(p["certified"] for p in per_class)
    return {
        "name": cert["name"],
        "objective": cert["objective"],
        "checks": {
            "C1_base_model_matches_seed_and_coset_rep": c1,
            "C2_points_on_twisted_curve": c2,
            "C3_points_non_torsion_mazur": c3,
            "C4_classes_distinct_mod_squares": c4,
            "C5_classes_form_coset_of_subgroup_dim_k": c5,
            "C6_transport_factor_consistent": c6,
        },
        "all_checks_passed": all([c1, c2, c3, c4, c5, c6]),
        "points_verified": npts,
        "declared_score": cert["score"],
        "recomputed_sum_mult": score,
        "score_agrees": score == cert["score"] if cert["objective"] == "sum_mult" else None,
        "recomputed_n_classes": sum(1 for p in per_class if p["certified"] >= 1),
        "timed_out_classes": timed_out,
        "declared_timed_out_classes": cert["search"].get("timed_out_classes"),
        "k": k,
        "support": support,
        "base_rank_over_Q_pari": cert["base_curve"]["rank_over_Q_pari"],
        "per_class": per_class,
        "masks": masks,
        "V": V,
    }


# --------------------------------------------------------------------------
# measurements
# --------------------------------------------------------------------------
def load_scan(repo):
    base = os.path.join(repo, "experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001")
    scan = json.load(open(os.path.join(base, "subspace_scan.json")))
    pool = json.load(open(os.path.join(base, "pool.json")))
    return scan, pool


def measure_fixture(repo, verified):
    """The k=3 regression fixture, at each level it can be checked WITHOUT PARI."""
    scan, pool = load_scan(repo)
    rank_of = {tuple(c["ai"]): c["rank"] for c in pool}
    rank_of.update(SEED_CURVES)
    k3 = [r["k3_mult"] for r in scan]
    best = max(scan, key=lambda r: r["k3_mult"])
    deg8 = next(v for v in verified if v["name"] == "deg8_control")

    return {
        "level_A_artifact_rederivation": {
            "description": "max over the committed 502-row scan table of k3_mult",
            "value": max(k3),
            "target": 20,
            "reproduced": max(k3) == 20,
            "argmax_curve_a_invariants": best["ai"],
            "argmax_row": best,
            "rows": len(scan),
            "pool_size_distinct_j": len(pool),
            "seed_curves_prepended": 5,
            "support": SUPPORT_COMMITTED,
            "source": "experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/subspace_scan.json",
            "independence": ("re-derivation from the committed intermediate artifact; "
                             "NOT an independent recomputation of the underlying descents"),
        },
        "level_B_certificate_recomputation": {
            "description": ("sum of min(r_low, #points) over the 8 classes of the committed "
                            "degree-8 coset, with every point re-verified on-curve and "
                            "non-torsion by stdlib-only exact arithmetic"),
            "value": deg8["recomputed_sum_mult"],
            "target": 20,
            "reproduced": deg8["recomputed_sum_mult"] == 20,
            "all_checks_passed": deg8["all_checks_passed"],
            "checks": deg8["checks"],
            "points_verified": deg8["points_verified"],
            "base_curve_a_invariants": [0, -1, 1, 8, -50],
            "base_rank_over_Q_pari": deg8["base_rank_over_Q_pari"],
            "timed_out_classes": deg8["timed_out_classes"],
            "independence": ("independent of the PARI search for on-curve, non-torsion, "
                             "distinctness, subgroup and transport; the per-class r_low "
                             "values are still PARI's and are NOT re-derived here"),
        },
        "level_C_search_reproduction": {
            "description": ("re-running ellrank over 502 curves x 128 twists to confirm that "
                            "no coset of the pool beats 20"),
            "status": "BLOCKED_INFRASTRUCTURE",
            "reason": ("cypari/PARI is not installed in this execution environment and the "
                       "task forbids network access, so no new descent could be run"),
            "value": None,
            "note": "NOT evidence for or against anything mathematical",
        },
        "argmax_agreement": {
            "scan_argmax_a_invariants": best["ai"],
            "deg8_certificate_base_a_invariants": [0, -1, 1, 8, -50],
            "agree": best["ai"] == [0, -1, 1, 8, -50],
        },
        "base_rank_distribution_in_pool": {
            str(r): sum(1 for c in scan if rank_of[tuple(c["ai"])] == r)
            for r in sorted({rank_of[tuple(c["ai"])] for c in scan})
        },
    }


def k3_subcosets_of(cert_result):
    """Every k=3 coset inside the certified coset, with its decomposition.

    The certified coset is m0 + V with dim V = k.  Choose coordinates on V and
    enumerate all 3-dimensional affine subspaces of F_2^k, mapping each back to
    the 8 classes it selects.  For k = 3 this returns the one coset itself.
    """
    k = cert_result["k"]
    if k < 3:
        return []
    masks = cert_result["masks"]
    cert_by_mask = {m: p for m, p in zip(masks, cert_result["per_class"])}
    m0 = masks[0]
    V = cert_result["V"]
    # coordinates: pick a basis of V by greedy independence over F_2
    basis = []
    span = {0}
    for v in V:
        if v not in span:
            basis.append(v)
            span |= {x ^ v for x in span}
        if len(basis) == k:
            break
    assert len(basis) == k and len(span) == 2 ** k

    def vec_to_mask(w):
        m = 0
        for i, b in enumerate(basis):
            if w >> i & 1:
                m ^= b
        return m

    rows = []
    for a0, W in affine_subspaces(k, 3):
        classes = []
        for w in W:
            mm = m0 ^ vec_to_mask(a0 ^ w)
            classes.append(cert_by_mask[mm])
        vals = [c["certified"] for c in classes]
        total = sum(vals)
        mx = max(vals)
        rows.append({
            "classes_d": [c["d"] for c in classes],
            "certified": vals,
            "total": total,
            "max_single_class": mx,
            "others": total - mx,
            "n_classes_with_a_point": sum(1 for v in vals if v >= 1),
            "timed_out_classes": sum(1 for c in classes if c["timed_out"]),
        })
    return rows


def linfit(xs, ys):
    """Least-squares y = a x + b with R^2 and residual range.  Pure stdlib."""
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = sxy / sxx
    b = my - a * mx
    res = [y - (a * x + b) for x, y in zip(xs, ys)]
    sst = sum((y - my) ** 2 for y in ys)
    sse = sum(r * r for r in res)
    return {
        "slope": a, "intercept": b, "n": n,
        "r_squared": (1 - sse / sst) if sst > 0 else None,
        "residual_min": min(res), "residual_max": max(res),
        "residual_rms": (sse / n) ** 0.5,
    }


def _contingency(rows):
    """count of k=3 cosets by (max single class, total), per certificate."""
    out = {}
    for r in rows:
        out.setdefault(r["certificate"], {})
        key = (r["max_single_class"], r["total"])
        out[r["certificate"]][key] = out[r["certificate"]].get(key, 0) + 1
    return out


def measure_cosets(verified):
    """The separability table: total vs max single class, over every k=3 coset
    that committed per-class certificate data can supply."""
    per_source = []
    all_rows = []
    for cr in verified:
        rows = k3_subcosets_of(cr)
        if not rows:
            continue
        totals = [r["total"] for r in rows]
        maxes = [r["max_single_class"] for r in rows]
        others = [r["others"] for r in rows]
        fit = linfit(maxes, totals)
        per_source.append({
            "certificate": cr["name"],
            "base_curve_rank_over_Q_pari": cr["base_rank_over_Q_pari"],
            "parent_k": cr["k"],
            "n_k3_cosets": len(rows),
            "total_min": min(totals), "total_max": max(totals),
            "total_mean": sum(totals) / len(totals),
            "max_single_class_min": min(maxes), "max_single_class_max": max(maxes),
            "others_min": min(others), "others_max": max(others),
            "others_mean": sum(others) / len(others),
            "others_spread": max(others) - min(others),
            "fit_total_vs_max": fit,
            "best_coset_by_total": max(rows, key=lambda r: r["total"]),
        })
        for r in rows:
            r2 = dict(r)
            r2["certificate"] = cr["name"]
            r2["objective"] = cr["objective"]
            r2["base_curve_rank_over_Q_pari"] = cr["base_rank_over_Q_pari"]
            all_rows.append(r2)

    totals = [r["total"] for r in all_rows]
    maxes = [r["max_single_class"] for r in all_rows]
    others = [r["others"] for r in all_rows]
    pooled_fit = linfit(maxes, totals)

    # distribution of `others` conditioned on the max single class
    by_max = {}
    for m, o in zip(maxes, others):
        by_max.setdefault(m, []).append(o)
    cond = {str(m): {"n": len(v), "others_min": min(v), "others_max": max(v),
                     "others_mean": sum(v) / len(v)}
            for m, v in sorted(by_max.items())}

    def pool_stats(rows):
        if not rows:
            return None
        t = [r["total"] for r in rows]
        m = [r["max_single_class"] for r in rows]
        o = [r["others"] for r in rows]
        bym = {}
        for a, b in zip(m, o):
            bym.setdefault(a, []).append(b)
        return {
            "n_cosets": len(rows),
            "total_min": min(t), "total_max": max(t), "total_mean": sum(t) / len(t),
            "max_single_class_min": min(m), "max_single_class_max": max(m),
            "others_min": min(o), "others_max": max(o), "others_mean": sum(o) / len(o),
            "others_spread": max(o) - min(o),
            "fit_total_vs_max_single_class": linfit(m, t),
            "others_conditioned_on_max_single_class": {
                str(a): {"n": len(v), "others_min": min(v), "others_max": max(v),
                         "others_mean": sum(v) / len(v)}
                for a, v in sorted(bym.items())},
        }

    mult_rows = [r for r in all_rows if r["objective"] == "sum_mult"]
    eig_rows = [r for r in all_rows if r["objective"] == "n_classes"]

    return {
        "n_k3_cosets_measured": len(all_rows),
        "sources": per_source,
        "pooled_skew_warning": (
            "The pooled block below is dominated by cert_deg64_eigenspace, which supplies "
            "11160 of the 12431 cosets and was optimised for the n_classes objective, so "
            "most of its classes carry exactly one exhibited point.  Read "
            "pooled_by_objective, and the per-source rows, before the pooled block."),
        "pooled_by_objective": {
            "sum_mult_certificates": pool_stats(mult_rows),
            "n_classes_certificates": pool_stats(eig_rows),
        },
        "pooled": {
            "total_min": min(totals), "total_max": max(totals),
            "total_mean": sum(totals) / len(totals),
            "others_min": min(others), "others_max": max(others),
            "others_mean": sum(others) / len(others),
            "others_spread": max(others) - min(others),
            "fit_total_vs_max_single_class": pooled_fit,
            "others_conditioned_on_max_single_class": cond,
        },
        "contingency_max_by_total": {
            cr["certificate"]: cr["table"] for cr in [
                {"certificate": name,
                 "table": {
                     "%d|%d" % (m, t): n
                     for (m, t), n in sorted(tab.items())}}
                for name, tab in _contingency(all_rows).items()]
        },
        "rows": all_rows,
    }


def measure_relation(repo, cosets, fixture):
    """The base rank that 31 at k = 3 would require, under stated relations."""
    scan, pool = load_scan(repo)
    rank_of = {tuple(c["ai"]): c["rank"] for c in pool}
    rank_of.update(SEED_CURVES)
    xs = [rank_of[tuple(r["ai"])] for r in scan]
    ys = [r["k3_mult"] for r in scan]
    fit_all = linfit(xs, ys)

    by_rank = {}
    for x, y in zip(xs, ys):
        by_rank.setdefault(x, []).append(y)
    per_rank = {str(r): {"n": len(v), "max_k3_mult": max(v), "min_k3_mult": min(v),
                         "mean_k3_mult": sum(v) / len(v)}
                for r, v in sorted(by_rank.items())}
    # frontier fit: best k3 achieved at each base rank (few points, stated as such)
    fr_x = sorted(by_rank)
    fr_y = [max(by_rank[r]) for r in fr_x]
    fit_frontier = linfit(fr_x, fr_y)

    def solve(fit, target=31):
        if not fit or fit["slope"] == 0:
            return None
        return (target - fit["intercept"]) / fit["slope"]

    pf = cosets["pooled"]["fit_total_vs_max_single_class"]
    other_mean = cosets["pooled"]["others_mean"]

    return {
        "relation_1_k3_total_vs_base_rank": {
            "form": "k3_mult = a * base_rank + b, over all 502 scanned curves",
            "fit": fit_all,
            "per_base_rank": per_rank,
            "base_ranks_present": sorted(by_rank),
            "base_rank_required_for_31": solve(fit_all),
            "label": "MODELED (extrapolation far outside the fitted range)",
        },
        "relation_1b_frontier": {
            "form": "max observed k3_mult at each base rank = a * base_rank + b",
            "fit": fit_frontier,
            "points": {str(r): m for r, m in zip(fr_x, fr_y)},
            "base_rank_required_for_31": solve(fit_frontier),
            "label": "MODELED (4 points, base ranks 1-4 only, n=1,1,497,3)",
        },
        "relation_2_total_vs_max_single_class": {
            "form": "k3 total = a * (max single class certified rank) + b, over the "
                    "%d k=3 cosets measured from committed certificates"
                    % cosets["n_k3_cosets_measured"],
            "fit": pf,
            "additive_form_total_minus_max": {
                "mean": other_mean,
                "min": cosets["pooled"]["others_min"],
                "max": cosets["pooled"]["others_max"],
            },
            "max_single_class_required_for_31_under_linear_fit": solve(pf),
            "max_single_class_required_for_31_under_additive_form": 31 - other_mean,
            "label": "MEASURED fit over certificate-derived cosets; the value required "
                     "for 31 is MODELED extrapolation",
        },
        "note": ("Every 'required' figure here is a MODELED extrapolation from fits whose "
                 "support is stated beside them.  None of them is a measurement, and none "
                 "of them is a statement about reachability."),
    }


def blocked_items():
    return [
        {
            "item": "handoff deliverable 2: extended twist support beyond 7 primes, "
                    "k = 3 and k = 4 re-optimisation",
            "status": "OPEN AND UNATTEMPTED",
            "reason": ("requires new PARI ellrank descents for every twist of every pool "
                       "curve over the enlarged support; cypari/PARI is absent from this "
                       "execution environment and network access is forbidden by the task"),
            "classification": "infrastructure_error",
            "not": "not tried, not screened, not a negative observation",
            "what_would_unblock": "a session with cypari (or gp) installed; the profiling "
                                  "pass is ~502 curves x 256 twists at a 3 s descent alarm",
        },
        {
            "item": "handoff deliverable 1 at search level: confirm 20 is the maximum over "
                    "the pool by re-running the descents",
            "status": "OPEN AND UNATTEMPTED",
            "reason": "same missing dependency",
            "classification": "infrastructure_error",
            "not": "not tried, not screened, not a negative observation",
        },
        {
            "item": "k = 3 coset decomposition for pool curves other than the five carrying "
                    "a committed per-class certificate",
            "status": "OPEN AND UNATTEMPTED",
            "reason": ("subspace_scan.json records only per-curve optima, not per-class "
                       "certified vectors, so no other curve's coset structure is "
                       "recoverable from committed data without new descents"),
            "classification": "infrastructure_error",
            "not": "not tried, not screened, not a negative observation",
        },
    ]


def environment_block():
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "modules_used": ["stdlib only (json, itertools, fractions, argparse, random)"],
        "pari_gp_available": False,
        "cypari_available": False,
        "numpy_available_but_unused": True,
        "network": "none (task constraint; nothing fetched)",
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
    }


# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["selftest", "verify", "fixture", "cosets",
                                    "relation", "all"])
    ap.add_argument("--repo", default="/home/user/crypto-autoresearcher")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    rng = random.Random(SELFTEST_SEED)
    st = {"transport": self_test_transport(rng), "subspaces": self_test_subspaces()}
    if args.cmd == "selftest":
        print(json.dumps(st, indent=2))
        return 0

    certs = [load_cert(args.repo, fn) for fn in CERT_FILES]
    verified = [verify_cert(c) for c in certs]
    if args.cmd == "verify":
        print(json.dumps([{k: v for k, v in r.items()
                           if k not in ("per_class", "masks", "V")} for r in verified],
                         indent=2))
        return 0

    fixture = measure_fixture(args.repo, verified)
    if args.cmd == "fixture":
        print(json.dumps(fixture, indent=2))
        return 0

    cosets = measure_cosets(verified)
    if args.cmd == "cosets":
        print(json.dumps({k: v for k, v in cosets.items() if k != "rows"}, indent=2))
        return 0

    relation = measure_relation(args.repo, cosets, fixture)
    if args.cmd == "relation":
        print(json.dumps(relation, indent=2))
        return 0

    out = {
        "schema": "crypto.autoresearch.coset_structure.v1",
        "task_id": "TASK-20260822-8df232",
        "goal_id": "GOAL-ECRANK-002",
        "batch_id": "BATCH-e0caa5",
        "produced_by": "src/coset_structure.py",
        "measurement_only": True,
        "interpretation": "none; interpretation is a separate Coordinator act",
        "provenance": {
            "repo_commit": os.environ.get("TASK_GIT_COMMIT"),
            "repo_dirty": os.environ.get("TASK_GIT_DIRTY"),
            "command": os.environ.get("TASK_COMMAND"),
            "requested_policy": "executor-implementation",
            "resolved_model_id": os.environ.get("TASK_RESOLVED_MODEL"),
            "reasoning_effort": os.environ.get("TASK_REASONING_EFFORT"),
            "seeds": {"selftest_rng_seed": SELFTEST_SEED,
                      "measurement_rng": "none; the measurement is fully deterministic",
                      "pythonhashseed": os.environ.get("PYTHONHASHSEED")},
            "inputs": [
                "experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/pool.json",
                "experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/subspace_scan.json",
                "experiments/EXP-ECRANK-e1e30e/certificates/cert_deg8_control.json",
                "experiments/EXP-ECRANK-e1e30e/certificates/cert_deg16_multiplicity.json",
                "experiments/EXP-ECRANK-e1e30e/certificates/cert_deg32_multiplicity.json",
                "experiments/EXP-ECRANK-e1e30e/certificates/cert_deg32_eigenspace.json",
                "experiments/EXP-ECRANK-e1e30e/certificates/cert_deg64_eigenspace.json",
            ],
            "support_committed": SUPPORT_COMMITTED,
            "support_extended": None,
        },
        "environment": environment_block(),
        "self_tests": st,
        "certificate_verification": [
            {k: v for k, v in r.items() if k not in ("masks", "V")} for r in verified
        ],
        "certificate_claim_note": (
            "This task claims no discrete log and no factor-base relation, so "
            "docs/claims-and-verification.md certificate kinds do not apply to a NEW "
            "claim here: certificate.kind = none for the measurement itself.  What is "
            "verified above are the PRE-EXISTING committed rank-lower-bound certificates "
            "of EXP-ECRANK-e1e30e, re-checked by the stdlib-only exact arithmetic in this "
            "file, which shares no code with the PARI search that produced them."
        ),
        "fixture_k3": fixture,
        "coset_decomposition": cosets,
        "relations": relation,
        "extended_support": {
            "status": "OPEN AND UNATTEMPTED",
            "support_used": None,
            "k3_optimum": None,
            "k4_optimum": None,
            "reason": ("cypari/PARI absent from this execution environment; network access "
                       "forbidden by the task; no new descent could be run"),
            "classification": "infrastructure_error",
        },
        "open_and_unattempted": blocked_items(),
        "boundary_of_what_was_tested": {
            "support": SUPPORT_COMMITTED,
            "base_curves_with_per_class_data": [c["base_curve"]["minimal_model_a_invariants"]
                                                for c in certs],
            "pool": "497 distinct-j curves of PARI rank >= 3 from small-coefficient "
                    "enumeration (a1 in {0,1}, a2 in {-1,0,1}, a3 in {0,1}, |a4| <= 20, "
                    "|a6| <= 50) plus 5 seed curves = 502 rows",
            "base_ranks_present_over_Q": [1, 2, 3, 4],
            "transfer_assumptions": (
                "None are made here.  The k=3 cosets measured are sub-cosets of five "
                "specific certified cosets on five specific base curves; they are NOT a "
                "uniform sample of k=3 cosets over the pool, and every statistic below is "
                "scoped to exactly that set.  No toy-scale number here is a "
                "cryptographic-scale claim."
            ),
        },
    }
    rows = out["coset_decomposition"].pop("rows")
    if args.out:
        rows_path = os.path.join(
            os.path.dirname(os.path.abspath(args.out)),
            os.environ.get("TASK_RUN_DIR", "runs/RUN-8df232-005-all"),
            "k3_coset_rows.json")
        os.makedirs(os.path.dirname(rows_path), exist_ok=True)
        with open(rows_path, "w") as f:
            json.dump(rows, f, indent=1)
        out["coset_decomposition"]["rows_file"] = (
            os.environ.get("TASK_RUN_DIR", "runs/RUN-8df232-005-all")
            + "/k3_coset_rows.json")
        out["coset_decomposition"]["rows_note"] = (
            "one JSON object per k=3 coset (%d of them): its 8 class values, the "
            "per-class certified counts, total, max_single_class, others, and "
            "timed_out_classes.  Split out of this file for size only; nothing is "
            "summarised away, and contingency_max_by_total above is the complete "
            "joint distribution." % len(rows))
    text = json.dumps(out, indent=2, sort_keys=False)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text + "\n")
        print("wrote %s (%d bytes)" % (args.out, len(text) + 1))
    else:
        print(text)
    # console summary
    print("--- summary ---")
    print("fixture level A (scan re-derivation) k3 max:",
          fixture["level_A_artifact_rederivation"]["value"],
          "reproduced:", fixture["level_A_artifact_rederivation"]["reproduced"])
    print("fixture level B (certificate recomputation):",
          fixture["level_B_certificate_recomputation"]["value"],
          "all checks:", fixture["level_B_certificate_recomputation"]["all_checks_passed"])
    print("fixture level C (search reproduction):",
          fixture["level_C_search_reproduction"]["status"])
    print("k=3 cosets measured:", cosets["n_k3_cosets_measured"])
    print("others = total - max_single_class: min %d max %d mean %.3f" % (
        cosets["pooled"]["others_min"], cosets["pooled"]["others_max"],
        cosets["pooled"]["others_mean"]))
    print("extended support:", out["extended_support"]["status"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""INDEPENDENT re-verification of the independence certificates of EXP-ECQ-f5af06.

DELIBERATELY DOES NOT IMPORT exact_certify.py.  Every routine below -- the group
law, the point count, the mod-l coordinatisation and the F_l rank -- is written
again from scratch here, so that running this file re-proves the certificate
rather than restating the solver's own answer.  This is the certificate
discipline of docs/claims-and-verification.md: a claim is re-verified by code
independent of the solver.

It reads ONLY the committed deliverables:
    certification.json      (part A)
    twist_search.json       (part C, gated curves that found points)
    extension_search.json   (part B, any hit)
and re-checks, in exact integer arithmetic and with NO FLOATING POINT ANYWHERE:

  (1) every point lies on the stated model;
  (2) no point is torsion (Mazur: order in {1..10, 12});
  (3) the stated torsion bound really divides gcd_p #E(F_p) over the stated primes;
  (4) the stated prime l is coprime to that torsion bound;
  (5) each stated good prime p is a prime of good reduction at which every point
      is p-integral and l | #E(F_p);
  (6) the stacked matrix of psi_p images over the stated primes really has the
      stated F_l-rank, hence the points really are independent modulo torsion.

THIRD-PARTY RE-RUNNABLE: needs only Python 3 (stdlib) and the JSON deliverables.

    python3 verify_certificate.py [--dir <task directory>]

Exit status 0 iff every certificate in scope re-verifies.
"""
import argparse
import json
import os
import sys
from fractions import Fraction as F
from math import gcd

MAZUR_ORDERS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12)
INF = ("infinity",)


# ----------------------------- exact group law -----------------------------
def add_Q(ai, P, Q):
    """Group law on y^2 + a1xy + a3y = x^3 + a2x^2 + a4x + a6 over Q (Fractions)."""
    if P is INF:
        return Q
    if Q is INF:
        return P
    a1, a2, a3, a4, a6 = ai
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y1 + y2 + a1 * x2 + a3 == 0:
            return INF
        num = 3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1
        den = 2 * y1 + a1 * x1 + a3
    else:
        num = y2 - y1
        den = x2 - x1
    lam = F(num, 1) / den if not isinstance(num, F) else num / den
    nu = y1 - lam * x1
    x3 = lam * lam + a1 * lam - a2 - x1 - x2
    y3 = -(lam + a1) * x3 - nu - a3
    return (x3, y3)


def mul_Q(ai, n, P):
    R = INF
    if n < 0:
        n = -n
        a1, a2, a3, a4, a6 = ai
        P = (P[0], -P[1] - a1 * P[0] - a3)
    Qp = P
    while n:
        if n & 1:
            R = add_Q(ai, R, Qp)
        Qp = add_Q(ai, Qp, Qp)
        n >>= 1
    return R


def on_curve_Q(ai, P):
    a1, a2, a3, a4, a6 = ai
    x, y = P
    return y * y + a1 * x * y + a3 * y == x * x * x + a2 * x * x + a4 * x + a6


# ----------------------------- exact arithmetic over F_p -------------------
def add_p(ai, p, P, Q):
    if P is INF:
        return Q
    if Q is INF:
        return P
    a1, a2, a3, a4, a6 = ai
    x1, y1 = P
    x2, y2 = Q
    if (x1 - x2) % p == 0:
        if (y1 + y2 + a1 * x2 + a3) % p == 0:
            return INF
        num = (3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1) % p
        den = (2 * y1 + a1 * x1 + a3) % p
    else:
        num = (y2 - y1) % p
        den = (x2 - x1) % p
    lam = num * pow(den, -1, p) % p
    nu = (y1 - lam * x1) % p
    x3 = (lam * lam + a1 * lam - a2 - x1 - x2) % p
    y3 = (-(lam + a1) * x3 - nu - a3) % p
    return (x3, y3)


def mul_p(ai, p, n, P):
    R = INF
    Qp = P
    while n:
        if n & 1:
            R = add_p(ai, p, R, Qp)
        Qp = add_p(ai, p, Qp, Qp)
        n >>= 1
    return R


def npoints(ai, p):
    """#E(F_p), counted independently of the solver: brute force over x and y
    would be O(p^2), so count roots of the quadratic in y by an exact Euler
    criterion.  Exact integer arithmetic."""
    a1, a2, a3, a4, a6 = [a % p for a in ai]
    if p == 2:
        n = 1
        for x in range(2):
            for y in range(2):
                if (y * y + a1 * x * y + a3 * y - (x ** 3 + a2 * x * x + a4 * x + a6)) % 2 == 0:
                    n += 1
        return n
    n = 1
    e = (p - 1) // 2
    for x in range(p):
        f = (x * x * x + a2 * x * x + a4 * x + a6) % p
        b = (a1 * x + a3) % p
        D = (b * b + 4 * f) % p
        if D == 0:
            n += 1
        elif pow(D, e, p) == 1:
            n += 2
    return n


def b_inv(ai):
    a1, a2, a3, a4, a6 = ai
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return b2, b4, b6, b8


def disc_of(ai):
    b2, b4, b6, b8 = b_inv(ai)
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


def fl_rank(rows, l):
    rows = [list(r) for r in rows]
    m = len(rows[0]) if rows else 0
    rank = 0
    col = 0
    while col < m and rank < len(rows):
        piv = None
        for i in range(rank, len(rows)):
            if rows[i][col] % l:
                piv = i
                break
        if piv is None:
            col += 1
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        inv = pow(rows[rank][col], -1, l)
        rows[rank] = [(v * inv) % l for v in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col] % l:
                f = rows[i][col]
                rows[i] = [(a - f * b) % l for a, b in zip(rows[i], rows[rank])]
        rank += 1
        col += 1
    return rank


def coords_in_l_torsion(ai, p, elems, l):
    basis = []
    coords = []
    for g in elems:
        if not basis:
            span = {INF: (0, 0)}
        elif len(basis) == 1:
            span = {}
            X = INF
            for a in range(l):
                span[X] = (a, 0)
                X = add_p(ai, p, X, basis[0])
        else:
            span = {}
            X = INF
            for a in range(l):
                Y = X
                for b in range(l):
                    span[Y] = (a, b)
                    Y = add_p(ai, p, Y, basis[1])
                X = add_p(ai, p, X, basis[0])
        if g in span:
            coords.append(span[g])
        else:
            if len(basis) >= 2:
                return None
            basis.append(g)
            coords.append((1, 0) if len(basis) == 1 else (0, 1))
    return coords


# ----------------------------- the verification ----------------------------
def verify(ainvs, points, l, primes, claimed_rank, torsion_bound,
           torsion_primes, label, report):
    ai = [int(a) for a in ainvs]
    aiF = [F(a) for a in ai]
    P = [(F(x), F(y)) for x, y in points]
    fail = []

    disc = disc_of(ai)
    if disc == 0:
        fail.append("singular model")

    # (1) on-curve
    off = [i for i, pt in enumerate(P) if not on_curve_Q(aiF, pt)]
    if off:
        fail.append("points not on the stated model: %s" % off)

    # (2) non-torsion (Mazur)
    tors = [i for i, pt in enumerate(P) if any(mul_Q(aiF, m, pt) is INF for m in MAZUR_ORDERS)]
    if tors:
        fail.append("torsion points present: %s" % tors)

    # (3) torsion bound really divides gcd #E(F_p) over the stated primes
    if torsion_primes:
        g = 0
        for p in torsion_primes:
            g = gcd(g, npoints(ai, p))
        if torsion_bound is not None and g != torsion_bound:
            fail.append("torsion bound %s does not match recomputed gcd %s"
                        % (torsion_bound, g))
        tb = g
    else:
        tb = torsion_bound

    # (4) l coprime to the torsion bound
    if tb is not None and l is not None and tb % l == 0:
        fail.append("l = %s divides the torsion bound %s: the homomorphism does "
                    "not kill torsion" % (l, tb))

    # (5)+(6) rebuild the stacked matrix from scratch
    rank = 0
    if l is not None and primes:
        rows = [[] for _ in P]
        for p in primes:
            if disc % p == 0:
                fail.append("prime %d is a prime of BAD reduction" % p)
                continue
            if any(pt[0].denominator % p == 0 or pt[1].denominator % p == 0 for pt in P):
                fail.append("some point is not %d-integral" % p)
                continue
            N = npoints(ai, p)
            if N % l:
                fail.append("l = %d does not divide #E(F_%d) = %d" % (l, p, N))
                continue
            aip = [a % p for a in ai]
            imgs = []
            for pt in P:
                x = (pt[0].numerator % p) * pow(pt[0].denominator % p, -1, p) % p
                y = (pt[1].numerator % p) * pow(pt[1].denominator % p, -1, p) % p
                imgs.append(mul_p(aip, p, N // l, (x, y)))
            co = coords_in_l_torsion(aip, p, imgs, l)
            if co is None:
                fail.append("E[%d](F_%d) has rank > 2: impossible" % (l, p))
                continue
            for i in range(len(P)):
                rows[i].extend(co[i])
        rank = fl_rank(rows, l)
        if rank < claimed_rank:
            fail.append("recomputed F_%d-rank %d is BELOW the claimed rank lower "
                        "bound %d" % (l, rank, claimed_rank))

    ok = not fail
    report.append({
        "label": label,
        "n_points": len(P),
        "claimed_rank_lower_bound": claimed_rank,
        "recomputed_Fl_rank": rank,
        "l": l,
        "n_primes_rechecked": len(primes or []),
        "recomputed_torsion_bound": tb,
        "on_curve_all": not off,
        "no_torsion_points": not tors,
        "verified": ok,
        "failures": fail,
    })
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ap.add_argument("--raw-out", default=None)
    a = ap.parse_args()
    report = []
    allok = True

    cpath = os.path.join(a.dir, "certification.json")
    if os.path.exists(cpath):
        c = json.load(open(cpath))
        pa = c["part_a"]
        full = pa["certifier_full_output"]
        allok &= verify(full["a_invariants"],
                        c["certifier_full_output_points"] if "certifier_full_output_points" in c
                        else json.load(open(os.path.join(
                            a.dir, "..", "..", "inputs", "ICARM-302.json")))["witness_points_xy_as_rationals"],
                        pa["prime_l_used"], pa["good_primes_used"],
                        pa["certified_rank_lower_bound_k"], pa["torsion_bound"],
                        pa["torsion_bound_primes"],
                        "PART A: ICARM no. 302, %d witness points" % pa["of_n_points"], report)

    for fn, key in (("extension_search.json", "hits"), ("twist_search.json", "gated")):
        fp = os.path.join(a.dir, fn)
        if not os.path.exists(fp):
            continue
        doc = json.load(open(fp))
        for row in doc.get("certificates_to_reverify", []):
            allok &= verify(row["a_invariants"], row["points"], row.get("l"),
                            row.get("primes_used"), row["certified_rank_lower_bound"],
                            row.get("torsion_bound"), row.get("torsion_bound_primes"),
                            row["label"], report)

    doc = {
        "part": "A-reverify",
        "independent_reverification": report,
        "all_verified": allok,
        "verifier": ("verify_certificate.py, written independently of "
                     "exact_certify.py; stdlib only; no floating point anywhere"),
        "metrics": {
            "certificates_reverified": len(report),
            "certificates_verified_ok": sum(1 for r in report if r["verified"]),
            "all_verified": allok,
        },
        "protocol_certificate": {
            "kind": "independence_certificate",
            "role": ("INDEPENDENT RE-VERIFICATION of the certificates emitted by the "
                     "solver runs; this run asserts no new rank result of its own"),
        },
    }
    print(json.dumps(doc, indent=1))
    if a.raw_out:
        json.dump(doc, open(a.raw_out, "w"), indent=1)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())

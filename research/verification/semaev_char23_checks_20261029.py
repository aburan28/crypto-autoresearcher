#!/usr/bin/env python3
"""Exhaustive exact checks of Semaev's S_3 and of KN-FIND-a8990a in characteristics 2 and 3.

Two claims flagged by docs/reports/2026-10-29-cfsg-lessons-ecdlp-exposure are
checked here by direct group-law computation, with no Semaev formula in the
reference side:

* SEMAEV-S3: the published S_3 (char > 3 short Weierstrass; char 2
  y^2 + xy = x^3 + a2 x^2 + a6) satisfies
  S_3(x1, x2, X) = lc * (X - x(P1+P2)) * (X - x(P1-P2)) for every pair of
  base-field abscissae, where P1, P2 are points over the quadratic extension.
  This is Semaev's correspondence (KR-IC-5a43e5), checked on every pair.
* MONODROMY-B/C: KN-FIND-a8990a Theorems B and C at m = 3 and m = 4. For every
  good tuple a in F_q^{m-1}, the polynomial whose roots are the signed-sum
  abscissae has F_q coefficients, distinct roots, and either all roots in F_q
  (exactly when the fibre classes c(a_i) agree) or none. The class counts
  S^k N^{n-k} + N^k S^{n-k} are checked exactly. This is done in
  characteristics 2 and 3 as well as an odd prime, using generic long
  Weierstrass arithmetic, so it does not depend on any S_m formula.

Exact computation over small fields only; it says nothing about ECDLP cost.
Usage: python3 semaev_char23_checks_20261029.py OUT.json
"""
from __future__ import annotations

import itertools
import json
import sys
import time


class Field:
    """GF(p^K) with elements encoded as base-p integers; log tables for products."""

    def __init__(self, p: int, K: int):
        self.p, self.K, self.Q = p, K, p ** K
        self.mod = self._irreducible()
        self.exp, self.log = self._tables()
        if p == 2:
            self.addt = None
        else:
            dig = [self._digits(a) for a in range(self.Q)]
            self.addt = [[self._undigits([(x + y) % p for x, y in zip(dig[a], dig[b])])
                          for b in range(self.Q)] for a in range(self.Q)]
            self.negt = [self._undigits([(-x) % p for x in dig[a]]) for a in range(self.Q)]

    def _digits(self, a):
        return [(a // self.p ** i) % self.p for i in range(self.K)]

    def _undigits(self, d):
        return sum(c * self.p ** i for i, c in enumerate(d))

    def _irreducible(self):
        p, K = self.p, self.K
        for tail in itertools.product(range(p), repeat=K):
            poly = list(tail) + [1]  # monic, low degree first
            if poly[0] == 0:
                continue
            if self._order_of_x(poly) is not None:
                return poly
        raise ValueError("no primitive polynomial found")

    def _order_of_x(self, poly):
        """Return Q-1 if x generates the multiplicative group mod poly (so poly is primitive)."""
        p, K, Q = self.p, self.K, self.p ** self.K
        cur, one = [1] + [0] * (K - 1), [1] + [0] * (K - 1)
        for i in range(1, Q):
            cur = [0] + cur  # multiply by x
            top = cur.pop()
            if top:
                cur = [(c - top * poly[j]) % p for j, c in enumerate(cur)]
            if cur == one:
                return i if i == Q - 1 else None
        return None

    def _tables(self):
        p, K, Q = self.p, self.K, self.Q
        exp, log = [0] * (2 * Q), [0] * Q
        cur = [1] + [0] * (K - 1)
        for i in range(Q - 1):
            v = self._undigits(cur)
            exp[i] = v
            log[v] = i
            cur = [0] + cur
            top = cur.pop()
            if top:
                cur = [(c - top * self.mod[j]) % p for j, c in enumerate(cur)]
        for i in range(Q - 1, 2 * Q):
            exp[i] = exp[i - (Q - 1)]
        return exp, log

    def add(self, a, b):
        return a ^ b if self.p == 2 else self.addt[a][b]

    def neg(self, a):
        return a if self.p == 2 else self.negt[a]

    def sub(self, a, b):
        return self.add(a, self.neg(b))

    def mul(self, a, b):
        if a == 0 or b == 0:
            return 0
        return self.exp[self.log[a] + self.log[b]]

    def inv(self, a):
        if a == 0:
            raise ZeroDivisionError
        return self.exp[(self.Q - 1 - self.log[a]) % (self.Q - 1)]

    def powr(self, a, e):
        if a == 0:
            return 0 if e else 1
        return self.exp[(self.log[a] * e) % (self.Q - 1)]

    def from_int(self, n):
        n %= self.p
        return n  # the prime-field element n is the constant polynomial n


class Curve:
    """Long Weierstrass y^2 + a1 xy + a3 y = x^3 + a2 x^2 + a4 x + a6 over F; O is None."""

    def __init__(self, F, a1, a2, a3, a4, a6):
        self.F = F
        self.a = (a1, a2, a3, a4, a6)
        self.fibre = {}
        f = F
        for x in range(F.Q):
            rhs = f.add(f.add(f.add(f.powr(x, 3), f.mul(a2, f.mul(x, x))), f.mul(a4, x)), a6)
            ys = []
            for y in range(F.Q):
                lhs = f.add(f.add(f.mul(y, y), f.mul(a1, f.mul(x, y))), f.mul(a3, y))
                if lhs == rhs:
                    ys.append(y)
            self.fibre[x] = ys

    def neg(self, P):
        if P is None:
            return None
        f, (a1, _, a3, _, _) = self.F, self.a
        x, y = P
        return (x, f.sub(f.neg(y), f.add(f.mul(a1, x), a3)))

    def add(self, P, R):
        f, (a1, a2, a3, a4, _) = self.F, self.a
        if P is None:
            return R
        if R is None:
            return P
        x1, y1 = P
        x2, y2 = R
        if x1 == x2:
            if R == self.neg(P):
                return None
            num = f.sub(f.add(f.add(f.mul(f.from_int(3), f.mul(x1, x1)), f.mul(f.from_int(2), f.mul(a2, x1))), a4),
                        f.mul(a1, y1))
            den = f.add(f.add(f.mul(f.from_int(2), y1), f.mul(a1, x1)), a3)
        else:
            num, den = f.sub(y2, y1), f.sub(x2, x1)
        lam = f.mul(num, f.inv(den))
        x3 = f.sub(f.sub(f.sub(f.add(f.mul(lam, lam), f.mul(a1, lam)), a2), x1), x2)
        y3 = f.sub(f.sub(f.mul(lam, f.sub(x1, x3)), y1), f.add(f.mul(a1, x3), a3))
        return (x3, y3)

    def is_two_torsion(self, P):
        return P is None or self.neg(P) == P


def subfield(F, q):
    """Elements z of F with z^q = z, i.e. the subfield F_q."""
    return [z for z in range(F.Q) if F.powr(z, q) == z]


def semaev_s3_coeffs(F, curve, x1, x2):
    """Coefficients (c2, c1, c0) of S_3(x1, x2, X) in X for the published formulas."""
    f = F
    a1, a2, a3, a4, a6 = curve.a
    if F.p > 3:
        assert a1 == a2 == a3 == 0
        d = f.sub(x1, x2)
        c2 = f.mul(d, d)
        s, pr = f.add(x1, x2), f.mul(x1, x2)
        c1 = f.neg(f.mul(f.from_int(2), f.add(f.mul(s, f.add(pr, a4)), f.mul(f.from_int(2), a6))))
        t = f.sub(pr, a4)
        c0 = f.sub(f.mul(t, t), f.mul(f.mul(f.from_int(4), a6), s))
        return c2, c1, c0
    if F.p == 2:
        assert a1 == 1 and a3 == a4 == 0
        s = f.add(x1, x2)
        c2 = f.mul(s, s)
        c1 = f.mul(x1, x2)
        pr = f.mul(x1, x2)
        c0 = f.add(f.mul(pr, pr), a6)
        return c2, c1, c0
    raise ValueError("no published closed S_3 checked in characteristic 3")


def check_s3(F, base, curve, perturb=False):
    f, bad, pairs = F, [], 0
    for x1, x2 in itertools.product(base, repeat=2):
        if x1 == x2 or not curve.fibre[x1] or not curve.fibre[x2]:
            continue
        P1, P2 = (x1, curve.fibre[x1][0]), (x2, curve.fibre[x2][0])
        S, D = curve.add(P1, P2), curve.add(P1, curve.neg(P2))
        c2, c1, c0 = semaev_s3_coeffs(F, curve, x1, x2)
        if perturb:  # known-false control: S_3 with its constant term off by one
            c0 = f.add(c0, 1)
        # lc * (X - s)(X - d) = lc X^2 - lc (s + d) X + lc s d, with O contributing a degree drop.
        roots = [R[0] for R in (S, D) if R is not None]
        if len(roots) == 2:
            s, d = roots
            want = (c2, f.neg(f.mul(c2, f.add(s, d))), f.mul(c2, f.mul(s, d)))
            got = (c2, c1, c0)
        else:
            got, want = (c2, c1, c0), None  # x1 != x2 makes both sums affine
        pairs += 1
        if want is None or got != want:
            bad.append([x1, x2])
    return {"pairs_checked": pairs, "mismatches": len(bad), "first_mismatches": bad[:5]}


def check_monodromy(F, base, q, curve, m, corrupt=False):
    f = F
    n = m - 1
    base_set = set(base)

    def c(a):
        ys = curve.fibre[a]
        if len(ys) == 1:
            return "*"
        if not ys:
            raise AssertionError("every abscissa has a point over the quadratic extension")
        return 0 if ys[0] in base_set else 1

    cls = {a: c(a) for a in base}
    if corrupt:  # known-false control: flip the fibre class of one rational abscissa
        flip = next(a for a in base if cls[a] == 0)
        cls[flip] = 1
    S = sum(1 for a in base if cls[a] == 0)
    N = sum(1 for a in base if cls[a] == 1)
    signs = [(1,) + e for e in itertools.product((1, -1), repeat=n - 1)]
    stats = {"good": 0, "split": 0, "quadratic": 0, "violations": 0, "first_violations": []}
    class_counts = {}
    for a in itertools.product(base, repeat=n):
        if any(cls[x] == "*" for x in a):
            continue
        P = [(x, curve.fibre[x][0]) for x in a]
        good = True
        for r in range(1, n):
            for idx in itertools.combinations(range(n), r):
                for e in itertools.product((1, -1), repeat=r):
                    Rsum = None
                    for i, s in zip(idx, e):
                        Rsum = curve.add(Rsum, P[i] if s == 1 else curve.neg(P[i]))
                    if curve.is_two_torsion(Rsum):
                        good = False
        sums = []
        for e in signs:
            Rsum = None
            for Pi, s in zip(P, e):
                Rsum = curve.add(Rsum, Pi if s == 1 else curve.neg(Pi))
            if Rsum is None:
                good = False
            else:
                sums.append(Rsum[0])
        if not good:
            continue
        stats["good"] += 1
        key = tuple(cls[x] for x in a)
        canon = min(key, tuple(1 - k for k in key))
        class_counts[canon] = class_counts.get(canon, 0) + 1
        distinct = len(set(sums)) == len(sums)
        # coefficients of prod (T - r) lie in F_q
        coeffs = [1]
        for r in sums:
            nxt = [0] * (len(coeffs) + 1)
            for i, cc in enumerate(coeffs):
                nxt[i] = f.add(nxt[i], f.mul(cc, f.neg(r)))
                nxt[i + 1] = f.add(nxt[i + 1], cc)
            coeffs = nxt
        in_base = all(cc in base_set for cc in coeffs)
        rational = [r in base_set for r in sums]
        same = len(set(key)) == 1
        ok = distinct and in_base and ((same and all(rational)) or (not same and not any(rational)))
        if same and all(rational):
            stats["split"] += 1
        elif not same and not any(rational):
            stats["quadratic"] += 1
        if not ok:
            stats["violations"] += 1
            if len(stats["first_violations"]) < 5:
                stats["first_violations"].append({"a": list(a), "classes": list(key)})
    # Exact class-count law S^k N^{n-k} + N^k S^{n-k} applies to all tuples of a class,
    # before removing non-good ones; recount over all non-branch tuples.
    full = {}
    for a in itertools.product([x for x in base if cls[x] != "*"], repeat=n):
        key = tuple(cls[x] for x in a)
        canon = min(key, tuple(1 - k for k in key))
        full[canon] = full.get(canon, 0) + 1
    law_ok = True
    for canon, cnt in full.items():
        k = sum(1 for v in canon if v == 0)
        predicted = S ** k * N ** (n - k) + (N ** k * S ** (n - k) if canon != tuple(1 - v for v in canon) else 0)
        if cnt != predicted:
            law_ok = False
    stats.update(S=S, N=N, class_count_law_holds=law_ok)
    return stats


CASES = [
    # (label, p, k, coefficients as (a1, a2, a3, a4, a6) over the prime field)
    ("F_31 y^2=x^3+2x+7", 31, 1, (0, 0, 0, 2, 7)),
    ("F_31 y^2=x^3+11x+3", 31, 1, (0, 0, 0, 11, 3)),
    ("F_32 y^2+xy=x^3+x^2+1", 2, 5, (1, 1, 0, 0, 1)),
    ("F_32 y^2+xy=x^3+1", 2, 5, (1, 0, 0, 0, 1)),
    ("F_27 y^2=x^3+x^2+1 (ordinary)", 3, 3, (0, 1, 0, 0, 1)),
    ("F_27 y^2=x^3+2x^2+2 (ordinary)", 3, 3, (0, 2, 0, 0, 2)),
    ("F_27 y^2=x^3+2x+1 (supersingular)", 3, 3, (0, 0, 0, 2, 1)),
]


def main(out):
    report = {"schema": "semaev-char23-checks/v1", "script": "research/verification/semaev_char23_checks_20261029.py",
              "cases": []}
    t0 = time.time()
    for label, p, k, coeffs in CASES:
        q = p ** k
        F = Field(p, 2 * k)
        base = subfield(F, q)
        assert len(base) == q
        curve = Curve(F, *[F.from_int(c) for c in coeffs])
        rec = {"curve": label, "q": q, "extension": f"GF({p}^{2 * k})"}
        if p != 3:
            rec["semaev_s3"] = check_s3(F, base, curve)
        for m in (3, 4):
            rec[f"monodromy_m{m}"] = check_monodromy(F, base, q, curve, m)
        # Controls: the same instrument must reject a wrong S_3 and a wrong class map.
        if p != 3:
            rec["control_perturbed_s3_mismatches"] = check_s3(F, base, curve, perturb=True)["mismatches"]
        rec["control_corrupt_class_violations_m3"] = check_monodromy(F, base, q, curve, 3, corrupt=True)["violations"]
        report["cases"].append(rec)
        print(json.dumps(rec), flush=True)
    report["seconds"] = round(time.time() - t0, 1)
    report["all_pass"] = all(
        c.get("semaev_s3", {"mismatches": 0})["mismatches"] == 0
        and all(c[f"monodromy_m{m}"]["violations"] == 0 and c[f"monodromy_m{m}"]["class_count_law_holds"]
                for m in (3, 4))
        and c.get("control_perturbed_s3_mismatches", 1) > 0
        and c["control_corrupt_class_violations_m3"] > 0
        for c in report["cases"])
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1)
    print("all_pass", report["all_pass"])
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

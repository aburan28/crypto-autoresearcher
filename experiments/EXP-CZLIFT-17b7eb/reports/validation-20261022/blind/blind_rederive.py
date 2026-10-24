#!/usr/bin/env python3
"""Blind re-derivation (joint J3) for TASK-20261022-282b02 / EXP-CZLIFT-17b7eb.

Written from experiments/EXP-CZLIFT-17b7eb/specification.yaml, trial-plan.json,
ledger/hypotheses/H-CZLIFT-889c9d.yaml and general mathematics ONLY. No path in
review_plan.blind_rederivation.blind_from was opened before this file and its
output were sealed with sha256sum.

Quantity (review_plan.blind_rederivation.quantity): for the CM discriminants
D in {-3,-11,-19,-43,-67,-163} and p <= 1500, the anomalous primes per D, and
for each curve v_p(z([p]P^)) on the canonical lift and on the lift with a6
perturbed by p, for three points P chosen here.

Independent choices made here (none taken from the producer):
  * anomalous primes from the norm equation 4p = 1 + |D| v^2 (trace 1), p >= 7
    (hypothesis assumption), cross-checked by brute-force point counting;
  * curve model: short Weierstrass y^2 = x^3 + a x + b with
      j != 0:  a = -3 j (j-1728), b = 2 j (j-1728)^2   (j-invariant exactly j_D),
               replaced by its quadratic twist (a u^2, b u^3), u the least
               non-residue mod p, when the reduction has trace -1;
      j  = 0:  a = 0, b = least b in [1, p-1] with #E(F_p) = p.
    Every Z_p-curve with j = j_D exactly and this reduction is Z_p-isomorphic
    to the Serre-Tate canonical lift, so these are canonical lifts;
  * lift classes: canonical; isomorphic re-model (a(1+p)^2, b(1+p)^3);
    a6 + p (the literal task wording); a4 + p; a6 + p^2; a4 + p^2;
  * three points P per curve: the point with least x (least y), and two points
    drawn with random.Random(SEED) -- fixed per curve;
  * three point sections: x = integer rep of x(P) then Hensel y ("int");
    x = x(P) + p * (uniform random higher digits) then Hensel y ("randx");
    x = Teichmuller lift of x(P) then Hensel y ("teich");
  * v_p(z([p]P^)) computed two ways:
      (A) closed form: [p]P^ = P^ + [p-1]P^ and, with x1 = x(P^),
          x2 = x([p-1]P^) (integral, computed mod p^N with unit denominators
          only), z([p]P^) = p^k (L^2 - (x1+x2) p^{2k}) / (L^3 - L(2x1+x2) p^{2k}
          + y1 p^{3k}) where p^k || (x2-x1) and L = (y2-y1) p^k/(x2-x1) is a
          unit; hence v_p(z) = v_p(x2 - x1);
      (B) a generic p-adic float class (valuation + unit mod p^r) running
          plain double-and-add for [p]P^ including the final addition, then
          z = -x/y. (A) and (B) must agree.
  * Smart ratio: Q = dP with d uniform in [2, p-2], Q^ lifted by the same
    section; leading digit of z([p]Q^)/z([p]P^) compared with d.
"""
import hashlib
import json
import random
import sys
from fractions import Fraction

SEED = 2026102282  # validator's own seed, derived from the task id
PMAX = 1500
PMIN = 7
N = 10  # p-adic absolute precision (digits); spec precision is 8
J_CM = {
    -3: 0,
    -11: -(2 ** 15),
    -19: -(2 ** 15) * 3 ** 3,
    -43: -(2 ** 18) * 3 ** 3 * 5 ** 3,
    -67: -(2 ** 15) * 3 ** 3 * 5 ** 3 * 11 ** 3,
    -163: -(2 ** 18) * 3 ** 3 * 5 ** 3 * 23 ** 3 * 29 ** 3,
}
D_LIST = [-3, -11, -19, -43, -67, -163]


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def anomalous_primes_norm(D):
    out = []
    v = 1
    while True:
        num = 1 + (-D) * v * v
        if num % 4 == 0:
            p = num // 4
            if p > PMAX:
                break
            if p >= PMIN and is_prime(p):
                out.append(p)
        v += 2
    return out


def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def count_points(a, b, p):
    a, b = a % p, b % p
    return 1 + sum(1 + legendre(x * x * x + a * x + b, p) for x in range(p))


def least_nonresidue(p):
    for u in range(2, p):
        if legendre(u, p) == -1:
            return u
    raise AssertionError


def jinv(a, b):
    a, b = Fraction(a), Fraction(b)
    den = 4 * a ** 3 + 27 * b ** 2
    return 1728 * 4 * a ** 3 / den


def vp_int(n, p):
    if n == 0:
        return None
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def vp_frac(q, p):
    if q == 0:
        return None
    return vp_int(q.numerator, p) - vp_int(q.denominator, p)


def cm_model(D, p):
    if D == -3:
        for b in range(1, p):
            if count_points(0, b, p) == p:
                return 0, b, {"form": "y^2=x^3+b", "b_mod_p": b}
        raise AssertionError("no anomalous j=0 twist")
    j = J_CM[D]
    c = j - 1728
    a, b = -3 * j * c, 2 * j * c * c
    assert a % p and b % p
    n = count_points(a, b, p)
    if n == p:
        return a, b, {"form": "a=-3jc,b=2jc^2", "twist": 1}
    assert n == p + 2, (D, p, n)
    u = least_nonresidue(p)
    return a * u * u, b * u ** 3, {"form": "a=-3jc,b=2jc^2", "twist": u}


# ---------------------------------------------------------------- method (A)
def inv_unit(x, m, p):
    assert x % p != 0, "non-unit denominator"
    return pow(x, -1, m)


def add_aff(P, Q, a, m, p):
    x1, y1 = P
    x2, y2 = Q
    if (x1 - x2) % m == 0:
        assert (y1 + y2) % m != 0
        lam = (3 * x1 * x1 + a) * inv_unit(2 * y1, m, p) % m
    else:
        lam = (y2 - y1) * inv_unit(x2 - x1, m, p) % m
    x3 = (lam * lam - x1 - x2) % m
    y3 = (lam * (x1 - x3) - y1) % m
    return x3, y3


def mul_aff(k, P, a, m, p):
    R = None
    for bit in bin(k)[2:]:
        if R is not None:
            R = add_aff(R, R, a, m, p)
        if bit == "1":
            R = P if R is None else add_aff(R, P, a, m, p)
    return R


def z_of_pP_closed(Ph, a, p, n):
    """Return (k, unit u mod p^(n-k)) with z([p]P^) = p^k * u, or (n, None) if k >= n."""
    m = p ** n
    x1, y1 = Ph
    x2, y2 = mul_aff(p - 1, Ph, a, m, p)
    dx = (x2 - x1) % m
    if dx == 0:
        return n, None
    k = vp_int(dx, p)
    mk = p ** (n - k)
    L = (y2 - y1) * pow(dx // p ** k, -1, mk) % mk
    num = (L * L - (x1 + x2) * p ** (2 * k)) % mk
    den = (L ** 3 - L * (2 * x1 + x2) * p ** (2 * k) + y1 * p ** (3 * k)) % mk
    return k, num * pow(den, -1, mk) % mk


# ---------------------------------------------------------------- method (B)
class Qp:
    """p-adic float: value p^v * u, u a unit known mod p^r; zero has v=abs prec."""

    __slots__ = ("p", "v", "u", "r")

    def __init__(self, p, v, u, r):
        self.p, self.v, self.r = p, v, r
        self.u = u % (p ** r) if r > 0 else 0

    @classmethod
    def from_int(cls, p, x, absprec):
        x %= p ** absprec
        if x == 0:
            return cls(p, absprec, 0, 0)
        v = vp_int(x, p)
        return cls(p, v, x // p ** v, absprec - v)

    def is_zero(self):
        return self.r <= 0

    def absprec(self):
        return self.v + max(self.r, 0)

    def __mul__(self, o):
        if self.is_zero() or o.is_zero():
            ap = min(self.v + o.absprec(), o.v + self.absprec())
            return Qp(self.p, ap, 0, 0)
        r = min(self.r, o.r)
        return Qp(self.p, self.v + o.v, self.u * o.u, r)

    def inv(self):
        assert not self.is_zero(), "division by p-adic zero"
        return Qp(self.p, -self.v, pow(self.u, -1, self.p ** self.r), self.r)

    def __truediv__(self, o):
        return self * o.inv()

    def __neg__(self):
        return Qp(self.p, self.v, -self.u, self.r) if not self.is_zero() else self

    def __add__(self, o):
        p = self.p
        ap = min(self.absprec(), o.absprec())
        vmin = min(self.v, o.v)
        if vmin >= ap:
            return Qp(p, ap, 0, 0)
        s = 0
        if not self.is_zero():
            s += self.u * p ** (self.v - vmin)
        if not o.is_zero():
            s += o.u * p ** (o.v - vmin)
        s %= p ** (ap - vmin)
        if s == 0:
            return Qp(p, ap, 0, 0)
        w = vp_int(s, p)
        return Qp(p, vmin + w, s // p ** w, ap - vmin - w)

    def __sub__(self, o):
        return self + (-o)


def qp_add(P, Q, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    dx = x2 - x1
    if dx.is_zero():
        sy = y1 + y2
        if sy.is_zero():
            return None
        lam = (Qp.from_int(x1.p, 3, 99) * x1 * x1 + a) / (Qp.from_int(x1.p, 2, 99) * y1)
    else:
        lam = (y2 - y1) / dx
    x3 = lam * lam - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return x3, y3


def z_of_pP_generic(Ph, a, p, n):
    a_ = Qp.from_int(p, a, n)
    P = (Qp.from_int(p, Ph[0], n), Qp.from_int(p, Ph[1], n))
    R = None
    for bit in bin(p)[2:]:
        R = qp_add(R, R, a_) if R is not None else None
        if bit == "1":
            R = qp_add(R, P, a_)
    if R is None:
        return None
    x, y = R
    z = -(x / y)
    return z


# ---------------------------------------------------------------- sections
def sqrt_table(p):
    t = {}
    for y in range(p):
        t.setdefault(y * y % p, []).append(y)
    return t


def hensel_y(x, y0, a, b, p, n):
    m = p ** n
    f = (x ** 3 + a * x + b) % m
    y = y0 % m
    for _ in range(n + 2):
        y = (y - (y * y - f) * pow(2 * y, -1, m)) % m
    assert (y * y - f) % m == 0 and (y - y0) % p == 0
    return y


def teichmuller(x, p, n):
    m = p ** n
    t = x % m
    for _ in range(n + 1):
        t = pow(t, p, m)
    return t


def lift_point(P, section, a, b, p, n, rng):
    x0, y0 = P
    if section == "int":
        x = x0
    elif section == "randx":
        x = x0 + p * rng.randrange(p ** (n - 1))
    elif section == "teich":
        x = teichmuller(x0, p, n)
    else:
        raise ValueError(section)
    return x % p ** n, hensel_y(x, y0, a, b, p, n)


def mul_modp(k, P, a, p):
    return mul_aff(k, P, a, p, p)


def main(out_path):
    rng = random.Random(SEED)
    primes = {D: anomalous_primes_norm(D) for D in D_LIST}
    curves = []
    for D in D_LIST:
        for p in primes[D]:
            curves.append((D, p))
    curves.sort(key=lambda c: (c[1], c[0]))
    # brute-force cross-check: for every prime 7 <= p <= PMAX, which of the six
    # j_D (j != 0 via both twists; j = 0 via all b) admit a curve with #E = p.
    brute = {D: [] for D in D_LIST}
    for p in range(PMIN, PMAX + 1):
        if not is_prime(p):
            continue
        for D in D_LIST:
            j = J_CM[D]
            if j == 0:
                if p % 3 != 1:
                    continue
                # trace of y^2 = x^3 + b runs over six twists; check all classes of b mod (F_p^*)^6
                found = False
                g = next(g for g in range(2, p) if all(pow(g, (p - 1) // q, p) != 1 for q in prime_factors(p - 1)))
                for e in range(6):
                    if count_points(0, pow(g, e, p), p) == p:
                        found = True
                        break
                if found:
                    brute[D].append(p)
            else:
                c = j - 1728
                a, b = -3 * j * c, 2 * j * c * c
                if a % p == 0 or b % p == 0 or (4 * a ** 3 + 27 * b ** 2) % p == 0:
                    continue
                n = count_points(a, b, p)
                if n in (p, p + 2):
                    brute[D].append(p)
    sections = ["int", "randx", "teich"]
    rows = []
    agree_AB = 0
    total_AB = 0
    for D, p in curves:
        a0, b0, meta = cm_model(D, p)
        jc = Fraction(J_CM[D])
        assert jinv(a0, b0) == jc
        assert count_points(a0, b0, p) == p
        lifts = {
            "canonical": (a0, b0),
            "isomorphic": (a0 * (1 + p) ** 2, b0 * (1 + p) ** 3),
            "a6+p": (a0, b0 + p),
            "a4+p": (a0 + p, b0),
            "a6+p2": (a0, b0 + p * p),
            "a4+p2": (a0 + p * p, b0),
        }
        e = 3 if J_CM[D] == 0 else 1
        sq = sqrt_table(p)
        pts = []
        for x in range(p):
            r = sq.get((x ** 3 + a0 * x + b0) % p)
            if r and r[0] != 0:
                pts.append((x, min(r)))
                break
        allpts = [(x, y) for x in range(p) for y in sq.get((x ** 3 + a0 * x + b0) % p, [])]
        assert len(allpts) == p - 1
        while len(pts) < 3:
            P = rng.choice(allpts)
            if P not in pts:
                pts.append(P)
        crow = {
            "D": D, "p": p, "e": e, "model": meta,
            "a_mod_p": a0 % p, "b_mod_p": b0 % p,
            "a_b_sha256": hashlib.sha256(f"{a0},{b0}".encode()).hexdigest()[:16],
            "points": pts, "lifts": {},
        }
        for lname, (a, b) in lifts.items():
            dj = jinv(a, b) - jc
            vdj = vp_frac(dj, p)
            pred_deg = (vdj is None) or (vdj >= 2 * e)
            cells = []
            for P in pts:
                d = rng.randrange(2, p - 1)
                Q = mul_modp(d, P, a0, p)
                for s in sections:
                    srng = random.Random(rng.randrange(2 ** 62))
                    Ph = lift_point(P, s, a, b, p, N, srng)
                    Qh = lift_point(Q, s, a, b, p, N, srng)
                    kP, uP = z_of_pP_closed(Ph, a, p, N)
                    kQ, uQ = z_of_pP_closed(Qh, a, p, N)
                    zg = z_of_pP_generic(Ph, a, p, N)
                    kg = N if (zg is None or zg.is_zero()) else zg.v
                    total_AB += 1
                    agree_AB += int(kg == kP)
                    ratio_digit = None
                    if uP is not None and uQ is not None and kP == kQ:
                        ratio_digit = uQ * pow(uP, -1, p) % p
                    cells.append({
                        "P": list(P), "d": d, "section": s,
                        "v_z_pP": kP, "v_z_pQ": kQ, "v_generic": kg,
                        "capped": kP >= N,
                        "ratio_leading_digit": ratio_digit,
                        "ratio_equals_d": (ratio_digit == d % p) if ratio_digit is not None else None,
                    })
            vs = [c["v_z_pP"] for c in cells]
            crow["lifts"][lname] = {
                "v_dj": vdj, "two_e": 2 * e, "predicted_degenerate": pred_deg,
                "v_z_min": min(vs), "v_z_max": max(vs),
                "rule_agrees_all": all((v >= 2) == pred_deg for v in vs),
                "smart_hits": sum(1 for c in cells if c["ratio_equals_d"]),
                "cells": cells,
            }
        rows.append(crow)
    # summary
    summ = {}
    for lname in ["canonical", "isomorphic", "a6+p", "a4+p", "a6+p2", "a4+p2"]:
        vs = [c["v_z_pP"] for r in rows for c in r["lifts"][lname]["cells"]]
        summ[lname] = {
            "cells": len(vs),
            "v_z_hist": {str(k): vs.count(k) for k in sorted(set(vs))},
            "rule_agreement_all": all(r["lifts"][lname]["rule_agrees_all"] for r in rows),
            "curves_predicted_degenerate": sum(r["lifts"][lname]["predicted_degenerate"] for r in rows),
            "smart_hits": sum(r["lifts"][lname]["smart_hits"] for r in rows),
            "v_dj_by_curve": {f"{r['D']}:{r['p']}": r["lifts"][lname]["v_dj"] for r in rows},
        }
    out = {
        "task_id": "TASK-20261022-282b02",
        "experiment_id": "EXP-CZLIFT-17b7eb",
        "joint": "J3",
        "seed": SEED, "precision_N": N, "pmin": PMIN, "pmax": PMAX,
        "anomalous_primes_by_D_norm_equation": {str(D): primes[D] for D in D_LIST},
        "anomalous_primes_by_D_bruteforce": {str(D): brute[D] for D in D_LIST},
        "norm_vs_bruteforce_agree": all(primes[D] == brute[D] for D in D_LIST),
        "curve_count": len(curves),
        "p_range": [min(p for _, p in curves), max(p for _, p in curves)],
        "method_A_vs_B_agree": f"{agree_AB}/{total_AB}",
        "summary_by_lift": summ,
        "curves": rows,
    }
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({k: out[k] for k in [
        "anomalous_primes_by_D_norm_equation", "norm_vs_bruteforce_agree",
        "curve_count", "p_range", "method_A_vs_B_agree"]}, indent=1))
    for lname, s in summ.items():
        print(lname, {k: s[k] for k in ["cells", "v_z_hist", "rule_agreement_all",
                                         "curves_predicted_degenerate", "smart_hits"]})


def prime_factors(n):
    out, q = [], 2
    while q * q <= n:
        if n % q == 0:
            out.append(q)
            while n % q == 0:
                n //= q
        q += 1
    if n > 1:
        out.append(n)
    return out


if __name__ == "__main__":
    main(sys.argv[1])

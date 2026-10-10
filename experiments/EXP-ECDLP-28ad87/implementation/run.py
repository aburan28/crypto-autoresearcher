#!/usr/bin/env python3
"""EXP-ECDLP-28ad87: cover floor over F_p itself (genus-2 cover C: y^2 = f(x^2) of E: y^2 = f(x)).

Measures the decomposition probability and relation-collection cost of reduced-factor-base
index calculus on Jac(C)(F_p) against Pollard rho on E, on special and matched random primes.
Pure Python 3 standard library. Observations only; no hypothesis verdict is computed here.

Representation. C has the degree-6 model y^2 = F(x), F = x^6 + a x^2 + b, so it has two
F_p-points at infinity inf+, inf-. A reduced class is [D - (inf+ + inf-)] with D an affine
effective divisor of degree 2, stored as Mumford (u, v), deg u = 2; the class 0 is None.
Cantor composition plus ONE reduction step is exactly this group law (the reduction of a
degree-4 D1 + D2 uses div(y - v) with deg v <= 3). Exceptional cases (lead coeff of v
equal to +-1, probability ~1/p) land on divisors involving infinity and raise Exceptional.

Documented design points that go beyond the one-line contract (see the execution report):
 * the l-subgroup <phi^*P> has index ~p in Jac(C), so a walk confined to it would contain
   about one decomposable element in total. Each walk element is therefore
   R = [r]A + [s]B + T with T in [l]Jac(C)(F_p) (the cofactor part); multiplying a relation
   by the cofactor kills T. Curves are required to have l^2 not dividing #E and l not
   dividing #E'' (E'': Y^2 = X f(X), the other elliptic quotient, #Jac = #E * #E''), so the
   l-part of Jac(C) is cyclic of order l and mod-l linear algebra is sound.
 * walk steps add a uniformly chosen one of 20 precomputed multipliers (one Cantor addition
   per decomposition test), not fresh scalar multiplications.
 * the field-op counter charges a modular exponentiation as bitlength + popcount mults.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import primeset  # noqa: E402

EXP_ID = "EXP-ECDLP-28ad87"
CNT = [0, 0]          # F_p multiplications, F_p inversions
PM = [0]              # current modulus


class Exceptional(Exception):
    pass


# ---------------------------------------------------------------- E arithmetic
def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R


def count_points(p, a, b):
    table = [0] * p
    for y in range(p):
        table[y * y % p] = 1
    total = p + 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v:
            total += 1 if table[v] else -1
    return total


def count_points_twist_quartic(p, a, b):
    """#E'' for E'': Y^2 = X^4 + a X^2 + b X (two points at infinity, lead coeff 1)."""
    table = [0] * p
    for y in range(p):
        table[y * y % p] = 1
    total = p + 2
    for x in range(p):
        v = (x * x * x * x + a * x * x + b * x) % p
        if v:
            total += 1 if table[v] else -1
        else:
            total += 0
    return total


def factor_small(n):
    f = {}
    q = 2
    while q * q <= n:
        while n % q == 0:
            f[q] = f.get(q, 0) + 1
            n //= q
        q += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def sqrt_mod(n, p):
    if n == 0:
        return 0
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p
            i += 1
        bexp = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, bexp * bexp % p, t * bexp * bexp % p, r * bexp % p
    return r


def is_qr(n, p):
    return n % p == 0 or pow(n, (p - 1) // 2, p) == 1


def random_point(p, a, b, rng):
    while True:
        x = rng.randrange(p)
        v = (x ** 3 + a * x + b) % p
        if v and is_qr(v, p):
            return (x, sqrt_mod(v, p))


# ---------------------------------------------------------------- polynomials over F_p (low -> high)
def trim(a):
    while a and a[-1] == 0:
        a.pop()
    return a


def padd(a, b):
    p = PM[0]
    n = max(len(a), len(b))
    return trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p for i in range(n)])


def psub(a, b):
    p = PM[0]
    n = max(len(a), len(b))
    return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p for i in range(n)])


def pneg(a):
    p = PM[0]
    return [(-c) % p for c in a]


def pmul(a, b):
    if not a or not b:
        return []
    p = PM[0]
    CNT[0] += len(a) * len(b)
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] += x * y
    return trim([c % p for c in r])


def pscale(a, c):
    CNT[0] += len(a)
    p = PM[0]
    return trim([x * c % p for x in a])


def pdivmod(a, b):
    p = PM[0]
    a = list(a)
    db = len(b) - 1
    if db < 0:
        raise ZeroDivisionError
    if b[-1] != 1:
        inv = pow(b[-1], -1, p)
        CNT[1] += 1
    else:
        inv = 1
    q = [0] * max(0, len(a) - db)
    while len(a) - 1 >= db and a:
        c = a[-1] * inv % p
        CNT[0] += 1 + len(b)
        shift = len(a) - 1 - db
        q[shift] = c
        if c:
            for i, y in enumerate(b):
                a[shift + i] = (a[shift + i] - c * y) % p
        a.pop()
        trim(a)
    return trim(q), a


def pmonic(a):
    if not a or a[-1] == 1:
        return a
    inv = pow(a[-1], -1, PM[0])
    CNT[1] += 1
    return pscale(a, inv)


def pxgcd(a, b):
    """Return (g monic, s, t) with s a + t b = g."""
    r0, r1 = list(a), list(b)
    s0, s1 = [1], []
    t0, t1 = [], [1]
    while r1:
        q, r = pdivmod(r0, r1)
        r0, r1 = r1, r
        s0, s1 = s1, psub(s0, pmul(q, s1))
        t0, t1 = t1, psub(t0, pmul(q, t1))
    if r0 and r0[-1] != 1:
        inv = pow(r0[-1], -1, PM[0])
        CNT[1] += 1
        r0, s0, t0 = pscale(r0, inv), pscale(s0, inv), pscale(t0, inv)
    return r0, s0, t0


def pdiv_exact(a, b):
    q, r = pdivmod(a, b)
    assert not r, "inexact division"
    return q


# ---------------------------------------------------------------- Jacobian of C: y^2 = F(x)
class Jac:
    def __init__(self, F, p):
        self.F = F
        self.p = p

    def add(self, D1, D2):
        PM[0] = self.p
        if D1 is None:
            return D2
        if D2 is None:
            return D1
        F = self.F
        u1, v1 = D1
        u2, v2 = D2
        d1, e1, e2 = pxgcd(u1, u2)
        d, c1, c2 = pxgcd(d1, padd(v1, v2))
        s1, s2, s3 = pmul(c1, e1), pmul(c1, e2), c2
        u = pdiv_exact(pmul(u1, u2), pmul(d, d)) if len(d) > 1 else pmul(u1, u2)
        num = padd(padd(pmul(pmul(s1, u1), v2), pmul(pmul(s2, u2), v1)),
                   pmul(s3, padd(pmul(v1, v2), F)))
        v = pdiv_exact(num, d) if len(d) > 1 else num
        if len(u) == 1:
            return None
        v = pdivmod(v, u)[1]
        if len(u) == 3:
            return (u, v)
        if len(u) != 5:
            raise Exceptional("unexpected composition degree")
        un = pdiv_exact(psub(F, pmul(v, v)), u)
        if len(un) != 3:
            raise Exceptional("reduction left deg != 2 (divisor meets infinity)")
        un = pmonic(un)
        vn = pdivmod(pneg(v), un)[1]
        return (un, vn)

    def neg(self, D):
        if D is None:
            return None
        PM[0] = self.p
        return (D[0], pdivmod(pneg(D[1]), D[0])[1])

    def mul(self, k, D):
        R = None
        for bit in bin(k)[2:]:
            R = self.add(R, R)
            if bit == "1":
                R = self.add(R, D)
        return R


def enc(D):
    return None if D is None else [list(D[0]), list(D[1])]


def pullback(x0, y0, p):
    """phi^*((x0,y0) - inf) = (X^2 - x0, y0)."""
    return ([(-x0) % p, 0, 1], trim([y0 % p]))


def random_divisor(Jc, p, F, rng):
    """Random affine degree-2 divisor class from two points with distinct x."""
    PM[0] = p
    while True:
        pts = []
        while len(pts) < 2:
            x = rng.randrange(p)
            v = polyval(F, x, p)
            if v and is_qr(v, p) and all(x != q[0] for q in pts):
                y = sqrt_mod(v, p)
                if rng.random() < 0.5:
                    y = p - y
                pts.append((x, y))
        (x1, y1), (x2, y2) = pts
        u = [x1 * x2 % p, (-(x1 + x2)) % p, 1]
        inv = pow((x2 - x1) % p, -1, p)
        slope = (y2 - y1) * inv % p
        v = trim([(y1 - slope * x1) % p, slope])
        return (u, v)


def polyval(poly, x, p):
    r = 0
    for c in reversed(poly):
        r = (r * x + c) % p
    return r


# ---------------------------------------------------------------- Pollard rho on E
def rho(P, Q, l, a, p, k_true, rng):
    ops = 0
    mults = []
    for _ in range(20):
        m, n = rng.randrange(1, l), rng.randrange(1, l)
        mults.append((m, n, ec_add(ec_mul(m, P, a, p), ec_mul(n, Q, a, p), a, p)))
    max_iter = 30 * math.isqrt(l) + 1000

    def step(st):
        X, ca, cb = st
        j = X[0] % 20 if X is not None else 0
        m, n, M = mults[j]
        return (ec_add(X, M, a, p), (ca + m) % l, (cb + n) % l)

    for restart in range(200):
        a0, b0 = rng.randrange(l), rng.randrange(l)
        X0 = ec_add(ec_mul(a0, P, a, p), ec_mul(b0, Q, a, p), a, p)
        t = h = (X0, a0, b0)
        for _ in range(max_iter):
            t = step(t)
            h = step(step(h))
            ops += 3
            if t[0] == h[0]:
                db = (t[2] - h[2]) % l
                if db == 0:
                    break
                k = (h[1] - t[1]) * pow(db, -1, l) % l
                ok = ec_mul(k, P, a, p) == Q
                return {"ops": ops, "restarts": restart, "k": k, "recovered": bool(ok and k == k_true)}
    return {"ops": ops, "restarts": 200, "k": None, "recovered": False}


# ---------------------------------------------------------------- linear algebra mod l
def solve_k(relations, S, l, P, Q, a, p, k_true):
    ncol = len(S) + 1  # factor-base columns plus e = [inf+ - inf-]
    idx = {x: i for i, x in enumerate(S)}
    rows = []
    skipped = 0
    for (r, s, x1, s1, x2, s2) in relations:
        if x1 in S0_ZERO[0] or x2 in S0_ZERO[0]:
            skipped += 1
            continue
        row = [0] * ncol
        for x, sg in ((x1, s1), (x2, s2)):
            if sg > 0:
                row[idx[x]] += 1
            else:
                row[idx[x]] -= 1
                row[len(S)] -= 1
        row[len(S)] += 1
        row = [c % l for c in row[:ncol]] + [r % l, s % l]
        rows.append(row)
    n = len(rows)
    piv_row = 0
    for col in range(ncol):
        sel = None
        for i in range(piv_row, n):
            if rows[i][col]:
                sel = i
                break
        if sel is None:
            continue
        rows[piv_row], rows[sel] = rows[sel], rows[piv_row]
        inv = pow(rows[piv_row][col], -1, l)
        rows[piv_row] = [c * inv % l for c in rows[piv_row]]
        pr = rows[piv_row]
        for i in range(piv_row + 1, n):
            c = rows[i][col]
            if c:
                rows[i] = [(x - c * y) % l for x, y in zip(rows[i], pr)]
        piv_row += 1
    kernel = rows[piv_row:]
    cands, verified, wrong, rec_k = 0, 0, 0, None
    for row in kernel:
        assert not any(row[:ncol])
        rr, ss = row[ncol], row[ncol + 1]
        if ss % l == 0:
            continue
        cands += 1
        k = (-rr) * pow(ss, -1, l) % l
        if ec_mul(k, P, a, p) == Q:
            verified += 1
            rec_k = k if rec_k is None else rec_k
            if k != k_true:
                wrong += 1
        else:
            wrong += 1
    return {"usable_rows": n, "skipped_two_torsion_rows": skipped, "rank": piv_row,
            "kernel_dim": len(kernel), "candidates": cands, "verified": verified, "wrong": wrong, "recovered_k": rec_k,
            "recovered_k_matches": bool(verified > 0 and wrong == 0)}


S0_ZERO = [set()]   # x in S with F(x) == 0 (2-torsion), set per cell


# ---------------------------------------------------------------- cell
def choose_curve(p, rng):
    tried = 0
    while True:
        tried += 1
        a, b = rng.randrange(p), rng.randrange(p)
        if b == 0 or (4 * a ** 3 + 27 * b ** 2) % p == 0:
            continue
        nE = count_points(p, a, b)
        fac = factor_small(nE)
        cands = [q for q, e in fac.items() if q % 2 == 1 and q >= 64 and q != p and e == 1]
        if not cands:
            continue
        l = max(cands)
        nE2 = count_points_twist_quartic(p, a, b)
        if nE2 % l == 0:
            continue
        return a, b, nE, nE2, l, tried


def run_cell(p, arm, meta, seed, cidx, args):
    t0 = time.time()
    rng = random.Random(f"{EXP_ID}:{seed}:{arm}:{p}:{cidx}")
    PM[0] = p
    cell = {"p": p, "arm": arm, "prime_meta": meta, "seed": seed, "curve_index": cidx,
            "p_bits": p.bit_length()}
    exc_setup = 0
    while True:
        a, b, nE, nE2, l, tried = choose_curve(p, rng)
        Pt = None
        while Pt is None:
            R0 = random_point(p, a, b, rng)
            Pt = ec_mul(nE // l, R0, a, p)
        k = rng.randrange(1, l)
        Q = ec_mul(k, Pt, a, p)
        F = trim([b, 0, a, 0, 0, 0, 1])
        Jc = Jac(F, p)
        try:
            A = pullback(Pt[0], Pt[1], p)
            B = pullback(Q[0], Q[1], p)
            # CTRL-PULLBACK
            lA = Jc.mul(l, A)
            ctrl_pullback = bool(lA is None and A is not None and A[0] != [1])
            # CTRL-HOMOMORPHISM on random pairs
            homo_ok, homo_n = True, 0
            for _ in range(5):
                i, j = rng.randrange(1, l), rng.randrange(1, l)
                P1, P2 = ec_mul(i, Pt, a, p), ec_mul(j, Pt, a, p)
                P3 = ec_add(P1, P2, a, p)
                lhs = Jc.add(pullback(P1[0], P1[1], p), pullback(P2[0], P2[1], p))
                rhs = None if P3 is None else pullback(P3[0], P3[1], p)
                homo_n += 1
                if lhs != rhs:
                    homo_ok = False
            # cofactor-part multipliers  M_j = m A + n B + [l] W
            def cof():
                W = random_divisor(Jc, p, F, rng)
                return Jc.mul(l, W)
            mult = []
            for _ in range(20):
                m, n = rng.randrange(l), rng.randrange(l)
                M = Jc.add(Jc.add(Jc.mul(m, A), Jc.mul(n, B)), cof())
                mult.append((m, n, M))
            r0, s0 = rng.randrange(l), rng.randrange(l)
            R = Jc.add(Jc.add(Jc.mul(r0, A), Jc.mul(s0, B)), cof())
            break
        except Exceptional:
            exc_setup += 1
            if exc_setup > 50:
                raise
    cell.update({"a": a, "b": b, "order_E": nE, "order_E2": nE2, "l": l, "k": k, "P": list(Pt),
                 "Q": list(Q), "curve_resamples_exceptional_setup": exc_setup,
                 "ctrl_pullback": ctrl_pullback, "ctrl_homomorphism": homo_ok,
                 "ctrl_homomorphism_pairs": homo_n})
    # factor base
    target = math.isqrt(p - 1) + 1
    S, ysm, two_tors = [], {}, set()
    x = 0
    while len(S) < target and x < p:
        v = polyval(F, x, p)
        if is_qr(v, p):
            y = sqrt_mod(v, p)
            y = min(y, p - y)
            S.append(x)
            ysm[x] = y
            if v == 0:
                two_tors.add(x)
        x += 1
    Sset = set(S)
    S0_ZERO[0] = two_tors
    nS = len(S)
    need = nS + 10
    inv2 = pow(2, -1, p)
    pw = p.bit_length() + bin((p - 1) // 2).count("1")
    CNT[0] = CNT[1] = 0
    r, s = r0, s0
    tests = decs = exc_steps = id_hits = 0
    relations = []
    rec = []
    last_j = None
    while len(relations) < need and tests < args.test_budget:
        try:
            if R is None:
                id_hits += 1
                tests += 1
                j = rng.randrange(20)
                m, n, M = mult[j]
                R = M
                r, s = (r + m) % l, (s + n) % l
                last_j = j
                continue
            u, v = R
            tests += 1
            u0, u1 = u[0], u[1]
            CNT[0] += 2
            disc = (u1 * u1 - 4 * u0) % p
            roots = None
            if disc == 0:
                roots = ((-u1) * inv2 % p,) * 2
            else:
                CNT[0] += pw
                if pow(disc, (p - 1) // 2, p) == 1:
                    CNT[0] += 2 * pw
                    sq = sqrt_mod(disc, p)
                    roots = ((-u1 + sq) * inv2 % p, (-u1 - sq) * inv2 % p)
            if roots is not None and roots[0] in Sset and roots[1] in Sset:
                decs += 1
                sg = []
                for xr in roots:
                    yv = polyval(v, xr, p)
                    sg.append(1 if yv == ysm[xr] else -1)
                    assert yv == ysm[xr] or yv == (p - ysm[xr]) % p, "decomposition off the curve"
                relations.append((r, s, roots[0], sg[0], roots[1], sg[1]))
                try:
                    Tc = Jc.add(R, Jc.neg(Jc.add(Jc.mul(r, A), Jc.mul(s, B))))
                    T_rec, T_ok = enc(Tc), True
                except Exceptional:
                    T_rec, T_ok = None, False
                rec.append({"test_index": tests, "r": r, "s": s, "R": enc(R), "T": T_rec,
                            "T_computed": T_ok, "multiplier_index": last_j,
                            "roots": [roots[0], roots[1]], "signs": [sg[0], sg[1]]})
            j = rng.randrange(20)
            m, n, M = mult[j]
            Rn = Jc.add(R, M)
            R = Rn
            r, s = (r + m) % l, (s + n) % l
            last_j = j
        except Exceptional:
            exc_steps += 1
            j = rng.randrange(20)
            # re-seed the walk position deterministically after an exceptional addition
            m, n, M = mult[j]
            try:
                R = Jc.add(R, M)
                r, s = (r + m) % l, (s + n) % l
            except Exceptional:
                R, r, s, last_j = A, 1, 0, None   # restart the walk at A (recorded in exceptional_steps)
    fp_mults, fp_inv = CNT[0], CNT[1]
    prob = decs / tests if tests else 0.0
    pred_old = (nS / p) ** 2 / 2
    pred = 2 * (nS / p) ** 2
    reached = len(relations) >= need
    if reached:
        cost = tests
    elif relations:
        cost = tests * need / len(relations)
    else:
        cost = float(tests) * need   # censored lower bound: zero relations
    cell.update({"factor_base_size": nS, "relations_target": need, "tests": tests,
                 "decompositions": decs, "relations": len(relations), "relation_records": rec,
                 "factor_base_x": S, "A": enc(A), "B": enc(B),
                 "multipliers": [{"j": jj, "r": m_, "s": n_, "M": enc(M_)} for jj, (m_, n_, M_) in enumerate(mult)],
                 "R_start": {"r": r0, "s": s0},
                 "relation_target_reached": reached,
                 "decomposition_probability": prob, "predicted_probability": pred, "predicted_probability_old": pred_old,
                 "fp_mults": fp_mults, "fp_inversions": fp_inv,
                 "fp_mults_per_test": fp_mults / tests if tests else None,
                 "fp_inversions_per_test": fp_inv / tests if tests else None,
                 "exceptional_steps": exc_steps, "identity_hits": id_hits,
                 "cost_tests_to_target": cost, "cost_censored_zero_relations": (not reached and not relations),
                 "cost_extrapolated": (not reached),
                 "two_torsion_in_base": len(two_tors)})
    # linear algebra
    if reached and p.bit_length() <= args.la_max_bits:
        la = solve_k(relations, S, l, Pt, Q, a, p, k)
        cell["linear_algebra"] = la
        ic_ok = la["recovered_k_matches"]
    else:
        cell["linear_algebra"] = None
        ic_ok = None
    # rho
    rr = rho(Pt, Q, l, a, p, k, random.Random(f"{EXP_ID}:rho:{seed}:{arm}:{p}:{cidx}"))
    cell["rho_ops"] = rr["ops"]
    cell["rho"] = rr
    cell["recovered_k_matches"] = {"ic": ic_ok, "rho": rr["recovered"]}
    return cell, time.time() - t0


# ---------------------------------------------------------------- aggregate
def lsq_slope(pts):
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in pts) / sxx


def aggregate(cells):
    out = {"per_arm": {}}
    for arm in ("special", "random"):
        cs = [c for c in cells if c["arm"] == arm]
        sizes = sorted({c["p_bits"] for c in cs})
        ic_pts = [(math.log(c["p"]), math.log(c["cost_tests_to_target"])) for c in cs if c["cost_tests_to_target"] > 0]
        rho_pts = [(math.log(c["p"]), math.log(c["rho_ops"])) for c in cs if c["rho_ops"] > 0]
        ok = len(sizes) >= 3
        out["per_arm"][arm] = {
            "sizes_completed": sizes, "cells": len(cs),
            "relation_cost_exponent": lsq_slope(ic_pts) if ok and ic_pts else None,
            "rho_cost_exponent": lsq_slope(rho_pts) if ok and rho_pts else None,
            "fit_points": len(ic_pts),
            "fit_uses_extrapolated_cells": sum(1 for c in cs if c["cost_extrapolated"]),
            "fit_cells_with_zero_relations": sum(1 for c in cs if c["cost_censored_zero_relations"]),
            "mean_decomposition_probability_by_bits": {
                str(bt): (sum(c["decompositions"] for c in cs if c["p_bits"] == bt)
                          / max(1, sum(c["tests"] for c in cs if c["p_bits"] == bt))) for bt in sizes},
            "mean_predicted_probability_old_by_bits": {
                str(bt): (sum(c["predicted_probability_old"] for c in cs if c["p_bits"] == bt)
                          / max(1, sum(1 for c in cs if c["p_bits"] == bt))) for bt in sizes},
            "mean_predicted_probability_by_bits": {
                str(bt): (sum(c["predicted_probability"] for c in cs if c["p_bits"] == bt)
                          / max(1, sum(1 for c in cs if c["p_bits"] == bt))) for bt in sizes},
        }
    if cells:
        top = max(cells, key=lambda c: c["decomposition_probability"])
        out["highest_probability_cell"] = {
            "p": top["p"], "arm": top["arm"], "seed": top["seed"], "curve_index": top["curve_index"],
            "decomposition_probability": top["decomposition_probability"],
            "predicted_probability": top["predicted_probability"],
            "predicted_probability_old": top["predicted_probability_old"],
            "S_over_p_squared": (top["factor_base_size"] / top["p"]) ** 2}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p-bits", type=int, nargs="+", default=[10, 12, 14, 16])
    ap.add_argument("--d", type=int, nargs="+", default=[2, 3])
    ap.add_argument("--primes-per-cell", type=int, default=3)
    ap.add_argument("--curves", type=int, default=3)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--test-budget", type=int, default=2000000)
    ap.add_argument("--la-max-bits", type=int, default=16)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()
    raw = {"experiment_id": EXP_ID, "hypothesis_id": "H-ECDLP-bd1572",
           "parameters": {"p_bits": args.p_bits, "d": args.d, "primes_per_cell": args.primes_per_cell,
                          "curves": args.curves, "seeds": args.seeds, "test_budget": args.test_budget,
                          "la_max_bits": args.la_max_bits},
           "cells": []}
    walls = []
    for seed in args.seeds:
        for bits in args.p_bits:
            for d in args.d:
                for i, sp in enumerate(primeset.special_primes(d, bits, args.primes_per_cell)):
                    rp = primeset.matched_random_prime(bits, seed, f"d{d}:{i}")
                    for arm, pr in (("special", sp), ("random", rp)):
                        p = pr["p"]
                        if p <= 3 or p % 2 == 0:
                            continue
                        for cidx in range(args.curves):
                            cell, wall = run_cell(p, arm, pr, seed, cidx, args)
                            cell["d"] = d
                            raw["cells"].append(cell)
                            walls.append({"p": p, "arm": arm, "seed": seed, "curve_index": cidx,
                                          "wall_seconds": wall})
                            print(f"{arm} p={p} seed={seed} c={cidx} l={cell['l']} tests={cell['tests']} "
                                  f"rel={cell['relations']}/{cell['relations_target']} "
                                  f"prob={cell['decomposition_probability']:.3g} "
                                  f"pred={cell['predicted_probability']:.3g} rho={cell['rho_ops']} "
                                  f"{wall:.1f}s", file=sys.stderr, flush=True)
    raw["aggregate"] = aggregate(raw["cells"])
    raw_path = os.path.join(args.out, "raw-result.json")
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=1, sort_keys=True, default=str)
    src = os.path.abspath(__file__)
    sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest()  # noqa: E731
    manifest = {"experiment_id": EXP_ID, "command": " ".join(sys.argv),
                "python": platform.python_version(), "platform": platform.platform(),
                "source_sha256": {"run.py": sha(src),
                                  "primeset.py": sha(os.path.join(os.path.dirname(src), "primeset.py"))},
                "raw_result_sha256": sha(raw_path),
                "started_unix": started, "finished_unix": time.time(),
                "total_wall_seconds": time.time() - started, "cell_wall_seconds": walls,
                "asserts_nothing_about": "the hypothesis; observations only"}
    try:
        manifest["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True,
                                                         stderr=subprocess.DEVNULL,
                                                         cwd=os.path.dirname(src)).strip()
    except Exception:  # noqa: BLE001
        manifest["git_commit"] = None
    with open(os.path.join(args.out, "manifest.yaml"), "w", encoding="utf-8") as fh:
        for kk, vv in manifest.items():
            fh.write(f"{kk}: {json.dumps(vv)}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent Boolean/squarefree Macaulay meter for TASK-20260904-ed0e8f
(red team).  Written from the definitions in the task card's
review_plan.blind_rederivation.quantity; it does NOT import
harness/macaulay_fp and shares no code with the producer's run script.

Ring B = F_p[a_0..a_{n-1}]/(a_i^2 - a_i).  A monomial is an int bitmask; the
product of two monomials is the bitwise OR (a^2 = a).  A polynomial is a dict
{mask: coeff mod p}, coeff != 0.

PER-LAYER convention (the contract's): for degree D and a generator g of
squarefree degree delta, the rows are {mu * g : popcount(mu) = D - delta}.
full_rank(D)  = rank over F_p of those rows on all 2^n monomials,
top_rank(D)   = rank of the same rows restricted to the columns of popcount D,
fall_dim(D)   = full_rank(D) - top_rank(D),
d_ff          = least D with fall_dim(D) > 0.
"""
from itertools import combinations


# ---------------------------------------------------------------- polynomials
def pmul(f, g, p):
    out = {}
    for m1, c1 in f.items():
        for m2, c2 in g.items():
            m = m1 | m2
            v = (out.get(m, 0) + c1 * c2) % p
            if v:
                out[m] = v
            elif m in out:
                del out[m]
    return out


def padd(f, g, p):
    out = dict(f)
    for m, c in g.items():
        v = (out.get(m, 0) + c) % p
        if v:
            out[m] = v
        elif m in out:
            del out[m]
    return out


def pscal(f, c, p):
    c %= p
    if c == 0:
        return {}
    return {m: (v * c) % p for m, v in f.items()}


def ppow(f, k, p):
    r = {0: 1}
    for _ in range(k):
        r = pmul(r, f, p)
    return r


def deg(f):
    return max((bin(m).count("1") for m in f), default=-1)


def top_part(f):
    d = deg(f)
    return {m: c for m, c in f.items() if bin(m).count("1") == d}


def homog_part(f, d):
    return {m: c for m, c in f.items() if bin(m).count("1") == d}


# ---------------------------------------------------------------- linear algebra
def rank_mod_p(rows, p):
    """rows: list of dicts {col: coeff}.  Exact Gaussian elimination mod p."""
    pivots = {}          # col -> reduced row (normalised, leading coeff 1)
    rank = 0
    for r in rows:
        r = {c: v % p for c, v in r.items() if v % p}
        while r:
            col = min(r)
            if col in pivots:
                f = r[col]
                pr = pivots[col]
                for c, v in pr.items():
                    nv = (r.get(c, 0) - f * v) % p
                    if nv:
                        r[c] = nv
                    elif c in r:
                        del r[c]
            else:
                inv = pow(r[col], p - 2, p)
                pivots[col] = {c: (v * inv) % p for c, v in r.items()}
                rank += 1
                break
    return rank


# ---------------------------------------------------------------- Macaulay
def monomials_of_degree(n, d):
    for combo in combinations(range(n), d):
        m = 0
        for i in combo:
            m |= 1 << i
        yield m


def layer_profile(gen, n, p, D_max, delta=None, stop_at_first_fall=False):
    """Returns list of (D, rows, full_rank, top_rank, fall_dim)."""
    if delta is None:
        delta = deg(gen)
    out = []
    for D in range(delta, D_max + 1):
        k = D - delta
        if k > n:
            break
        rows_full = []
        rows_top = []
        for mu in monomials_of_degree(n, k):
            r = pmul({mu: 1}, gen, p)
            rows_full.append(r)
            rows_top.append({m: c for m, c in r.items() if bin(m).count("1") == D})
        fr = rank_mod_p(rows_full, p)
        tr = rank_mod_p(rows_top, p)
        out.append((D, len(rows_full), fr, tr, fr - tr))
        if stop_at_first_fall and fr - tr > 0:
            break
    return out


def first_fall(profile):
    for (D, rows, fr, tr, fd) in profile:
        if fd > 0:
            return D, fd
    return None, None


# ---------------------------------------------------------------- Semaev
def S3(x1, x2, x3, a, b, p):
    """S_3 evaluated with x1, x2, x3 polynomials in B (dicts) and a, b in F_p.
    S_3 = (x1-x2)^2 x3^2 - 2((x1+x2)(x1 x2 + a) + 2b) x3 + (x1 x2 - a)^2
          - 4 b (x1 + x2)."""
    one = {0: 1}
    diff = padd(x1, pscal(x2, -1, p), p)
    t1 = pmul(pmul(diff, diff, p), pmul(x3, x3, p), p)
    x1x2 = pmul(x1, x2, p)
    s = padd(x1, x2, p)
    inner = padd(pmul(s, padd(x1x2, pscal(one, a, p), p), p), pscal(one, 2 * b, p), p)
    t2 = pscal(pmul(inner, x3, p), -2, p)
    d3 = padd(x1x2, pscal(one, -a, p), p)
    t3 = pmul(d3, d3, p)
    t4 = pscal(s, -4 * b, p)
    return padd(padd(t1, t2, p), padd(t3, t4, p), p)


def digit_forms(m, s, p):
    """ell_k = sum_i 2^i a_{k,i}; variable index of a_{k,i} is k*s + i."""
    ells = []
    for k in range(m):
        f = {}
        for i in range(s):
            f[1 << (k * s + i)] = pow(2, i, p)
        ells.append(f)
    return ells

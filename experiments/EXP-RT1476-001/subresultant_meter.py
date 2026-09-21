#!/usr/bin/env python3
"""EXP-RT1476-001 -- subresultant backward-state meter for the serial-S3 2|3 split of S5.

MEASUREMENT MODULE.  It computes numbers and writes them to raw-result.json.

ANTI-TAUTOLOGY DISCIPLINE (specification.yaml,
metrics.metric_isolation_rule_anti_tautology, binding):
  * this module contains no pre-registered threshold, no expected value, no
    answer key and no pass/fail verdict;
  * nothing in the measuring path branches on an expected outcome;
  * every quantity that any gate is evaluated on is written into
    raw-result.json, so the comparison can be, and is, performed elsewhere
    (experiments/EXP-RT1476-001/analysis.md, and independently by the
    Validator task TASK-20260728-003 from the raw files alone).

The module measures, per (arm, p, seed) cell:
  backward_state_support_size, deg_u_backward_eliminant, ops_success/ops_all
  (instrumented GF(p) operation counters), prs_step_count, success_rate,
  forward_state_size, coefficient/root diagnostics, and wall clock.

Nothing here interprets anything.  See implementation_notes.md for the exact
algebraic chain, the arithmetic layer, and every implementation choice the
specification did not fix.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from math import isqrt

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import sympy  # noqa: E402  (setup / verification path only -- never in the counted path)

from harness.toycurve import EllipticCurve, ECDLPInstance, _seed_int  # noqa: E402
from harness.semaev import (  # noqa: E402
    s3_eval,
    build_factor_base,
    verify_decomposition_certificate,
)

MODULE_VERSION = "1.0.0"
EXPERIMENT_ID = "EXP-RT1476-001"


# ---------------------------------------------------------------------------
# 1.  Deterministic randomness
# ---------------------------------------------------------------------------

def det_bytes(seed: int, tag: str, nbytes: int) -> bytes:
    out = b""
    ctr = 0
    while len(out) < nbytes:
        out += hashlib.sha256(f"{seed}:{tag}:{ctr}".encode()).digest()
        ctr += 1
    return out[:nbytes]


def det_int(seed: int, tag: str) -> int:
    return int.from_bytes(det_bytes(seed, tag, 32), "big")


# ---------------------------------------------------------------------------
# 2.  Instrumented GF(p) arithmetic layer
#
# Every counter increment below corresponds to an operation the interpreter
# actually executed on this call; none is an estimate, an extrapolation or a
# timing proxy.  Multiplications, additions/subtractions and inversions are
# counted separately.  The combined figure reported as
# `total_unit_weighted` gives every operation weight 1; the three counters are
# always reported separately so any other weighting can be applied afterwards
# from the raw record.
# ---------------------------------------------------------------------------

class FieldOps:
    __slots__ = ("p", "mul", "add", "inv")

    def __init__(self, p: int):
        self.p = p
        self.mul = 0
        self.add = 0
        self.inv = 0

    def reset(self) -> None:
        self.mul = 0
        self.add = 0
        self.inv = 0

    def snapshot(self) -> dict:
        return {
            "mul": self.mul,
            "add": self.add,
            "inv": self.inv,
            "total_unit_weighted": self.mul + self.add + self.inv,
        }


def _trim(f: list) -> list:
    while f and f[-1] == 0:
        f.pop()
    return f


# Polynomials over GF(p): little-endian coefficient lists, [] is the zero
# polynomial, no trailing zeros.

def padd(F: FieldOps, f, g):
    if len(f) < len(g):
        f, g = g, f
    p = F.p
    r = list(f)
    for i, gi in enumerate(g):
        r[i] = (r[i] + gi) % p
    F.add += len(g)
    return _trim(r)


def psub(F: FieldOps, f, g):
    p = F.p
    r = list(f)
    if len(g) > len(r):
        r.extend([0] * (len(g) - len(r)))
    for i, gi in enumerate(g):
        r[i] = (r[i] - gi) % p
    F.add += len(g)
    return _trim(r)


def pneg(F: FieldOps, f):
    p = F.p
    F.add += len(f)
    return [(-x) % p for x in f]


def pmul(F: FieldOps, f, g):
    if not f or not g:
        return []
    p = F.p
    r = [0] * (len(f) + len(g) - 1)
    n = 0
    for i, fi in enumerate(f):
        if fi == 0:
            continue
        for j, gj in enumerate(g):
            if gj == 0:
                continue
            r[i + j] = (r[i + j] + fi * gj) % p
            n += 1
    F.mul += n
    F.add += n
    return _trim(r)


def pscal(F: FieldOps, c: int, f):
    c %= F.p
    if c == 0 or not f:
        return []
    p = F.p
    F.mul += len(f)
    return _trim([(c * x) % p for x in f])


def pdivmod(F: FieldOps, f, g):
    """Long division in GF(p)[x]: returns (quotient, remainder)."""
    if not g:
        raise ZeroDivisionError("division by the zero polynomial")
    dg = len(g) - 1
    if len(f) - 1 < dg:
        return [], list(f)
    p = F.p
    inv_lc = pow(g[-1], -1, p)
    F.inv += 1
    r = list(f)
    q = [0] * (len(f) - dg)
    mul = 0
    add = 0
    for i in range(len(f) - 1, dg - 1, -1):
        ri = r[i]
        if ri == 0:
            continue
        c = (ri * inv_lc) % p
        mul += 1
        q[i - dg] = c
        base = i - dg
        for j in range(dg + 1):
            gj = g[j]
            if gj == 0:
                continue
            r[base + j] = (r[base + j] - c * gj) % p
            mul += 1
            add += 1
    F.mul += mul
    F.add += add
    return _trim(q), _trim(r[:dg])


class InexactDivision(Exception):
    pass


def pexactdiv(F: FieldOps, f, g):
    q, r = pdivmod(F, f, g)
    if r:
        raise InexactDivision("exact division failed")
    return q


def peval(F: FieldOps, f, x: int) -> int:
    if not f:
        return 0
    p = F.p
    acc = f[-1]
    n = len(f) - 1
    for i in range(len(f) - 2, -1, -1):
        acc = (acc * x + f[i]) % p
    F.mul += n
    F.add += n
    return acc


def ppow(F: FieldOps, f, e: int):
    r = [1]
    b = list(f)
    while e > 0:
        if e & 1:
            r = pmul(F, r, b)
        e >>= 1
        if e:
            b = pmul(F, b, b)
    return r


def pmonic(F: FieldOps, f):
    if not f:
        return []
    if f[-1] == 1:
        return list(f)
    return pscal(F, pow(f[-1], -1, F.p), f)


def pgcd(F: FieldOps, f, g):
    f = list(f)
    g = list(g)
    while g:
        _, r = pdivmod(F, f, g)
        f, g = g, r
    return pmonic(F, f)


def ppowmod(F: FieldOps, base, e: int, mod):
    r = [1]
    b = pdivmod(F, base, mod)[1]
    while e > 0:
        if e & 1:
            r = pdivmod(F, pmul(F, r, b), mod)[1]
        e >>= 1
        if e:
            b = pdivmod(F, pmul(F, b, b), mod)[1]
    return r


# ---------------------------------------------------------------------------
# 3.  Resultants: fraction-free (Bareiss) elimination on the Sylvester matrix
#
# Bareiss one-step fraction-free Gaussian elimination on the Sylvester matrix
# is the matrix form of the subresultant algorithm: its intermediate entries
# are the subresultants and every division it performs is exact in the
# coefficient domain.  The polynomial-remainder-sequence form is implemented
# separately below and used to record prs_step_count.
# ---------------------------------------------------------------------------

def sylvester(A, B):
    """A, B: lists (indexed by the eliminated variable's degree) of GF(p)[t]
    polynomials.  Returns the Sylvester matrix over GF(p)[t]."""
    m = len(A) - 1
    n = len(B) - 1
    N = m + n
    M = [[[] for _ in range(N)] for _ in range(N)]
    for i in range(n):
        for k in range(m + 1):
            M[i][i + k] = list(A[m - k])
    for j in range(m):
        for k in range(n + 1):
            M[n + j][j + k] = list(B[n - k])
    return M


def _trim_coeffs(A):
    A = list(A)
    while A and not A[-1]:
        A.pop()
    return A


def bareiss_det(F: FieldOps, M):
    n = len(M)
    if n == 0:
        return [1]
    M = [list(row) for row in M]
    prev = [1]
    sign = 1
    for k in range(n - 1):
        if not M[k][k]:
            piv = None
            for r in range(k + 1, n):
                if M[r][k]:
                    piv = r
                    break
            if piv is None:
                return []
            M[k], M[piv] = M[piv], M[k]
            sign = -sign
        akk = M[k][k]
        for i in range(k + 1, n):
            aik = M[i][k]
            for j in range(k + 1, n):
                num = psub(F, pmul(F, M[i][j], akk), pmul(F, aik, M[k][j]))
                M[i][j] = pexactdiv(F, num, prev)
            M[i][k] = []
        prev = akk
    d = M[n - 1][n - 1]
    return d if sign == 1 else pneg(F, d)


def det_eval_interp(F: FieldOps, M):
    """Independent determinant over GF(p)[t] by evaluation + interpolation.

    Used as the fallback when fraction-free elimination hits a non-exact
    division, and as the independent cross-check of bareiss_det.
    """
    n = len(M)
    dmax = 0
    for row in M:
        dmax += max((len(e) - 1) for e in row) if any(row) else 0
    npts = dmax + 1
    p = F.p
    xs = list(range(npts))
    ys = []
    for x in xs:
        A = [[peval(F, M[i][j], x) for j in range(n)] for i in range(n)]
        ys.append(_num_det(F, A))
    return _lagrange(F, xs, ys)


def _num_det(F: FieldOps, A):
    n = len(A)
    p = F.p
    A = [row[:] for row in A]
    det = 1
    for k in range(n):
        piv = None
        for r in range(k, n):
            if A[r][k]:
                piv = r
                break
        if piv is None:
            return 0
        if piv != k:
            A[k], A[piv] = A[piv], A[k]
            det = (-det) % p
        inv = pow(A[k][k], -1, p)
        F.inv += 1
        det = det * A[k][k] % p
        F.mul += 1
        for r in range(k + 1, n):
            if not A[r][k]:
                continue
            f = A[r][k] * inv % p
            F.mul += 1
            for c in range(k, n):
                A[r][c] = (A[r][c] - f * A[k][c]) % p
            F.mul += n - k
            F.add += n - k
    return det % p


def _lagrange(F: FieldOps, xs, ys):
    p = F.p
    res = []
    for i, xi in enumerate(xs):
        num = [1]
        den = 1
        for j, xj in enumerate(xs):
            if i == j:
                continue
            num = pmul(F, num, [(-xj) % p, 1])
            den = den * ((xi - xj) % p) % p
            F.mul += 1
        c = ys[i] * pow(den, -1, p) % p
        F.inv += 1
        F.mul += 1
        res = padd(F, res, pscal(F, c, num))
    return _trim(res)


def resultant(F: FieldOps, A, B, stats: dict | None = None):
    """Res_x(A, B) where A, B are polynomials in the eliminated variable x with
    coefficients in GF(p)[t], given as coefficient lists indexed by deg_x."""
    A = _trim_coeffs(A)
    B = _trim_coeffs(B)
    if not A or not B:
        return []
    m = len(A) - 1
    n = len(B) - 1
    if m == 0 and n == 0:
        return [1]
    if m == 0:
        return ppow(F, A[0], n)
    if n == 0:
        return ppow(F, B[0], m)
    M = sylvester(A, B)
    try:
        return bareiss_det(F, M)
    except InexactDivision:
        if stats is not None:
            stats["bareiss_fallbacks"] = stats.get("bareiss_fallbacks", 0) + 1
        return det_eval_interp(F, M)


def prs_remainder_degrees(F: FieldOps, A, B):
    """Degree sequence of the subresultant polynomial remainder sequence of
    (A, B) over GF(p)[t], via pseudo-division (Brown/Collins variant).

    Only the DEGREE SEQUENCE is used (secondary metric prs_step_count); the
    resultant value itself is taken from the fraction-free elimination above.
    """
    A = _trim_coeffs(A)
    B = _trim_coeffs(B)
    if not A or not B:
        return []
    if len(A) < len(B):
        A, B = B, A
    degs = [len(A) - 1, len(B) - 1]
    R0, R1 = A, B
    guard = 0
    while len(R1) - 1 > 0 and guard < 64:
        guard += 1
        R2 = _pseudo_rem(F, R0, R1)
        R2 = _trim_coeffs(R2)
        if not R2:
            break
        degs.append(len(R2) - 1)
        R0, R1 = R1, R2
    return degs


def _pseudo_rem(F: FieldOps, A, B):
    """Pseudo-remainder of A by B in D[x], D = GF(p)[t]."""
    A = [list(c) for c in A]
    dB = len(B) - 1
    lcB = B[dB]
    while len(A) - 1 >= dB and _trim_coeffs(A):
        A = _trim_coeffs(A)
        if not A or len(A) - 1 < dB:
            break
        dA = len(A) - 1
        lcA = A[dA]
        newA = [pmul(F, c, lcB) for c in A]
        shift = dA - dB
        for i in range(dB + 1):
            newA[shift + i] = psub(F, newA[shift + i], pmul(F, lcA, B[i]))
        A = _trim_coeffs(newA)
        if not A:
            break
    return A


# ---------------------------------------------------------------------------
# 4.  Trivariate chain links
# ---------------------------------------------------------------------------

def s3_trivariate(a: int, b: int, p: int) -> dict:
    """Semaev S_3 as a monomial dict {(i,j,k): c} for X^i Y^j Z^k."""
    T: dict = {}

    def acc(mon, c):
        T[mon] = (T.get(mon, 0) + c) % p

    acc((2, 0, 2), 1)
    acc((1, 1, 2), -2)
    acc((0, 2, 2), 1)
    acc((2, 1, 1), -2)
    acc((1, 2, 1), -2)
    acc((1, 0, 1), -2 * a)
    acc((0, 1, 1), -2 * a)
    acc((0, 0, 1), -4 * b)
    acc((2, 2, 0), 1)
    acc((1, 1, 0), -2 * a)
    acc((0, 0, 0), a * a)
    acc((1, 0, 0), -4 * b)
    acc((0, 1, 0), -4 * b)
    return {k: v % p for k, v in T.items() if v % p}


def random_trivariate(seed: int, tag: str, p: int) -> dict:
    """Random dense trivariate over GF(p) with per-variable degree <= 2 and
    total degree <= 4 -- the per-variable degrees and the total degree of
    Semaev S_3 (specification controls.CTRL-NEG.concrete_construction)."""
    T = {}
    idx = 0
    for i in range(3):
        for j in range(3):
            for k in range(3):
                if i + j + k <= 4:
                    c = det_int(seed, f"{tag}.{idx}") % p
                    idx += 1
                    if c:
                        T[(i, j, k)] = c
    return T


def tri_subst_XY(T: dict, x: int, y: int, p: int) -> list:
    """Substitute X = x, Y = y; return the univariate in Z."""
    out = [0, 0, 0]
    for (i, j, k), c in T.items():
        out[k] = (out[k] + c * pow(x, i, p) * pow(y, j, p)) % p
    return _trim(out)


def tri_subst_YZ(T: dict, y: int, z: int, p: int) -> list:
    """Substitute Y = y, Z = z; return the univariate in X."""
    out = [0, 0, 0]
    for (i, j, k), c in T.items():
        out[i] = (out[i] + c * pow(y, j, p) * pow(z, k, p)) % p
    return _trim(out)


def tri_subst_Y_elim_Z(T: dict, y: int, p: int) -> list:
    """Substitute Y = y; return a list indexed by deg_Z of GF(p)[X] polys."""
    out = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for (i, j, k), c in T.items():
        out[k][i] = (out[k][i] + c * pow(y, j, p)) % p
    return _trim_coeffs([_trim(o) for o in out])


def tri_subst_Y_elim_X(T: dict, y: int, p: int) -> list:
    """Substitute Y = y; return a list indexed by deg_X of GF(p)[Z] polys."""
    out = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for (i, j, k), c in T.items():
        out[i][k] = (out[i][k] + c * pow(y, j, p)) % p
    return _trim_coeffs([_trim(o) for o in out])


# ---------------------------------------------------------------------------
# 5.  Square roots and quadratic roots in GF(p) (chain-propagation path)
# ---------------------------------------------------------------------------

def sqrt_mod(a: int, p: int):
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    # Tonelli-Shanks
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        bpow = pow(c, 1 << (m - i - 1), p)
        m, c = i, bpow * bpow % p
        t = t * c % p
        r = r * bpow % p
    return r


def poly_roots_deg_le2(f: list, p: int) -> list:
    """All roots in GF(p) of a polynomial of degree <= 2 (f=[] -> every element,
    reported as None meaning 'unconstrained')."""
    f = _trim(list(f))
    if not f:
        return None
    if len(f) == 1:
        return []
    if len(f) == 2:
        c0, c1 = f
        return [(-c0) * pow(c1, -1, p) % p]
    c0, c1, c2 = f
    disc = (c1 * c1 - 4 * c2 * c0) % p
    s = sqrt_mod(disc, p)
    if s is None:
        return []
    inv2c2 = pow(2 * c2 % p, -1, p)
    r1 = (-c1 + s) * inv2c2 % p
    r2 = (-c1 - s) * inv2c2 % p
    return [r1] if r1 == r2 else [r1, r2]


# ---------------------------------------------------------------------------
# 6.  Curve construction (direct; NOT via generate_instance)
# ---------------------------------------------------------------------------

def j_invariant(a: int, b: int, p: int) -> int:
    den = (4 * pow(a, 3, p) + 27 * b * b) % p
    return 1728 * 4 * pow(a, 3, p) % p * pow(den, -1, p) % p


def _first_point(E: EllipticCurve):
    for x in range(E.p):
        P = E.lift_x(x)
        if P is not None and P != (x, 0):
            return P
    return None


def curve_order_prime_bsgs(E: EllipticCurve):
    """Return n = #E(F_p) if it is prime, else None.

    BSGS on the Hasse interval: find t with (p+1-t)Q = O.  If n = p+1-t is
    prime and lies in the Hasse interval and nQ = O for Q != O, then
    ord(Q) = n divides #E, #E is in the Hasse interval and #E/n < 2, hence
    #E = n exactly.  So a prime value returned here is the group order and is
    certified prime-order by construction.
    """
    p = E.p
    Q = _first_point(E)
    if Q is None:
        return None
    bound = 2 * isqrt(p) + 1
    m = isqrt(2 * bound) + 1
    baby = {}
    acc = None
    for j in range(m + 1):
        baby.setdefault(acc, j)
        acc = E.add(acc, Q)
    A = E.mul(p + 1, Q)
    imax = bound // m + 2
    found = set()
    for i in range(-imax, imax + 1):
        T = E.add(A, E.mul(-i * m, Q))
        if T in baby:
            t = i * m + baby[T]
            if -bound <= t <= bound:
                found.add(t)
    for t in sorted(found):
        n = p + 1 - t
        if n <= 0:
            continue
        if abs(n - (p + 1)) > 2 * isqrt(p) + 1:
            continue
        if E.mul(n, Q) is not None:
            continue
        if sympy.isprime(n):
            return n
    return None


def sample_curve(p: int, seed: int, max_tries: int = 20000) -> dict:
    """Deterministic rejection sampling on the full curve predicate."""
    rejections = {}
    for t in range(1, max_tries + 1):
        a = det_int(seed, f"a{t}") % p
        b = det_int(seed, f"b{t}") % p
        if (4 * pow(a, 3, p) + 27 * b * b) % p == 0:
            rejections["singular"] = rejections.get("singular", 0) + 1
            continue
        E = EllipticCurve(p, a, b)
        j = j_invariant(a, b, p)
        if j == 0 or j == 1728 % p:
            rejections["j_in_0_1728"] = rejections.get("j_in_0_1728", 0) + 1
            continue
        n = curve_order_prime_bsgs(E)
        if n is None:
            rejections["order_not_prime"] = rejections.get("order_not_prime", 0) + 1
            continue
        if n == p:
            rejections["anomalous"] = rejections.get("anomalous", 0) + 1
            continue
        if n == p + 1:
            rejections["trace_zero_supersingular"] = rejections.get(
                "trace_zero_supersingular", 0) + 1
            continue
        P = _first_point(E)
        return {
            "p": p, "a": a, "b": b, "n": n, "j": j,
            "trace": p + 1 - n,
            "P": list(P),
            "candidate_index": t,
            "rejections": rejections,
            "rejected_total": sum(rejections.values()),
        }
    raise RuntimeError(f"no curve satisfying the predicate for p={p} seed={seed}")


def naive_order(E: EllipticCurve) -> int:
    p = E.p
    total = 1
    for x in range(p):
        rhs = (x * x * x + E.a * x + E.b) % p
        if rhs == 0:
            total += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            total += 2
    return total


DECOMPOSITION_ARITY = 5     # m = 5; the frozen sizing rule is L = round(q^(1/m))


def integer_fifth_root_rounded(n: int) -> int:
    """round(q^(1/5)) by exact integer comparison only.

    The exponent here is the decomposition arity m = 5 fixed by the frozen
    protocol's factor-base sizing rule.  It is a protocol parameter, not a
    threshold, an expected value or a verdict, and nothing is compared against
    it.  No floating point is used, so the value is exactly reproducible.
    """
    m = DECOMPOSITION_ARITY
    hi = 1
    while hi ** m <= n:
        hi *= 2
    lo = hi // 2
    while lo + 1 < hi:                      # largest k with k^m <= n
        mid = (lo + hi) // 2
        if mid ** m <= n:
            lo = mid
        else:
            hi = mid
    k = lo
    # round up iff q^(1/m) > k + 1/2, i.e. iff 2^m * n > (2k+1)^m
    return k + 1 if (2 ** m) * n > (2 * k + 1) ** m else k


# ---------------------------------------------------------------------------
# 7.  Factor bases and states
# ---------------------------------------------------------------------------

def factor_base_random(E: EllipticCurve, L: int, seed: int) -> list:
    inst = ECDLPInstance(E.p, E.a, E.b, None, None, 0, 0, E.p.bit_length(), seed)
    return build_factor_base(inst, L, seed)


def factor_base_planted(E: EllipticCurve, L: int, P) -> list:
    xs = []
    acc = None
    for i in range(1, L + 1):
        acc = E.add(acc, P)
        xs.append(acc[0])
    return xs


def forward_state_group_law(E: EllipticCurve, V: list) -> list:
    pts = [E.lift_x(v) for v in V]
    out = set()
    for i, A in enumerate(pts):
        for j in range(i, len(pts)):
            B = pts[j]
            for sB in (B, E.negate(B)):
                S = E.add(A, sB)
                if S is not None:
                    out.add(S[0])
    return sorted(out)


DEGENERATE = {"count": 0}


def _roots_or_skip(f, p):
    r = poly_roots_deg_le2(f, p)
    if r is None:                     # identically zero link: unconstrained
        DEGENERATE["count"] += 1
        return []
    return r


def forward_state_chain(link, V: list, p: int) -> list:
    out = set()
    for i, v1 in enumerate(V):
        for v2 in V[i:]:
            out.update(_roots_or_skip(tri_subst_XY(link, v1, v2, p), p))
    return sorted(out)


def backward_state_group_law(E: EllipticCurve, V: list, R):
    """Backward state by the group law, following the SAME chain order as the
    algebraic chain (x_R -> W2 -> W1 -> U), deduplicating on x-coordinates at
    every level.  Deduplicating on x is exact: an x-coordinate determines the
    point up to sign, and the sign of the intermediate point is absorbed by the
    free sign on the next factor-base point.  Paths through the point at
    infinity terminate, exactly as they do in the S_3 chain."""
    pts = [E.lift_x(v) for v in V]
    signed = []
    for Pt in pts:
        signed.append(Pt)
        signed.append(E.negate(Pt))

    def step(xs, first=False):
        out = set()
        for x in xs:
            W = R if first else E.lift_x(x)
            if W is None:
                continue
            for S in signed:
                T = E.add(W, S)
                if T is not None:
                    out.add(T[0])
        return out

    X2 = step([None], first=True)      # W2 level
    X1 = step(X2)                      # W1 level
    X0 = step(X1)                      # u level
    return X0, X1, X2


def backward_state_chain(links, V: list, xR: int, p: int, levels: int = 3):
    """Chain propagation x_R -> W2 -> W1 -> U through the three backward links.

    links = (link1, link2, link3) with
      link1(u, x3, w1), link2(w1, x4, w2), link3(w2, x5, x_R).

    levels=2 stops after W1 (used by the screening stage of the negative
    control, where a meet at the W1 level is equivalent to a meet at u).
    """
    link1, link2, link3 = links
    W2 = set()
    for v5 in V:
        W2.update(_roots_or_skip(tri_subst_YZ(link3, v5, xR, p), p))
    W1 = set()
    for v4 in V:
        for w2 in W2:
            W1.update(_roots_or_skip(tri_subst_YZ(link2, v4, w2, p), p))
    if levels < 3:
        return None, W1, W2
    U = set()
    for v3 in V:
        for w1 in W1:
            U.update(_roots_or_skip(tri_subst_YZ(link1, v3, w1, p), p))
    return U, W1, W2


def w1_forward_closure(link1, V: list, Fset, p: int):
    """{w1 : exists u in Fset, v3 in V with link1(u, v3, w1) = 0}."""
    out = set()
    for u in Fset:
        for v3 in V:
            out.update(_roots_or_skip(tri_subst_XY(link1, u, v3, p), p))
    return out


# ---------------------------------------------------------------------------
# 8.  Meet-in-the-middle certification (arms with a group law)
# ---------------------------------------------------------------------------

def build_sum_tables(E: EllipticCurve, V: list):
    pts = [E.lift_x(v) for v in V]
    signed = []
    for idx, Pt in enumerate(pts):
        signed.append((Pt, (V[idx], 1)))
        signed.append((E.negate(Pt), (V[idx], -1)))
    t2 = {}
    for i in range(len(signed)):
        Ai, di = signed[i]
        for j in range(i, len(signed)):
            Bj, dj = signed[j]
            S = E.add(Ai, Bj)
            t2.setdefault(S, (di, dj))
    t3 = {}
    for i in range(0, len(signed), 2):        # e3 = +1 representatives only
        Ai, di = signed[i]
        for j in range(len(signed)):
            Bj, dj = signed[j]
            Sij = E.add(Ai, Bj)
            for k in range(j, len(signed)):
                Ck, dk = signed[k]
                S = E.add(Sij, Ck)
                t3.setdefault(S, (di, dj, dk))
    return t2, t3


def mitm_query(E: EllipticCurve, t2, t3, R):
    """Return an explicit signed 5-tuple decomposition of R, or None."""
    for S2, d2 in t2.items():
        T = E.add(R, E.negate(S2)) if S2 is not None else R
        if T in t3:
            d3 = t3[T]
            return list(d2) + list(d3)
        Tn = E.negate(T)
        if Tn in t3:
            d3 = t3[Tn]
            return list(d2) + [(v, -e) for (v, e) in d3]
    return None


def materialise_certificate(E: EllipticCurve, R, tuples5):
    summands = []
    for (v, e) in tuples5:
        Pt = E.lift_x(v)
        summands.append(list(Pt if e == 1 else E.negate(Pt)))
    return {
        "kind": "decomposition",
        "statement": {
            "target": list(R),
            "summands": summands,
            "curve": {"p": E.p, "a": E.a, "b": E.b},
        },
    }


def independent_recheck(cert: dict) -> bool:
    """Second, independent re-verification of a decomposition certificate.

    Reimplements curve membership and the group law from modular arithmetic
    directly, without calling harness.toycurve, so that agreement between this
    and harness.semaev.verify_decomposition_certificate is agreement between
    two separate implementations.
    """
    st = cert["statement"]
    c = st["curve"]
    p, a, b = c["p"], c["a"], c["b"]

    def on_curve(pt):
        if pt is None:
            return True
        x, y = pt
        return (y * y - (x * x * x + a * x + b)) % p == 0

    def add(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 % p == x2 % p and (y1 + y2) % p == 0:
            return None
        if (x1 - x2) % p == 0 and (y1 - y2) % p == 0:
            lam = (3 * x1 * x1 + a) * pow(2 * y1 % p, -1, p) % p
        else:
            lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        return (x3, y3)

    acc = None
    for s in st["summands"]:
        pt = tuple(s)
        if not on_curve(pt):
            return False
        acc = add(acc, pt)
    tgt = tuple(st["target"])
    return acc is not None and (acc[0] - tgt[0]) % p == 0 and (acc[1] - tgt[1]) % p == 0


# ---------------------------------------------------------------------------
# 9.  The counted membership query
#
# Per target x_R and per factor-base triple (v3, v4, v5):
#   Q_{v4,v5}(w1) = Res_{w2}( link2(w1, v4, w2), link3(w2, v5, x_R) )
#   G_{v3,v4,v5}(u) = Res_{w1}( link1(u, v3, w1), Q_{v4,v5}(w1) )
# and the meet with the forward state is tested by evaluating G at every
# forward value.  deg_u of the backward eliminant B_R = prod G is the sum of
# the per-factor degrees.  All GF(p) arithmetic on this path goes through the
# instrumented layer of section 2.
# ---------------------------------------------------------------------------

def membership_query(F: FieldOps, links, V, xR, forward, p,
                     deadline=None, prs_sample=0):
    link1, link2, link3 = links
    stats = {"bareiss_fallbacks": 0}
    F.reset()
    t0 = time.perf_counter()

    link3_by_v5 = {}
    for v5 in V:
        link3_by_v5[v5] = tri_subst_YZ(link3, v5, xR, p)

    qcache = {}
    deg_sum = 0
    hits = []
    triples = 0
    prs_steps = 0
    prs_seqs = []
    timed_out = False
    zero_factor = 0

    for v3 in V:
        l1 = tri_subst_Y_elim_Z(link1, v3, p)     # list over deg_{w1}
        for v4 in V:
            l2 = tri_subst_Y_elim_Z(link2, v4, p)  # list over deg_{w2}
            for v5 in V:
                if deadline is not None and time.perf_counter() > deadline:
                    timed_out = True
                    break
                triples += 1
                key = (v4, v5)
                Q = qcache.get(key)
                if Q is None:
                    l3 = [[c] for c in link3_by_v5[v5]]
                    Q = resultant(F, l2, l3, stats)
                    qcache[key] = Q
                    if prs_sample and len(prs_seqs) < prs_sample:
                        prs_seqs.append(prs_remainder_degrees(F, l2, l3))
                if not Q:
                    zero_factor += 1
                    continue
                G = resultant(F, l1, [[c] for c in Q], stats)
                if not G:
                    zero_factor += 1
                    continue
                if prs_sample and len(prs_seqs) < prs_sample:
                    prs_seqs.append(prs_remainder_degrees(F, l1, [[c] for c in Q]))
                deg_sum += len(G) - 1
                for u0 in forward:
                    if peval(F, G, u0) == 0:
                        hits.append((u0, v3, v4, v5))
            if timed_out:
                break
        if timed_out:
            break

    for s in prs_seqs:
        prs_steps += max(0, len(s) - 1)

    return {
        "deg_u_backward_eliminant": deg_sum if not timed_out else None,
        "triples_processed": triples,
        "triples_total": len(V) ** 3,
        "zero_factors": zero_factor,
        "hits": len(hits),
        "hit_sample": [list(h) for h in hits[:8]],
        "distinct_hit_u": len(set(h[0] for h in hits)),
        "prs_step_count_sampled": prs_steps,
        "prs_degree_sequences_sampled": prs_seqs,
        "bareiss_fallbacks": stats["bareiss_fallbacks"],
        "ops": F.snapshot(),
        "seconds": time.perf_counter() - t0,
        "timed_out": timed_out,
    }


def eliminant_root_support(F: FieldOps, links, V, xR, p, deadline=None):
    """Number of distinct GF(p) roots of B_R = prod G, by union of per-factor
    root sets.  Used where no group law exists (negative control), and as an
    algebraic cross-check elsewhere."""
    link1, link2, link3 = links
    roots = set()
    qcache = {}
    for v3 in V:
        l1 = tri_subst_Y_elim_Z(link1, v3, p)
        for v4 in V:
            l2 = tri_subst_Y_elim_Z(link2, v4, p)
            for v5 in V:
                if deadline is not None and time.perf_counter() > deadline:
                    return None
                key = (v4, v5)
                Q = qcache.get(key)
                if Q is None:
                    l3 = [[c] for c in tri_subst_YZ(link3, v5, xR, p)]
                    Q = resultant(F, l2, l3)
                    qcache[key] = Q
                if not Q:
                    continue
                G = resultant(F, l1, [[c] for c in Q])
                if not G:
                    continue
                roots.update(poly_roots_in_fp(F, G, p))
    return roots


def poly_roots_in_fp(F: FieldOps, g, p):
    """All GF(p) roots of g (deg g small) via gcd(g, x^p - x) then splitting."""
    g = _trim(list(g))
    if len(g) <= 1:
        return []
    if len(g) - 1 <= 2:
        return poly_roots_deg_le2(g, p)
    xp = ppowmod(F, [0, 1], p, g)
    h = pgcd(F, psub(F, xp, [0, 1]), g)
    if len(h) <= 1:
        return []
    return _split_all(F, h, p, 0)


def _split_all(F, h, p, depth):
    h = pmonic(F, h)
    d = len(h) - 1
    if d == 0:
        return []
    if d <= 2:
        return poly_roots_deg_le2(h, p)
    if depth > 40:
        return [x for x in range(p) if peval(F, h, x) == 0] if p < 100000 else []
    for c in range(0, 64):
        t = ppowmod(F, [c, 1], (p - 1) // 2, h)
        g1 = pgcd(F, psub(F, t, [1]), h)
        if 0 < len(g1) - 1 < d:
            q = pexactdiv(F, h, g1)
            return _split_all(F, g1, p, depth + 1) + _split_all(F, q, p, depth + 1)
    return []


# ---------------------------------------------------------------------------
# 10.  Self-tests (verification code, deliberately independent of the solver)
# ---------------------------------------------------------------------------

def selftests(p: int = 1009, seed: int = 1) -> dict:
    out = {}
    F = FieldOps(p)

    # (a) the hard-coded S_3 monomial table against harness.semaev.s3_eval
    a, b = 5, 7
    T = s3_trivariate(a, b, p)
    ok = True
    for i in range(40):
        v1 = det_int(seed, f"t{i}.1") % p
        v2 = det_int(seed, f"t{i}.2") % p
        v3 = det_int(seed, f"t{i}.3") % p
        val = 0
        for (e1, e2, e3), c in T.items():
            val = (val + c * pow(v1, e1, p) * pow(v2, e2, p) * pow(v3, e3, p)) % p
        if val != s3_eval(a, b, v1, v2, v3, p):
            ok = False
            break
    out["s3_monomial_table_matches_harness_s3_eval"] = ok

    # (b) resultant against sympy.resultant on random inputs
    t, x = sympy.symbols("t x")
    agree = 0
    trials = 25
    for i in range(trials):
        dA = 2
        dB = 2 + (i % 3)
        A = [[det_int(seed, f"A{i}.{k}.{m}") % p for m in range(3)] for k in range(dA + 1)]
        B = [[det_int(seed, f"B{i}.{k}.{m}") % p for m in range(2)] for k in range(dB + 1)]
        A = [_trim(c) for c in A]
        B = [_trim(c) for c in B]
        A = _trim_coeffs(A)
        B = _trim_coeffs(B)
        if not A or not B:
            continue
        mine = resultant(F, A, B)
        As = sum(sum(cc * t ** m for m, cc in enumerate(c)) * x ** k for k, c in enumerate(A))
        Bs = sum(sum(cc * t ** m for m, cc in enumerate(c)) * x ** k for k, c in enumerate(B))
        ref = sympy.Poly(sympy.resultant(sympy.Poly(As, x), sympy.Poly(Bs, x)), t, modulus=p)
        refc = [int(v) % p for v in reversed(ref.all_coeffs())]
        refc = _trim(refc)
        if refc == mine:
            agree += 1
    out["resultant_vs_sympy_trials"] = trials
    out["resultant_vs_sympy_agreements"] = agree

    # (c) product-factorisation identity for the eliminant, at L = 3:
    #     Res_{x5}(S3(w2,x5,xR), f_V(x5)) == prod_{v in V} S3(w2, v, xR)
    a, b = 5, 7
    T = s3_trivariate(a, b, p)
    V = [11, 23, 37]
    xR = 101
    w2 = sympy.symbols("w2")
    x5 = sympy.symbols("x5")
    S3s = sum(c * w2 ** e1 * x5 ** e2 * xR ** e3 for (e1, e2, e3), c in T.items())
    fV = sympy.prod([(x5 - v) for v in V])
    lhs = sympy.Poly(sympy.resultant(sympy.Poly(S3s, x5), sympy.Poly(fV, x5)), w2,
                     modulus=p)
    rhs = sympy.Poly(sympy.prod([
        sum(c * w2 ** e1 * v ** e2 * xR ** e3 for (e1, e2, e3), c in T.items())
        for v in V]), w2, modulus=p)
    lc = [int(v) % p for v in reversed(lhs.all_coeffs())]
    rc = [int(v) % p for v in reversed(rhs.all_coeffs())]
    lc = _trim(lc)
    rc = _trim(rc)
    ratio = None
    if lc and rc and len(lc) == len(rc):
        inv = pow(rc[-1], -1, p)
        k = lc[-1] * inv % p
        ratio = k if all((rc[i] * k - lc[i]) % p == 0 for i in range(len(lc))) else None
    out["factorbase_elimination_identity_holds_up_to_constant"] = ratio is not None
    out["factorbase_elimination_identity_constant"] = ratio

    return out


# ---------------------------------------------------------------------------
# 11.  Per-run driver
# ---------------------------------------------------------------------------

def git_state(repo: str) -> dict:
    def run(args):
        return subprocess.run(args, cwd=repo, capture_output=True, text=True).stdout.strip()
    commit = run(["git", "rev-parse", "HEAD"])
    status = run(["git", "status", "--porcelain"])
    return {
        "commit": commit,
        "dirty": bool(status),
        "dirty_paths": [ln[3:] for ln in status.splitlines()][:80],
        "dirty_path_count": len(status.splitlines()),
    }


def environment_block() -> dict:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "sage_version": None,
        "dependencies": {
            "sympy": sympy.__version__,
            "numpy": _numpy_version(),
            "pyyaml": _yaml_version(),
        },
        "module_version": MODULE_VERSION,
    }


def _numpy_version():
    try:
        import numpy
        return numpy.__version__
    except Exception:
        return None


def _yaml_version():
    try:
        import yaml
        return yaml.__version__
    except Exception:
        return None


def run_cell(arm: str, p: int, seed: int, targets: int,
             max_succ: int, max_fail: int,
             query_timeout: float, cell_timeout: float,
             prs_sample: int, support_cross_check: int,
             out_dir: str, command: str, argv_list: list) -> dict:
    t_start = time.time()
    perf0 = time.perf_counter()
    stop_fired = []

    print(f"[cell] arm={arm} p={p} seed={seed} targets={targets}", flush=True)

    p_is_prime = bool(sympy.isprime(p))
    print(f"[check] p prime: {p_is_prime}", flush=True)
    if not p_is_prime:
        raise SystemExit(f"STOP: modulus {p} is not prime; substituting a modulus is forbidden")

    t0 = time.perf_counter()
    curve = sample_curve(p, seed)
    curve_seconds = time.perf_counter() - t0
    E = EllipticCurve(p, curve["a"], curve["b"])
    n = curve["n"]
    P = tuple(curve["P"])
    print(f"[curve] a={curve['a']} b={curve['b']} n={n} j={curve['j']} "
          f"rejected={curve['rejected_total']} ({curve_seconds:.2f}s)", flush=True)

    order_cross_check = None
    if p <= 70000:
        nc = naive_order(E)
        order_cross_check = {"method": "naive Legendre-symbol point count",
                             "value": nc, "agrees_with_bsgs": nc == n}
        print(f"[curve] naive order cross-check: {nc} agrees={nc == n}", flush=True)

    L = integer_fifth_root_rounded(n)
    print(f"[fb] L = round(q^(1/5)) = {L}", flush=True)

    if arm == "posctl":
        V = factor_base_planted(E, L, P)
        fb_kind = "planted: {x([i]P) : i = 1..L}"
    else:
        V = factor_base_random(E, L, seed)
        fb_kind = "harness.semaev.build_factor_base (deterministic on-curve x-coordinates)"
    V = sorted(set(V))
    print(f"[fb] |V| = {len(V)}", flush=True)

    if arm == "negctl":
        link0 = random_trivariate(seed, "neglink0", p)
        link1 = random_trivariate(seed, "neglink1", p)
        link2 = random_trivariate(seed, "neglink2", p)
        link3 = random_trivariate(seed, "neglink3", p)
        link_kind = "random dense trivariate over GF(p), per-variable degree <= 2, total degree <= 4"
        link_dump = {
            "forward": {f"{k}": v for k, v in link0.items()},
            "back1": {f"{k}": v for k, v in link1.items()},
            "back2": {f"{k}": v for k, v in link2.items()},
            "back3": {f"{k}": v for k, v in link3.items()},
        }
    else:
        S3 = s3_trivariate(curve["a"], curve["b"], p)
        link0 = link1 = link2 = link3 = S3
        link_kind = "Semaev S_3"
        link_dump = {"S3": {f"{k}": v for k, v in S3.items()}}
    links = (link1, link2, link3)

    F = FieldOps(p)

    t0 = time.perf_counter()
    if arm == "negctl":
        forward = forward_state_chain(link0, V, p)
        forward_method = "roots of the randomized forward link over V x V"
        forward_cross = None
    else:
        forward = forward_state_group_law(E, V)
        forward_method = "group law: {x(P1 +/- P2) : x(Pi) in V}"
        fchain = forward_state_chain(link0, V, p)
        forward_cross = {
            "method": "roots of S3(x1,x2,u) over V x V",
            "size": len(fchain) if fchain is not None else None,
            "agrees": (fchain is not None and set(fchain) == set(forward)),
        }
    forward_seconds = time.perf_counter() - t0
    print(f"[fwd] |F| = {len(forward)} ({forward_seconds:.2f}s) cross={forward_cross}",
          flush=True)

    # ---- Stage A: screening -------------------------------------------------
    t0 = time.perf_counter()
    scr_success = []
    scr_fail = []
    certificates = []
    cert_failures = 0
    screening_method = None

    if arm == "negctl":
        screening_method = ("algebraic meet: backward chain propagation from x_R to W1 "
                            "meets the forward closure of the forward state through link1 "
                            "(no group law exists, so no certificate exists)")
        w1fwd = w1_forward_closure(link1, V, forward, p)
        for i in range(targets):
            xR = det_int(seed, f"negtarget{i}") % p
            _, W1, _ = backward_state_chain(links, V, xR, p, levels=2)
            hit = bool(W1 & w1fwd) if W1 is not None else False
            (scr_success if hit else scr_fail).append({"index": i, "x_R": xR})
    else:
        screening_method = ("meet-in-the-middle over the signed 2-sum and 3-sum tables "
                            "of V, materialising an explicit signed 5-tuple")
        t2, t3 = build_sum_tables(E, V)
        print(f"[mitm] |T2|={len(t2)} |T3|={len(t3)} "
              f"({time.perf_counter() - t0:.2f}s)", flush=True)
        for i in range(targets):
            r = det_int(seed, f"target{i}") % (n - 1) + 1
            R = E.mul(r, P)
            if R is None:
                scr_fail.append({"index": i, "r": r, "x_R": None})
                continue
            tup = mitm_query(E, t2, t3, R)
            if tup is None:
                scr_fail.append({"index": i, "r": r, "x_R": R[0]})
            else:
                cert = materialise_certificate(E, R, tup)
                v1 = bool(verify_decomposition_certificate(cert))
                v2 = bool(independent_recheck(cert))
                if not (v1 and v2):
                    cert_failures += 1
                certificates.append({
                    "certificate_id": f"CERT-{arm}-p{p}-s{seed}-{i}",
                    "target_index": i,
                    "stage": "A_screening",
                    "kind": "decomposition",
                    "statement": cert["statement"],
                    "summand_x_signs": [[v, e] for (v, e) in tup],
                    "reverified_harness_semaev": v1,
                    "reverified_independent_reimplementation": v2,
                    "verified": bool(v1 and v2),
                })
                scr_success.append({"index": i, "r": r, "x_R": R[0]})
    screening_seconds = time.perf_counter() - t0
    print(f"[screen] certified_successes={len(scr_success)} failures={len(scr_fail)} "
          f"cert_failures={cert_failures} ({screening_seconds:.1f}s)", flush=True)

    # ---- Stage B: measurement ----------------------------------------------
    measured = []
    cell_deadline = perf0 + cell_timeout
    chosen_succ = scr_success[:max_succ]
    chosen_fail = scr_fail[:max_fail]
    plan = ([("success", s) for s in chosen_succ] + [("failure", s) for s in chosen_fail])

    for kind, tgt in plan:
        if time.perf_counter() > cell_deadline:
            stop_fired.append({"rule": "STOP-2", "at_target_index": tgt["index"],
                               "elapsed_seconds": time.perf_counter() - perf0,
                               "note": "cell wall clock exhausted; remaining targets not measured"})
            break
        xR = tgt["x_R"]
        if xR is None:
            continue
        rec = {"target_index": tgt["index"], "subset": kind, "x_R": xR,
               "r_scalar": tgt.get("r")}

        if arm == "negctl":
            U, W1, W2 = backward_state_chain(links, V, xR, p)
            rec["backward_state_support_size"] = len(U)
            rec["backward_state_support_method"] = (
                "algebraic chain propagation (no group law exists on this arm)")
            rec["backward_state_support_group_law"] = None
            rec["backward_state_support_chain_propagation"] = len(U)
            rec["backward_support_cross_check_agrees"] = None
            rec["intermediate_state_sizes"] = {"W2": len(W2), "W1": len(W1)}
        else:
            R = E.lift_x(xR)
            X0, X1, X2 = backward_state_group_law(E, V, R)
            rec["backward_state_support_size"] = len(X0)
            rec["backward_state_support_method"] = (
                "group law, chain-ordered enumeration x_R -> W2 -> W1 -> u")
            rec["backward_state_support_group_law"] = len(X0)
            rec["intermediate_state_sizes"] = {"W2": len(X2), "W1": len(X1)}
            if len([m for m in measured]) < support_cross_check:
                U, W1, W2 = backward_state_chain(links, V, xR, p)
                rec["backward_state_support_chain_propagation"] = len(U)
                rec["backward_support_cross_check_agrees"] = bool(
                    set(U) == set(X0) and set(W1) == set(X1) and set(W2) == set(X2))
            else:
                rec["backward_state_support_chain_propagation"] = None
                rec["backward_support_cross_check_agrees"] = None

        qdeadline = min(time.perf_counter() + query_timeout, cell_deadline)
        q = membership_query(F, links, V, xR, forward, p,
                             deadline=qdeadline, prs_sample=prs_sample)
        if q["timed_out"]:
            stop_fired.append({"rule": "STOP-1", "at_target_index": tgt["index"],
                               "elapsed_seconds": q["seconds"],
                               "note": "membership query / eliminant aborted on the "
                                       "per-eliminant wall clock; contributes no degree datum"})
        rec["query"] = q
        rec["meet_found"] = q["hits"] > 0
        rec["degenerate_link_substitutions"] = DEGENERATE["count"]
        measured.append(rec)
        print(f"[measure] idx={tgt['index']} {kind} support="
              f"{rec['backward_state_support_size']} deg_u="
              f"{q['deg_u_backward_eliminant']} ops="
              f"{q['ops']['total_unit_weighted']} hits={q['hits']} "
              f"({q['seconds']:.1f}s)", flush=True)

    # ---- aggregation (raw numbers only) ------------------------------------
    def _mean(vals):
        vals = [v for v in vals if v is not None]
        return (sum(vals) / len(vals)) if vals else None

    succ = [m for m in measured if m["subset"] == "success"]
    fail = [m for m in measured if m["subset"] == "failure"]
    allm = measured

    gate = {
        "q": n,
        "log_q": None,
        "L": len(V),
        "forward_state_size": len(forward),
        "targets_screened": targets,
        "certified_successes": len(scr_success),
        "screening_failures": len(scr_fail),
        "success_rate": (len(scr_success) / targets) if targets else None,
        "measured_success_count": len(succ),
        "measured_failure_count": len(fail),
        "backward_state_support_size_mean_success": _mean(
            [m["backward_state_support_size"] for m in succ]),
        "backward_state_support_size_mean_all": _mean(
            [m["backward_state_support_size"] for m in allm]),
        "backward_state_support_size_values_success": [
            m["backward_state_support_size"] for m in succ],
        "deg_u_backward_eliminant_mean_success": _mean(
            [m["query"]["deg_u_backward_eliminant"] for m in succ]),
        "deg_u_backward_eliminant_values_success": [
            m["query"]["deg_u_backward_eliminant"] for m in succ],
        "ops_success_mul": _mean([m["query"]["ops"]["mul"] for m in succ]),
        "ops_success_add": _mean([m["query"]["ops"]["add"] for m in succ]),
        "ops_success_inv": _mean([m["query"]["ops"]["inv"] for m in succ]),
        "ops_success_total_unit_weighted": _mean(
            [m["query"]["ops"]["total_unit_weighted"] for m in succ]),
        "ops_success_values": [m["query"]["ops"]["total_unit_weighted"] for m in succ],
        "ops_all_total_unit_weighted": _mean(
            [m["query"]["ops"]["total_unit_weighted"] for m in allm]),
        "ops_failure_total_unit_weighted": _mean(
            [m["query"]["ops"]["total_unit_weighted"] for m in fail]),
        "prs_step_count_sampled_mean": _mean(
            [m["query"]["prs_step_count_sampled"] for m in allm]),
        "ops_measured_from_instrumented_layer": True,
        "ops_null_reason": None,
    }
    import math
    gate["log_q"] = math.log(n)

    finished = time.time()
    ru = resource.getrusage(resource.RUSAGE_SELF)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "module_version": MODULE_VERSION,
        "arm": arm,
        "run_id": f"RUN-RT1476-{arm}-p{p}-s{seed}",
        "command": command,
        "argv": argv_list,
        "inputs": {
            "p": p, "seed": seed, "targets_screened": targets,
            "max_measured_successes": max_succ,
            "max_measured_failures": max_fail,
            "query_timeout_seconds": query_timeout,
            "cell_timeout_seconds": cell_timeout,
            "prs_sample_per_query": prs_sample,
            "support_cross_check_targets": support_cross_check,
        },
        "primality_check": {"p": p, "is_prime": p_is_prime, "method": "sympy.isprime"},
        "curve": {
            "p": p, "a": curve["a"], "b": curve["b"], "n": n, "q": n,
            "j_invariant": curve["j"], "trace": curve["trace"],
            "base_point_P": curve["P"],
            "predicate": {
                "prime_order": True,
                "ordinary_trace_nonzero_mod_p": (curve["trace"] % p) != 0,
                "non_anomalous_n_ne_p": n != p,
                "j_not_in_0_1728": True,
                "non_singular": True,
            },
            "rejected_candidates": curve["rejected_total"],
            "rejection_breakdown": curve["rejections"],
            "accepted_candidate_index": curve["candidate_index"],
            "order_method": "BSGS on the Hasse interval + primality certificate",
            "order_cross_check": order_cross_check,
            "sampling_seconds": curve_seconds,
        },
        "factor_base": {"L_rule": "round(q^(1/5))", "L": len(V), "V": V,
                        "construction": fb_kind},
        "links": {"kind": link_kind, "monomials": link_dump},
        "forward_state": {"size": len(forward), "method": forward_method,
                          "cross_check": forward_cross, "seconds": forward_seconds,
                          "values": forward if len(forward) <= 4096 else forward[:4096]},
        "screening": {
            "method": screening_method,
            "targets": targets,
            "certified_successes": len(scr_success),
            "failures": len(scr_fail),
            "success_rate": (len(scr_success) / targets) if targets else None,
            "certificates_written": len(certificates),
            "certificates_failing_reverification": cert_failures,
            "seconds": screening_seconds,
            "success_target_indices": [s["index"] for s in scr_success][:200],
        },
        "measured_targets": measured,
        "gate_values": gate,
        "stopping_rules_fired": stop_fired,
        "timing": {
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t_start)),
            "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(finished)),
            "wall_seconds": finished - t_start,
        },
        "resources": {
            "peak_rss_bytes": ru.ru_maxrss,
            "cpu_seconds": ru.ru_utime + ru.ru_stime,
        },
        "git": git_state(REPO),
        "environment": environment_block(),
    }
    return raw, certificates


# ---------------------------------------------------------------------------
# 12.  Summariser (raw files -> results_summary.json).  Slopes only; no
#      threshold, no verdict.
# ---------------------------------------------------------------------------

def fit_slopes(points):
    """points: list of (log_q, log_y).  Returns pooled least-squares slope and
    all pairwise slopes."""
    import math
    pts = [(x, y) for (x, y) in points if x is not None and y is not None]
    if len(pts) < 2:
        return {"pooled_slope": None, "pairwise": [], "n_points": len(pts)}
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    num = sum((x - mx) * (y - my) for x, y in pts)
    den = sum((x - mx) ** 2 for x, _ in pts)
    pooled = num / den if den else None
    pair = []
    for i in range(n):
        for j in range(i + 1, n):
            dx = pts[j][0] - pts[i][0]
            if dx:
                pair.append({"i": i, "j": j, "slope": (pts[j][1] - pts[i][1]) / dx})
    return {"pooled_slope": pooled, "pairwise": pair, "n_points": n}


def summarize(runs_dir: str, out_path: str):
    import math
    cells = []
    for name in sorted(os.listdir(runs_dir)):
        rp = os.path.join(runs_dir, name, "raw-result.json")
        if not os.path.isfile(rp):
            continue
        with open(rp) as fh:
            raw = json.load(fh)
        g = raw["gate_values"]
        cells.append({
            "run_id": raw["run_id"], "arm": raw["arm"],
            "p": raw["inputs"]["p"], "seed": raw["inputs"]["seed"],
            "q": g["q"], "log_q": g["log_q"], "L": g["L"],
            "forward_state_size": g["forward_state_size"],
            "success_rate": g["success_rate"],
            "certified_successes": g["certified_successes"],
            "targets_screened": g["targets_screened"],
            "measured_success_count": g["measured_success_count"],
            "measured_failure_count": g["measured_failure_count"],
            "backward_state_support_size_mean_success": g["backward_state_support_size_mean_success"],
            "backward_state_support_size_mean_all": g["backward_state_support_size_mean_all"],
            "deg_u_backward_eliminant_mean_success": g["deg_u_backward_eliminant_mean_success"],
            "ops_success_total_unit_weighted": g["ops_success_total_unit_weighted"],
            "ops_all_total_unit_weighted": g["ops_all_total_unit_weighted"],
            "ops_failure_total_unit_weighted": g["ops_failure_total_unit_weighted"],
            "ops_success_mul": g["ops_success_mul"],
            "ops_success_add": g["ops_success_add"],
            "ops_success_inv": g["ops_success_inv"],
            "ops_null_reason": g["ops_null_reason"],
            "prs_step_count_sampled_mean": g["prs_step_count_sampled_mean"],
            "stopping_rules_fired": [s["rule"] for s in raw["stopping_rules_fired"]],
            "certificates_failing_reverification":
                raw["screening"]["certificates_failing_reverification"],
            "wall_seconds": raw["timing"]["wall_seconds"],
        })

    def series(arm, key, agg="mean_over_seeds"):
        by_p = {}
        for c in cells:
            if c["arm"] != arm or c[key] is None:
                continue
            by_p.setdefault(c["p"], []).append((c["log_q"], c[key]))
        pts = []
        detail = []
        for p in sorted(by_p):
            vals = by_p[p]
            lq = sum(v[0] for v in vals) / len(vals)
            mv = sum(v[1] for v in vals) / len(vals)
            pts.append((lq, math.log(mv) if mv > 0 else None))
            detail.append({"p": p, "log_q": lq, "mean_value": mv,
                           "per_seed_values": [v[1] for v in vals]})
        return {"points": detail, "fit": fit_slopes(pts)}

    def per_seed_series(arm, key):
        by_seed = {}
        for c in cells:
            if c["arm"] != arm or c[key] is None or c[key] <= 0:
                continue
            by_seed.setdefault(c["seed"], []).append((c["log_q"], math.log(c[key])))
        return {str(s): fit_slopes(v) for s, v in sorted(by_seed.items())}

    nulls = []
    for c in cells:
        for k in ("backward_state_support_size_mean_success",
                  "deg_u_backward_eliminant_mean_success",
                  "ops_success_total_unit_weighted",
                  "ops_success_mul", "ops_success_add", "ops_success_inv"):
            if c[k] is None:
                nulls.append({
                    "run_id": c["run_id"], "field": k, "value": None,
                    "reason": (
                        f"the measured success subset of this cell is empty "
                        f"(measured_success_count = {c['measured_success_count']}, "
                        f"certified_successes in the cell = {c['certified_successes']} "
                        f"out of {c['targets_screened']} screened targets), so no mean "
                        f"over the certified-relation subset exists. Not a failure of "
                        f"the counter: ops_all is present for this cell."),
                })
    nulls.append({
        "run_id": "ALL", "field": "coefficient_profile",
        "value": None,
        "reason": (
            "the backward eliminant B_R is never materialised as a coefficient "
            "vector -- it is handled in its factored form prod_{(v3,v4,v5) in V^3} "
            "G(u) -- so its nonzero-coefficient count and density were not "
            "computed. At L = 28 the product would be a degree-175616 polynomial "
            "assembled from 21952 degree-8 factors, which is outside this budget. "
            "The per-coefficient bit ceiling ceil(log2 p) is 10, 16 and 24 at the "
            "three sizes; the Collins/Brown coefficient-growth check is vacuous "
            "over GF(p) and was already declared not_applicable_over_GF_p in the "
            "specification."),
    })
    nulls.append({
        "run_id": "ALL_NEGCTL", "field": "backward_state_support_group_law",
        "value": None,
        "reason": (
            "the negative control replaces the S_3 chain by random dense "
            "polynomials, so no group law exists on that arm and the backward "
            "state can only be measured by algebraic chain propagation. Declared "
            "in specification controls.CTRL-NEG.comparability_limit_declared."),
    })

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "module_version": MODULE_VERSION,
        "generated_from": "experiments/EXP-RT1476-001/runs/*/raw-result.json",
        "nulls_with_reasons": nulls,
        "note": ("Slopes only.  No threshold, expected value or verdict appears in this "
                 "file or in the module that produced it; the pre-registered comparisons "
                 "are made in analysis.md and independently by the Validator."),
        "cells": cells,
        "beta_deg_backward_state_support_success_subset": {
            arm: series(arm, "backward_state_support_size_mean_success")
            for arm in ("main", "posctl", "negctl")},
        "beta_deg_backward_state_support_all_targets": {
            arm: series(arm, "backward_state_support_size_mean_all")
            for arm in ("main", "posctl", "negctl")},
        "beta_deg_eliminant_degree": {
            arm: series(arm, "deg_u_backward_eliminant_mean_success")
            for arm in ("main", "posctl", "negctl")},
        "beta_ops_success": {
            arm: series(arm, "ops_success_total_unit_weighted")
            for arm in ("main", "posctl", "negctl")},
        "beta_ops_all": {
            arm: series(arm, "ops_all_total_unit_weighted")
            for arm in ("main", "posctl", "negctl")},
        "per_seed_beta_deg_support": {
            arm: per_seed_series(arm, "backward_state_support_size_mean_all")
            for arm in ("main", "posctl", "negctl")},
        "per_seed_beta_ops_success": {
            arm: per_seed_series(arm, "ops_success_total_unit_weighted")
            for arm in ("main", "posctl", "negctl")},
        "per_seed_beta_ops_all": {
            arm: per_seed_series(arm, "ops_all_total_unit_weighted")
            for arm in ("main", "posctl", "negctl")},
        "forward_state_size_series": {
            arm: series(arm, "forward_state_size") for arm in ("main", "posctl", "negctl")},
        "success_rate_series": {
            arm: series(arm, "success_rate") for arm in ("main", "posctl", "negctl")},
    }
    with open(out_path, "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=False)
    return summary


# ---------------------------------------------------------------------------
# 13.  CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arm", default="main", choices=["main", "posctl", "negctl"])
    ap.add_argument("--p", type=int)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--targets", type=int, default=1200)
    ap.add_argument("--max-measured-successes", type=int, default=8)
    ap.add_argument("--max-measured-failures", type=int, default=8)
    ap.add_argument("--query-timeout", type=float, default=900.0)
    ap.add_argument("--cell-timeout", type=float, default=1800.0)
    ap.add_argument("--prs-sample", type=int, default=4)
    ap.add_argument("--support-cross-check", type=int, default=2)
    ap.add_argument("--out", default=None, help="runs/ directory")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--summary-out", default=None)
    args = ap.parse_args(argv)

    if args.selftest:
        print(json.dumps(selftests(), indent=1))
        return 0

    if args.summarize:
        s = summarize(args.out, args.summary_out)
        print(json.dumps({"cells": len(s["cells"])}, indent=1))
        return 0

    if args.dry_run:
        print(json.dumps({
            "arm": args.arm, "p": args.p, "seed": args.seed,
            "targets": args.targets, "out": args.out,
            "would_measure_successes": args.max_measured_successes,
            "would_measure_failures": args.max_measured_failures,
            "selftests": selftests(),
        }, indent=1))
        return 0

    command = "python3 " + " ".join(
        [os.path.relpath(os.path.abspath(__file__), REPO)] + list(sys.argv[1:]))
    raw, certs = run_cell(
        args.arm, args.p, args.seed, args.targets,
        args.max_measured_successes, args.max_measured_failures,
        args.query_timeout, args.cell_timeout, args.prs_sample,
        args.support_cross_check, args.out, command, list(sys.argv[1:]))

    run_id = raw["run_id"]
    rd = os.path.join(args.out, run_id)
    os.makedirs(rd, exist_ok=True)
    with open(os.path.join(rd, "raw-result.json"), "w") as fh:
        json.dump(raw, fh, indent=1, sort_keys=False)
    with open(os.path.join(rd, "certificates.json"), "w") as fh:
        json.dump({
            "run_id": run_id,
            "experiment_id": EXPERIMENT_ID,
            "arm": raw["arm"],
            "certificate_kind": "decomposition" if raw["arm"] != "negctl" else "none",
            "certificate_kind_note": (
                "none: the negative control replaces the S_3 chain by random dense "
                "polynomials, so there is no group law and no relation to certify. Its "
                "'success' predicate is root-existence in the forward state, which is a "
                "different predicate from the main arm's and is declared as such."),
            "count": len(certs),
            "failing_reverification": sum(1 for c in certs if not c["verified"]),
            "verifiers": [
                "harness.semaev.verify_decomposition_certificate",
                "subresultant_meter.independent_recheck (separate reimplementation "
                "of curve membership and the group law)",
            ],
            "certificates": certs,
        }, fh, indent=1)
    print(f"[done] wrote {rd}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

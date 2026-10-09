"""pilot_lib.py -- PILOT (m3closure), exploratory, hypothesis-generating only.

Instance construction for chained S_3 (m = 3, t = 3) Weil descents with
subgroup targets, reusing the vendored in-repo builder (vendor/boolsys.py,
EXP-SEMBIN-7e1371 copy) for S_3, the descent and the variable layout, and the
vendored CERTBIN field/curve code (vendor/gf2n.py, vendor/curve.py) for point
counting and the group law.

Variable layout (boolsys.generate, t = 3): u[0..n-1] (u = sum u_j alpha^j),
x1[0..k-1], x2[0..k-1], x3[0..k-1] (x_i = sum_j bit * basis[j]).
System: S_3(u, x1, x2) = 0 (n Boolean equations), S_3(u, x3, z) = 0 (n), z = x(R).
"""
from __future__ import annotations

import ctypes
import random
import sys
from array import array
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
import boolsys  # noqa: E402
from gf2n import Field  # noqa: E402
from curve import Curve, is_prime  # noqa: E402

_aff = ctypes.CDLL(str(HERE / "libcountaffu.so"))
_aff.count_affu.restype = ctypes.c_longlong
_aff.count_affu.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
                           ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int,
                           ctypes.c_void_p, ctypes.c_long, ctypes.POINTER(ctypes.c_long)]


# ----------------------------------------------------------------------------
# curve + targets
# ----------------------------------------------------------------------------

def pick_curve(n, seed, a=1, modulus=None):
    """Ordinary curve y^2 + xy = x^3 + a x^2 + b with #E = 2 q, q prime (a = 1,
    Tr(1) = 1 for odd n). b drawn by a seeded stream; first hit is taken."""
    if modulus is None:
        modulus, _ = boolsys.modulus_for(n)
    F = Field(n, modulus)
    rng = random.Random(boolsys.derive_seed("m3closure-curve", n, seed, a))
    tries = 0
    while True:
        tries += 1
        b = rng.randrange(2, 1 << n)
        E = Curve(F, a, b)
        N = E.count_points()
        h = 2 if (N % 2 == 0 and is_prime(N // 2)) else None
        if h:
            return {"F": F, "E": E, "a": a, "b": b, "order": N, "q": N // h, "h": h,
                    "modulus": modulus, "tries": tries}


def subgroup_targets(cv, count, seed):
    """x(R) for R = h * P, P a uniformly random affine point (lift of a random
    liftable x, random sign); R != O checked; q R = O checked."""
    F, E = cv["F"], cv["E"]
    rng = random.Random(boolsys.derive_seed("m3closure-targets", cv["F"].n, cv["b"], seed))
    out = []
    while len(out) < count:
        x = rng.randrange(1, 1 << F.n)
        P = E.lift_x(x)
        if P is None:
            continue
        if rng.randrange(2):
            P = E.neg(P)
        R = E.mul(cv["h"], P)
        if R is None:
            continue
        assert E.on_curve(R) and E.mul(cv["q"], R) is None
        out.append(R[0])
    return out


# ----------------------------------------------------------------------------
# systems
# ----------------------------------------------------------------------------

def build_chain3(n, k, basis, b, z, modulus):
    """Chained S_3, t = 3, built with boolsys's own s3/descend/linear_form."""
    F = boolsys.GF2n(n, modulus)
    N = n + 3 * k
    U = boolsys.linear_form([1 << j for j in range(n)], 0)
    X = [boolsys.linear_form(basis, n + i * k) for i in range(3)]
    zc = {0: z} if z else {}
    eqs = []
    eqs += boolsys.descend(boolsys.s3(F, U, X[0], X[1], b), n)
    eqs += boolsys.descend(boolsys.s3(F, U, X[2], zc, b), n)
    return {"N": N, "equations": eqs, "n": n, "k": k}


def build_m2(n, k, basis, b, z, modulus):
    """m = 2: S_3(x1, x2, z) = 0, x1, x2 in V (positive control)."""
    F = boolsys.GF2n(n, modulus)
    X = [boolsys.linear_form(basis, i * k) for i in range(2)]
    zc = {0: z} if z else {}
    eqs = boolsys.descend(boolsys.s3(F, X[0], X[1], zc, b), n)
    return {"N": 2 * k, "equations": eqs, "n": n, "k": k}


def support_null(system, seed):
    """Same monomial support per equation, i.i.d. uniform GF(2) coefficients."""
    rng = random.Random(boolsys.derive_seed("m3closure-null", seed))
    eqs = [[m for m in e if rng.randrange(2)] for e in system["equations"]]
    return {**system, "equations": eqs}


def eval_system(equations, mask):
    """Evaluate all equations at a Boolean point; returns list of values."""
    return [sum(1 for m in e if (m & mask) == m) & 1 for e in equations]


# ----------------------------------------------------------------------------
# satisfiability: (1) curve-level root solving, (2) Boolean system (affine in u)
# ----------------------------------------------------------------------------

class VSpace:
    def __init__(self, F, basis):
        k = len(basis)
        self.k = k
        elems = np.zeros(1 << k, dtype=np.int64)
        for c in range(1, 1 << k):
            low = c & -c
            j = low.bit_length() - 1
            elems[c] = elems[c ^ low] ^ basis[j]
        self.elems = elems
        self.coord = np.full(1 << F.n, -1, dtype=np.int64)
        self.coord[elems] = np.arange(1 << k)
        assert len(set(elems.tolist())) == 1 << k, "basis not independent"


def _solve_quadratic_vec(F, A, B, C):
    """Roots y of A y^2 + B y + C = 0 for arrays A, B, C (int64). Returns list of
    (index_array, root_array) pairs. The case A = B = C = 0 (every y) is
    reported separately as an index array."""
    out = []
    A, B, C = (np.asarray(v, dtype=np.int64) for v in (A, B, C))
    allidx = np.nonzero((A == 0) & (B == 0) & (C == 0))[0]
    # A = 0, B != 0: y = C / B
    i = np.nonzero((A == 0) & (B != 0))[0]
    if i.size:
        out.append((i, F.vmul(C[i], F.vinv(B[i]))))
    # A != 0, B = 0: y = sqrt(C / A); sqrt(v) = v^(2^(n-1))
    i = np.nonzero((A != 0) & (B == 0))[0]
    if i.size:
        v = F.vmul(C[i], F.vinv(A[i]))
        e = (1 << (F.n - 1)) % F.order
        lg = F.log_np[v]
        r = np.where(v == 0, 0, F.exp_np[(lg * e) % F.order])
        out.append((i, r))
    # A != 0, B != 0: y = (B/A) w, w^2 + w = A C / B^2
    i = np.nonzero((A != 0) & (B != 0))[0]
    if i.size:
        Bi = B[i]
        c = F.vmul(F.vmul(A[i], C[i]), F.vinv(F.vmul(Bi, Bi)))
        ok = F.vtrace(c) == 0
        i2, c2 = i[ok], c[ok]
        w = F.vhalftrace(c2)
        s = F.vmul(B[i2], F.vinv(A[i2]))
        y0 = F.vmul(s, w)
        y1 = F.vmul(s, w ^ 1)
        out.append((i2, y0))
        out.append((i2, y1))
    return out, allidx


def curve_solutions(F, V, b, z, cap=1 << 20):
    """All (u, x1, x2, x3) in F x V^3 with S_3(u,x3,z) = 0 and S_3(u,x1,x2) = 0,
    as Boolean masks in the boolsys layout. Root-solving, curve-level."""
    n, k = F.n, V.k
    sq = lambda v: F.vmul(v, v)
    x3 = V.elems
    zz = np.full(x3.shape, z, dtype=np.int64)
    # S_3(u, x3, z) in u: u^2 (x3+z)^2 + u x3 z + (x3 z)^2 + b
    A = sq(x3 ^ zz)
    Bq = F.vmul(x3, zz)
    C = sq(Bq) ^ b
    pairs, allidx = _solve_quadratic_vec(F, A, Bq, C)
    if allidx.size:
        raise RuntimeError("degenerate: S_3(u,x3,z) vanishes identically in u")
    ux3 = {}
    for idx, roots in pairs:
        for i, u in zip(idx.tolist(), roots.tolist()):
            ux3.setdefault(u, set()).add(i)   # set: guards double roots
    sols = []
    x1 = V.elems
    for u, x3set in ux3.items():
        uu = np.full(x1.shape, u, dtype=np.int64)
        A = sq(x1 ^ uu)
        Bq = F.vmul(x1, uu)
        C = sq(Bq) ^ b
        pairs, allidx = _solve_quadratic_vec(F, A, Bq, C)
        x12 = set()
        for idx, roots in pairs:
            c2 = V.coord[roots]
            good = c2 >= 0
            for i1, i2 in zip(idx[good].tolist(), c2[good].tolist()):
                x12.add((i1, i2))
        for i1 in allidx.tolist():
            for i2 in range(1 << k):
                x12.add((i1, i2))
        for (i1, i2) in x12:
            for i3 in x3set:
                sols.append(u | (i1 << n) | (i2 << (n + k)) | (i3 << (n + 2 * k)))
                if len(sols) > cap:
                    raise RuntimeError("solution cap")
    return sorted(set(sols))


def m2_solutions(F, V, b, z):
    """(x1, x2) in V^2 with S_3(x1, x2, z) = 0, masks x1 | x2 << k."""
    k = V.k
    x1 = V.elems
    zz = np.full(x1.shape, z, dtype=np.int64)
    sq = lambda v: F.vmul(v, v)
    A = sq(x1 ^ zz)
    Bq = F.vmul(x1, zz)
    C = sq(Bq) ^ b
    pairs, allidx = _solve_quadratic_vec(F, A, Bq, C)
    s = set()
    for idx, roots in pairs:
        c2 = V.coord[roots]
        good = c2 >= 0
        for i1, i2 in zip(idx[good].tolist(), c2[good].tolist()):
            s.add(i1 | (i2 << k))
    for i1 in allidx.tolist():
        for i2 in range(1 << k):
            s.add(i1 | (i2 << k))
    return sorted(s)


def boolean_count_chain3(system, sol_cap=4096):
    """Independent exhaustive count over the Boolean system (affine in u)."""
    n, k, N = system["n"], system["k"], system["N"]
    eqs = system["equations"]
    ptr = array("q", [0]); masks = array("Q")
    for e in eqs:
        masks.extend(e); ptr.append(len(masks))
    xa = (ctypes.c_int * (2 * k))(*range(n, n + 2 * k))
    xb = (ctypes.c_int * k)(*range(n + 2 * k, n + 3 * k))
    sol = (ctypes.c_uint64 * sol_cap)()
    ns = ctypes.c_long(0)
    pb = (ctypes.c_long * len(ptr)).from_buffer(ptr)
    mb = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks)
    tot = _aff.count_affu(N, n, len(eqs), ctypes.addressof(pb), ctypes.addressof(mb),
                          xa, 2 * k, xb, k, sol, sol_cap, ctypes.byref(ns))
    if tot < 0:
        raise RuntimeError("count_affu: structural violation")
    return int(tot), [int(sol[i]) for i in range(ns.value)]


def boolean_count_m2(system, sol_cap=4096):
    """m = 2: exhaustive over all 2^(2k) assignments via count_affu with no u."""
    N, eqs = system["N"], system["equations"]
    ptr = array("q", [0]); masks = array("Q")
    for e in eqs:
        masks.extend(e); ptr.append(len(masks))
    xa = (ctypes.c_int * N)(*range(N))
    xb = (ctypes.c_int * 1)(0)
    sol = (ctypes.c_uint64 * sol_cap)()
    ns = ctypes.c_long(0)
    pb = (ctypes.c_long * len(ptr)).from_buffer(ptr)
    mb = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks)
    tot = _aff.count_affu(N, 0, len(eqs), ctypes.addressof(pb), ctypes.addressof(mb),
                          xa, N, xb, 0, sol, sol_cap, ctypes.byref(ns))
    if tot < 0:
        raise RuntimeError("count_affu: structural violation")
    return int(tot), [int(sol[i]) for i in range(ns.value)]

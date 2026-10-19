"""pilot2_lib.py -- PILOT #2 (m45closure). EXPLORATORY, hypothesis-generating only.

Chained S_3 with general chain length t = m (m in {3,4,5}), x_i in V, u_i in
F_(2^n). Reuses pilot_lib (pilot #1) for the curve, targets, field arithmetic
and the quadratic root solver; the system is built with the vendored boolsys
primitives exactly as boolsys.generate does for general t.

Variable layout (boolsys.generate): u_0..u_{m-3} (n bits each), then x_0..x_{m-1}
(k bits each). Equations: S_3(u_0,x_0,x_1), S_3(u_{i-1},u_i,x_{i+1}) for
i=1..m-3, S_3(u_{m-3}, x_{m-1}, z).
"""
from __future__ import annotations

import ctypes
import random
import sys
from array import array
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pilot_lib as L  # noqa: E402
boolsys = L.boolsys

_cc = ctypes.CDLL(str(HERE / "libcountchain.so"))
_cc.count_chain.restype = ctypes.c_longlong
_cc.count_dense.restype = ctypes.c_longlong
_cc.count_dense.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long,
                            ctypes.POINTER(ctypes.c_long)]
_cc.count_chain.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long,
                            ctypes.POINTER(ctypes.c_long)]


def build_chain(n, k, m, basis, b, z, modulus):
    """Chained S_3 with t = m, boolsys primitives, boolsys.generate layout."""
    assert m >= 3
    F = boolsys.GF2n(n, modulus)
    N = (m - 2) * n + m * k
    U = [boolsys.linear_form([1 << j for j in range(n)], i * n) for i in range(m - 2)]
    X = [boolsys.linear_form(basis, (m - 2) * n + i * k) for i in range(m)]
    zc = {0: z} if z else {}
    polys = [boolsys.s3(F, U[0], X[0], X[1], b)]
    for i in range(1, m - 2):
        polys.append(boolsys.s3(F, U[i - 1], U[i], X[i + 1], b))
    polys.append(boolsys.s3(F, U[m - 3], X[m - 1], zc, b))
    eqs = []
    for p in polys:
        eqs += boolsys.descend(p, n)
    return {"N": N, "equations": eqs, "n": n, "k": k, "m": m}


def boolean_count_chain(system, sol_cap=4096):
    n, k, m, N = system["n"], system["k"], system["m"], system["N"]
    eqs = system["equations"]
    ptr = array("q", [0]); masks = array("Q")
    for e in eqs:
        masks.extend(e); ptr.append(len(masks))
    sol = (ctypes.c_uint64 * sol_cap)()
    ns = ctypes.c_long(0)
    pb = (ctypes.c_long * len(ptr)).from_buffer(ptr)
    mb = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks)
    tot = _cc.count_chain(N, n, m, k, len(eqs), ctypes.addressof(pb), ctypes.addressof(mb), sol, sol_cap, ctypes.byref(ns))
    if tot == -1:
        raise RuntimeError("count_chain: structural violation")
    if tot == -2:
        return 0, []
    return int(tot), sorted(int(sol[i]) for i in range(ns.value))


def chain_solutions(F, V, b, z, m, cap=1 << 22):
    """Curve-level (root-solving) enumeration of all (u_0..u_{m-3}, x_0..x_{m-1})
    in F^(m-2) x V^m satisfying the chain, as masks in the boolsys layout."""
    n, k = F.n, V.k
    sq = lambda v: F.vmul(v, v)
    xs = V.elems
    nV = 1 << k
    # stage 0: pairs (x0, x1) -> roots u0 of S_3(u0, x0, x1)
    i1 = np.repeat(np.arange(nV), nV); i2 = np.tile(np.arange(nV), nV)
    x1, x2 = xs[i1], xs[i2]
    A = sq(x1 ^ x2); Bq = F.vmul(x1, x2); C = sq(Bq) ^ b
    pairs, allidx = L._solve_quadratic_vec(F, A, Bq, C)
    if allidx.size:
        raise RuntimeError("degenerate stage 0")
    # partial: arrays u (current u), xidx (packed x coordinate indices as int)
    u_cur = []; xi_cur = []
    for idx, roots in pairs:
        u_cur.append(roots); xi_cur.append(i1[idx] | (i2[idx] << k))
    u_cur = np.concatenate(u_cur) if u_cur else np.zeros(0, dtype=np.int64)
    xi_cur = np.concatenate(xi_cur) if xi_cur else np.zeros(0, dtype=np.int64)
    # dedupe (double roots)
    packed = np.unique(xi_cur.astype(np.int64) * (1 << n) + u_cur)
    xi_cur, u_cur = packed // (1 << n), packed % (1 << n)
    ustack = [u_cur]      # u_0 values per partial
    for s in range(1, m - 2):
        # new x_{s+1}; roots u_s of S_3(u_{s-1}, u_s, x): u_s^2 (u_{s-1}+x)^2 + u_s u_{s-1} x + (u_{s-1} x)^2 + b
        P = len(u_cur)
        rep = np.repeat(np.arange(P), nV); ix = np.tile(np.arange(nV), P)
        up = u_cur[rep]; x = xs[ix]
        A = sq(up ^ x); Bq = F.vmul(up, x); C = sq(Bq) ^ b
        pairs, allidx = L._solve_quadratic_vec(F, A, Bq, C)
        if allidx.size:
            raise RuntimeError(f"degenerate stage {s}")
        sel = []; roots_all = []
        for idx, roots in pairs:
            sel.append(idx); roots_all.append(roots)
        sel = np.concatenate(sel) if sel else np.zeros(0, dtype=np.int64)
        roots_all = np.concatenate(roots_all) if roots_all else np.zeros(0, dtype=np.int64)
        # key for dedupe: (partial index, x index, root)
        key = (rep[sel].astype(np.int64) * nV + ix[sel]) * (1 << n) + roots_all
        key = np.unique(key)
        rr = key % (1 << n); rest = key // (1 << n); ixs = rest % nV; ps = rest // nV
        xi_cur = xi_cur[ps] | (ixs << ((s + 1) * k))
        ustack = [a[ps] for a in ustack] + [rr]
        u_cur = rr
        if len(u_cur) > cap:
            raise RuntimeError("partial cap")
    # final: S_3(u_{m-3}, x_{m-1}, z) == 0
    P = len(u_cur)
    rep = np.repeat(np.arange(P), nV); ix = np.tile(np.arange(nV), P)
    up = u_cur[rep]; x = xs[ix]
    zz = np.full(x.shape, z, dtype=np.int64)
    s3 = sq(F.vmul(up, x) ^ F.vmul(up, zz) ^ F.vmul(x, zz)) ^ F.vmul(F.vmul(up, x), zz) ^ b
    ok = np.nonzero(s3 == 0)[0]
    ps = rep[ok]; ixs = ix[ok]
    masks = np.zeros(len(ok), dtype=np.int64)
    for i, a in enumerate(ustack):
        masks |= a[ps] << (i * n)
    masks |= (xi_cur[ps] | (ixs << ((m - 1) * k))) << ((m - 2) * n)
    return sorted(set(masks.tolist()))


def point_check(cv, V, m, mask, z):
    """Curve-level semantic check of one solution: lift every x_j to a point,
    and look for signs with x(P_0+P_1) = u_0, x(P_0+..+P_{j+1}) = u_j, and
    x(P_0+..+P_{m-1}) = z. Returns True/False (False also when some x_j is not
    an x-coordinate)."""
    F, E = cv["F"], cv["E"]
    n, k = F.n, V.k
    us = [(mask >> (i * n)) & ((1 << n) - 1) for i in range(m - 2)]
    xidx = [(mask >> ((m - 2) * n + j * k)) & ((1 << k) - 1) for j in range(m)]
    xv = [int(V.elems[i]) for i in xidx]
    pts = []
    for x in xv:
        P = E.lift_x(x)
        if P is None:
            return False
        pts.append(P)
    for signs in range(1 << m):
        acc = None
        ok = True
        for j in range(m):
            Pj = pts[j] if not (signs >> j) & 1 else E.neg(pts[j])
            acc = Pj if acc is None else E.add(acc, Pj)
            if j >= 1:
                want = us[j - 1] if j - 1 < m - 2 else None
                if j == m - 1:
                    if acc is None or acc[0] != z:
                        ok = False; break
                else:
                    if acc is None or acc[0] != want:
                        ok = False; break
        if ok:
            return True
    return False


def support_null(system, seed):
    rng = random.Random(boolsys.derive_seed("m45closure-null", seed))
    eqs = [[mm for mm in e if rng.randrange(2)] for e in system["equations"]]
    return {**system, "equations": eqs}


def dense_null(system, seed_tag, draw):
    fake = {"N": system["N"], "equations": system["equations"], "seed": seed_tag, "draw": draw,
            "var_names": [f"v{j}" for j in range(system["N"])], "n": system["n"], "m": system["m"],
            "t": system["m"], "k": system["k"]}
    nl = boolsys.matched_null(fake, 1)
    return {**system, "equations": nl["equations"]}


def boolean_count_dense(system, sol_cap=4096):
    """Exhaustive over all 2^N assignments (no structure assumed). N <= 26 only."""
    N, eqs = system["N"], system["equations"]
    assert N <= 26
    ptr = array("q", [0]); masks = array("Q")
    for e in eqs:
        masks.extend(e); ptr.append(len(masks))
    sol = (ctypes.c_uint64 * sol_cap)()
    ns = ctypes.c_long(0)
    pb = (ctypes.c_long * len(ptr)).from_buffer(ptr)
    mb = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks)
    tot = _cc.count_dense(N, len(eqs), ctypes.addressof(pb), ctypes.addressof(mb), sol, sol_cap, ctypes.byref(ns))
    return int(tot), sorted(int(sol[i]) for i in range(ns.value))

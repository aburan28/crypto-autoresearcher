#!/usr/bin/env python3
"""Minimal, specification-literal checkers of TASK-20260926-f50294 (J7 CP-3).

Written by the comparator from the TEXT of
experiments/EXP-CERTBIN-060020/specification.yaml (object.field, curve,
factor_base_and_unknowns, summation_polynomial, descended_system, E_layout,
certificate_format FORMAT flat-v1 / wdag-v1 / ann-v1) and
experiments/EXP-CERTBIN-e94b27/specification.yaml object.mutant_closure_W_D,
BEFORE reading any code of TASK-20260926-f0736e, TASK-20260926-401771, impl/,
verifier/ or src/crypto_autoresearcher/. Imports only the Python standard
library and numpy. Imports no crypto_autoresearcher module.

Conventions (all from the text):
  * B = F_2[v_0..v_19]/(v_i^2 + v_i). A multilinear monomial is a 20-bit mask,
    bit i <-> v_i. A polynomial in B is a Python set of masks (XOR = symmetric
    difference). Multiplication by a monomial is mask OR, with parity
    cancellation (this IS the multilinear reduction).
  * F_{2^19} = F_2[t]/(t^19 + t^5 + t^2 + t + 1); element <-> 19-bit int,
    bit j = coefficient of t^j.
  * x_1 = sum_{j<10} v_j t^j, x_2 = sum_{j<10} v_{10+j} t^j, x_3 = x_R.
  * S_3 = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B; f_k = coefficient of t^k.
  * E_layout: column j = j-th monomial of mu_order(2, 20): degree ascending,
    then ascending sorted index tuple. E_hex row k, bit j (LSB first) = col j.
  * ann-v1 coordinate order: all multilinear monomials of degree <= 4 in
    v_0..v_19 sorted by (-degree, bitmask ascending); bitmask read as bit i
    <-> v_i (the natural reading of "bitmask"; this is a reading, recorded).
"""
from itertools import combinations

import numpy as np

NV = 20
NEQ = 19
N = 19
MOD = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1  # 524327
assert MOD == 524327


def popcount(x):
    return bin(x).count("1")


# ----------------------------------------------------------------- F_{2^19}
def gf_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> N:
            a ^= MOD
    return r


def gf_pow(a, e):
    r = 1
    while e:
        if e & 1:
            r = gf_mul(r, a)
        a = gf_mul(a, a)
        e >>= 1
    return r


def gf_inv(a):
    assert a != 0
    return gf_pow(a, (1 << N) - 2)


def gf_tr(a):
    s, x = 0, a
    for _ in range(N):
        s ^= x
        x = gf_mul(x, x)
    assert s in (0, 1)
    return s


# ------------------------------------------ polynomials over F_{2^19} in B
def fpoly_mul(p, q):
    out = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = m1 | m2
            v = out.get(m, 0) ^ gf_mul(c1, c2)
            if v:
                out[m] = v
            else:
                out.pop(m, None)
    return out


def fpoly_add(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            v = out.get(m, 0) ^ c
            if v:
                out[m] = v
            else:
                out.pop(m, None)
    return out


def descend_s3(x_r, b_coef):
    """Own S_3 descent: returns the 19 Boolean polynomials f_0..f_18 (sets of
    masks), plus a route-2 check (e^2 by Frobenius on coefficients)."""
    x1 = {1 << j: 1 << j for j in range(10)}
    x2 = {1 << (10 + j): 1 << j for j in range(10)}
    x3 = {0: x_r} if x_r else {}
    e = fpoly_add(fpoly_mul(x1, x2), fpoly_mul(x1, x3), fpoly_mul(x2, x3))
    e2 = fpoly_mul(e, e)
    e2_frob = {m: gf_mul(c, c) for m, c in e.items()}
    assert e2 == {m: c for m, c in e2_frob.items() if c}, "route-2 (Frobenius) mismatch"
    s = fpoly_add(e2, fpoly_mul(fpoly_mul(x1, x2), x3), {0: b_coef})
    fs = []
    for k in range(NEQ):
        fs.append({m for m, c in s.items() if (c >> k) & 1})
    return fs


# ------------------------------------------------------------- E_layout codec
def mu_order2():
    cols = [0]
    cols += [1 << i for i in range(NV)]
    cols += [(1 << i) | (1 << j) for i, j in combinations(range(NV), 2)]
    assert len(cols) == 211
    return cols


COLS2 = mu_order2()
COL2_INDEX = {m: c for c, m in enumerate(COLS2)}


def decode_ehex(ehex):
    assert len(ehex) == NEQ
    fs = []
    for h in ehex:
        x = int(h, 16)
        assert x >> 211 == 0
        fs.append({COLS2[c] for c in range(211) if (x >> c) & 1})
    return fs


def encode_ehex(fs):
    out = []
    for f in fs:
        x = 0
        for m in f:
            x |= 1 << COL2_INDEX[m]
        out.append(format(x, "x"))
    return out


def explicit_to_polys(equations):
    """blind-inputs.json explicit kind: 19 equations, each a list of monomials,
    each monomial an ascending list of variable indices ([] = 1)."""
    fs = []
    for eq in equations:
        f = set()
        for mono in eq:
            assert list(mono) == sorted(set(mono)) and all(0 <= i < NV for i in mono)
            m = 0
            for i in mono:
                m |= 1 << i
            f ^= {m}
        fs.append(f)
    assert len(fs) == NEQ
    return fs


# --------------------------------------------------------- Boolean ring ops
def mono_mul(poly, mu):
    out = set()
    for m in poly:
        x = m | mu
        if x in out:
            out.remove(x)
        else:
            out.add(x)
    return out


def deg(poly):
    return max((popcount(m) for m in poly), default=-1)  # deg 0 = -1 convention


def mask_of(idx_list):
    m = 0
    for i in idx_list:
        m |= 1 << i
    return m


# --------------------------------------------------------- wdag-v1 checker
def check_wdag(cert, fs, D=4, nv=NV, neq=NEQ):
    """Rules (a)-(e) of FORMAT wdag-v1, literally, degrees in B (i.e. after
    multilinear reduction). Returns (valid, first_violation, stats)."""
    stats = {}
    if cert.get("D") != D or cert.get("nv") != nv or cert.get("neq") != neq:
        return False, "header (D, nv, neq) != (%d, %d, %d)" % (D, nv, neq), stats
    nodes = cert["nodes"]
    ids = [nd["id"] for nd in nodes]
    if len(set(ids)) != len(ids):
        return False, "duplicate node id", stats
    by_id = {nd["id"]: nd for nd in nodes}
    polys = {}
    cache = {}
    max_mu = 0
    nrows = nprods = 0
    for i in sorted(by_id):
        nd = by_id[i]
        acc = set()
        for mu, k in nd.get("rows", []):
            if not isinstance(mu, list) or len(mu) > 2 or len(set(mu)) != len(mu) \
                    or any((not isinstance(v, int)) or v < 0 or v >= nv for v in mu):
                return False, "(b) node %d: bad mu %r" % (i, mu), stats
            if not isinstance(k, int) or k < 0 or k >= neq:
                return False, "(b) node %d: bad k %r" % (i, k), stats
            mm = mask_of(mu)
            key = (mm, k)
            if key not in cache:
                cache[key] = frozenset(mono_mul(fs[k], mm))
            acc ^= cache[key]
            max_mu = max(max_mu, len(mu))
            nrows += 1
        for j, c in nd.get("prods", []):
            if not isinstance(c, int) or c >= i or c not in polys:
                return False, "(a) node %d: child %r not < %d or absent" % (i, c, i), stats
            if not isinstance(j, int) or j < 0 or j >= nv:
                return False, "node %d: bad variable index j=%r" % (i, j), stats
            if deg(polys[c]) > D - 1:
                return False, "(c) node %d: child %d has deg %d > %d" % (i, c, deg(polys[c]), D - 1), stats
            acc ^= mono_mul(polys[c], 1 << j)
            nprods += 1
        if deg(acc) > D:
            return False, "(d) node %d: deg %d > %d" % (i, deg(acc), D), stats
        polys[i] = acc
    o = cert.get("output")
    stats = {"nodes": len(nodes), "rows": nrows, "prods": nprods, "max_mu": max_mu}
    if o not in polys:
        return False, "(e) output %r is not a node" % (o,), stats
    if polys[o] != {0}:
        return False, "(e) poly(output) != 1 (%d terms, has_const=%s)" % (len(polys[o]), 0 in polys[o]), stats
    stats["deg_by_node"] = {i: deg(p) for i, p in polys.items()}
    return True, None, stats


def check_flat(C, fs, nv=NV, neq=NEQ):
    """FORMAT flat-v1: sum_{(mu,k) in C} mu*f_k == 1 in B. Returns
    (identity_holds, max|mu|)."""
    acc = set()
    mx = 0
    for mu, k in C:
        assert 0 <= k < neq and all(0 <= v < nv for v in mu) and len(set(mu)) == len(mu)
        acc ^= mono_mul(fs[k], mask_of(mu))
        mx = max(mx, len(mu))
    return acc == {0}, mx


# ------------------------------------------------ ann-v1 coordinate order
def ann_order(D=4, nv=NV):
    monos = [m for m in range(1 << nv) if popcount(m) <= D]
    monos.sort(key=lambda m: (-popcount(m), m))
    return monos


ANN = None
ANN_POS = None


def _ann_init():
    global ANN, ANN_POS
    if ANN is None:
        ANN = ann_order()
        ANN_POS = {m: c for c, m in enumerate(ANN)}
        assert len(ANN) == 6196 and ANN[-1] == 0


def poly_to_vec(poly):
    _ann_init()
    v = np.zeros(6196, dtype=np.uint8)
    for m in poly:
        v[ANN_POS[m]] ^= 1
    return v


def hex_to_bits(h, width=6196):
    x = int(h, 16)
    if x >> width:
        raise ValueError("functional has bits beyond coordinate %d" % (width - 1))
    b = np.frombuffer(x.to_bytes((width + 7) // 8, "little"), dtype=np.uint8)
    return np.unpackbits(b, bitorder="little")[:width]


# ------------------------------------------------------ GF(2) elimination
def gf2_rref_nullspace(A):
    """Own elimination. A: (r x n) uint8 0/1. Returns (rank, nullspace basis
    as (n - rank) x n uint8). Reduced row echelon form by column sweep on
    packed uint64 rows."""
    r, n = A.shape
    words = (n + 63) // 64
    M = np.zeros((r, words * 64), dtype=np.uint8)
    M[:, :n] = A
    P = np.packbits(M, axis=1, bitorder="little").view(np.uint64).copy()
    pivrow_of_col = {}
    row = 0
    for c in range(n):
        if row >= r:
            break
        w, b = divmod(c, 64)
        bit = np.uint64(1) << np.uint64(b)
        col = (P[row:, w] & bit) != 0
        nz = np.flatnonzero(col)
        if nz.size == 0:
            continue
        p = row + nz[0]
        if p != row:
            P[[row, p]] = P[[p, row]]
        mask = (P[:, w] & bit) != 0
        mask[row] = False
        P[mask] ^= P[row]
        pivrow_of_col[c] = row
        row += 1
    rank = row
    R = np.unpackbits(P[:rank].view(np.uint8), axis=1, bitorder="little")[:, :n]
    pivcols = sorted(pivrow_of_col)
    free = [c for c in range(n) if c not in pivrow_of_col]
    K = np.zeros((len(free), n), dtype=np.uint8)
    for t, f in enumerate(free):
        K[t, f] = 1
        for pc in pivcols:
            if R[pivrow_of_col[pc], f]:
                K[t, pc] = 1
    return rank, K


def gf2_rank(A):
    rank, _ = gf2_rref_nullspace(A)
    return rank


def matmul2(A, B):
    """(A @ B) mod 2 exactly, via float32 BLAS (inner dim <= 2^24)."""
    assert A.shape[1] == B.shape[0] and A.shape[1] < (1 << 24)
    return (np.rint(A.astype(np.float32) @ B.astype(np.float32)).astype(np.int64) & 1).astype(np.uint8)


def m4_rows(fs):
    """All rows mu*f_k of M_4 (|mu| <= 2, k in 0..18), as a 4009 x 6196
    matrix in ann-v1 coordinates. Row order is irrelevant to (A1)."""
    rows = []
    for mu in COLS2:
        for k in range(NEQ):
            rows.append(poly_to_vec(mono_mul(fs[k], mu)))
    return np.array(rows, dtype=np.uint8)


def check_ann(cert, fs, D=4, nv=NV, neq=NEQ, M4=None):
    """(A1)-(A3) of FORMAT ann-v1, literally. Returns (valid, first_violation,
    stats)."""
    _ann_init()
    if cert.get("D") != D or cert.get("nv") != nv or cert.get("neq") != neq:
        return False, "header (D, nv, neq)", {}
    L = np.array([hex_to_bits(h) for h in cert["L_hex"]], dtype=np.uint8)
    stats = {"L_size": int(L.shape[0])}
    if M4 is None:
        M4 = m4_rows(fs)
    # (A1) every row of M_4 lies in S
    A1 = matmul2(L, M4.T)
    bad = np.argwhere(A1)
    if bad.size:
        li, ri = bad[0]
        return False, "(A1) lambda %d nonzero on M_4 row %d" % (li, ri), stats
    # (A2) basis K of S cap B_{<=3} by own elimination; lambda(v_j k) = 0
    first3 = 6196 - 1351  # degree-4 coordinates come first in the order
    assert all(popcount(m) == 4 for m in ANN[:first3]) and all(popcount(m) <= 3 for m in ANN[first3:])
    L3 = L[:, first3:]
    rank3, Kb = gf2_rref_nullspace(L3)
    # K as full 6196-vectors (zero on degree-4 coordinates)
    stats.update({"rank_L_on_B3": int(rank3), "dim_S_cap_B3": int(Kb.shape[0])})
    # sanity: K really lies in S and has full rank
    Kfull = np.zeros((Kb.shape[0], 6196), dtype=np.uint8)
    Kfull[:, first3:] = Kb
    assert not matmul2(L, Kfull.T).any()
    assert gf2_rank(Kb) == Kb.shape[0]
    monos3 = ANN[first3:]
    for j in range(nv):
        # v_j * k for every k in K, built monomial by monomial (literal product)
        tgt = np.array([ANN_POS[m | (1 << j)] for m in monos3], dtype=np.int64)
        Pj = np.zeros((Kb.shape[0], 6196), dtype=np.int64)
        np.add.at(Pj.T, tgt, Kb.T.astype(np.int64))
        Pj = (Pj & 1).astype(np.uint8)
        A2 = matmul2(L, Pj.T)
        bad = np.argwhere(A2)
        if bad.size:
            li, ki = bad[0]
            return False, "(A2) lambda %d nonzero on v_%d * K[%d]" % (li, j, ki), stats
    # (A3) some lambda has lambda(1) = 1
    if not L[:, 6195].any():
        return False, "(A3) no lambda with lambda(1) = 1", stats
    stats["n_lambda_one"] = int(L[:, 6195].sum())
    return True, None, stats

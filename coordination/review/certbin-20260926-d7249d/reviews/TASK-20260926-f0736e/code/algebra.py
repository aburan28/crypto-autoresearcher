"""Boolean-algebra side of the blind re-derivation (TASK-20260926-f0736e).

Everything here is written from the text of EXP-CERTBIN-060020 object,
EXP-CERTBIN-e94b27 object (M_D, W_D) and EXP-CERTBIN-4e92d7 object
(Macaulay conventions).  numpy + an own C kernel (gf2kern.c) only.

Monomials are bitmasks: bit i set <=> v_i divides the monomial.
Polynomials over F_2 are numpy arrays of distinct masks (sparse) or packed
bit vectors over a column order (dense).

COLUMN ORDER used for every matrix and closure here: all multilinear
monomials of degree <= D sorted by (-degree, bitmask ascending).  This is the
ann-v1 coordinate order of the specification.  It is degree-graded, so an
echelon basis's rows with leading monomial of degree <= d span X cap B_{<=d};
ranks, dims_by_deg and "1 in X" do not depend on the within-degree order
(BR-1).  The specification's own Macaulay column order (descending
degrevlex) is NOT used; see ambiguities in the report.
"""
import ctypes
import itertools
import os
import subprocess

import numpy as np

import field as F

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# C kernel
# ---------------------------------------------------------------------------
_LIB = None
CFLAGS = ["-O3", "-march=native", "-fPIC", "-shared"]


def lib():
    global _LIB
    if _LIB is None:
        src = os.path.join(HERE, "gf2kern.c")
        build_dir = os.environ.get("F0736E_BUILD_DIR", os.path.join(HERE, "..", "build"))
        os.makedirs(build_dir, exist_ok=True)
        so = os.path.join(build_dir, "gf2kern.so")
        if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(src):
            subprocess.check_call(["gcc"] + CFLAGS + ["-o", so, src])
        L = ctypes.CDLL(so)
        u64p = np.ctypeslib.ndpointer(dtype=np.uint64, flags="C_CONTIGUOUS")
        i32p = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
        u8p = np.ctypeslib.ndpointer(dtype=np.uint8, flags="C_CONTIGUOUS")
        ci = ctypes.c_int
        L.insert_batch.argtypes = [ci, u64p, i32p, i32p, u64p, ci, ci, u64p, ci, i32p, ci, u64p, i32p]
        L.insert_batch.restype = ci
        L.reduce_batch.argtypes = [ci, u64p, i32p, u64p, u64p, ci, i32p, ci, u64p, u64p]
        L.reduce_batch.restype = None
        L.mul_var.argtypes = [ci, ci, u64p, ci, i32p, u64p, ctypes.POINTER(ci)]
        L.mul_var.restype = None
        L.full_reduce.argtypes = [ci, u64p, i32p, ci, i32p, ci, u64p]
        L.full_reduce.restype = None
        L.parity_products.argtypes = [ci, u64p, ci, u64p, ci, u8p]
        L.parity_products.restype = None
        _LIB = L
    return _LIB


# ---------------------------------------------------------------------------
# Monomial orders
# ---------------------------------------------------------------------------
def popcount(a):
    return np.bitwise_count(np.asarray(a, dtype=np.uint64)).astype(np.int64)


def mu_order(d, nv):
    """Multilinear monomials of degree <= d: degree ascending, then ascending
    sorted index tuple (lexicographic).  Returns list of masks."""
    out = []
    for deg in range(d + 1):
        for tup in itertools.combinations(range(nv), deg):
            m = 0
            for i in tup:
                m |= 1 << i
            out.append(m)
    return out


def mask_to_tuple(m):
    return [i for i in range(m.bit_length()) if (m >> i) & 1]


class Cols:
    """Column order (-degree, bitmask ascending) for monomials of degree <= D."""
    _cache = {}

    def __new__(cls, nv, D):
        key = (nv, D)
        if key in cls._cache:
            return cls._cache[key]
        self = object.__new__(cls)
        self.nv, self.D = nv, D
        allm = np.arange(1 << nv, dtype=np.int64)
        deg = popcount(allm)
        sel = allm[deg <= D]
        sd = deg[deg <= D]
        order = np.lexsort((sel, -sd))
        self.masks = sel[order]
        self.deg = sd[order]
        self.n = len(self.masks)
        self.nw = (self.n + 63) // 64
        self.idx = np.full(1 << nv, -1, dtype=np.int64)
        self.idx[self.masks] = np.arange(self.n)
        self.const_col = int(self.idx[0])
        assert self.const_col == self.n - 1
        # first column of each degree (degree-descending blocks)
        self.deg_start = {d: int(np.flatnonzero(self.deg == d)[0]) for d in range(D + 1)}
        self._cmap = {}
        cls._cache[key] = self
        return self

    def cmap(self, j):
        """cmap[c] = column of mask(c) | v_j, or -1 if that has degree > D."""
        if j not in self._cmap:
            prod = self.masks | (1 << j)
            cm = self.idx[prod]
            self._cmap[j] = np.ascontiguousarray(cm.astype(np.int32))
        return self._cmap[j]

    def first_col_of_deg_le(self, d):
        """All columns >= this index have degree <= d."""
        return self.deg_start[d] if d <= self.D else 0


def pack_dense(dense_u8):
    """rows x ncols uint8 {0,1} -> rows x nw uint64 (bit c of row = column c)."""
    r, c = dense_u8.shape
    nw = (c + 63) // 64
    pad = np.zeros((r, nw * 64), dtype=np.uint8)
    pad[:, :c] = dense_u8
    b = np.packbits(pad, axis=1, bitorder="little")
    return np.ascontiguousarray(b.view(np.uint64).reshape(r, nw))


def unpack_rows(packed, ncols):
    b = packed.view(np.uint8)
    u = np.unpackbits(b, axis=1, bitorder="little")
    return u[:, :ncols]


def masks_to_packed(mask_lists, cols):
    """list of arrays of masks (each a polynomial) -> packed matrix."""
    dense = np.zeros((len(mask_lists), cols.n), dtype=np.uint8)
    for i, ms in enumerate(mask_lists):
        ms = np.asarray(ms, dtype=np.int64)
        if ms.size == 0:
            continue
        c = cols.idx[ms]
        assert (c >= 0).all(), "monomial outside column set"
        dense[i] = (np.bincount(c, minlength=cols.n) & 1).astype(np.uint8)
    return pack_dense(dense)


def packed_to_masks(vec, cols):
    u = np.unpackbits(vec.view(np.uint8), bitorder="little")[: cols.n]
    return cols.masks[np.flatnonzero(u)]


# ---------------------------------------------------------------------------
# Polynomials as mask arrays
# ---------------------------------------------------------------------------
def poly_reduce(masks):
    """XOR-accumulate a multiset of masks: keep those with odd multiplicity."""
    masks = np.asarray(masks, dtype=np.int64)
    if masks.size == 0:
        return masks
    u, c = np.unique(masks, return_counts=True)
    return u[(c & 1) == 1]


def poly_mul_monomial(p, mu):
    return poly_reduce(np.asarray(p, dtype=np.int64) | mu)


def poly_mul(p, q):
    p = np.asarray(p, dtype=np.int64)
    q = np.asarray(q, dtype=np.int64)
    if p.size == 0 or q.size == 0:
        return np.zeros(0, dtype=np.int64)
    return poly_reduce((p[:, None] | q[None, :]).ravel())


def poly_eval(p, assignment_mask):
    """Value at the Boolean point whose set variables are assignment_mask."""
    p = np.asarray(p, dtype=np.int64)
    return int(np.count_nonzero((p & ~assignment_mask) == 0) & 1)


def poly_deg(p):
    p = np.asarray(p, dtype=np.int64)
    return int(popcount(p).max()) if p.size else -1


# ---------------------------------------------------------------------------
# Descended system of S_3 (generic expansion over F_{2^19})
# ---------------------------------------------------------------------------
NV = 20
NEQ = 19
L_DIM = 10


def descend_S3(xR, B, l=L_DIM, n=F.N):
    """Expand S_3(x_1, x_2, x_R) with x_1 = sum_{j<l} v_j t^j,
    x_2 = sum_{j<l} v_{l+j} t^j over F_{2^n}, multilinearise (v^2 = v), and
    return the n equations (coefficient of t^k) as mask arrays.

    Generic multilinear polynomial arithmetic with F_{2^19} coefficients; it
    does NOT use any closed form of the expansion."""
    def pmul(P, Q):
        out = {}
        for m1, c1 in P.items():
            for m2, c2 in Q.items():
                m = m1 | m2
                v = out.get(m, 0) ^ F.mul(c1, c2)
                if v:
                    out[m] = v
                else:
                    out.pop(m, None)
        return out

    def padd(*Ps):
        out = {}
        for P in Ps:
            for m, c in P.items():
                v = out.get(m, 0) ^ c
                if v:
                    out[m] = v
                else:
                    out.pop(m, None)
        return out

    x1 = {1 << j: 1 << j for j in range(l)}
    x2 = {1 << (l + j): 1 << j for j in range(l)}
    x3 = {0: xR} if xR else {}
    Bp = {0: B} if B else {}
    u = padd(pmul(x1, x2), pmul(x1, x3), pmul(x2, x3))
    S = padd(pmul(u, u), pmul(pmul(x1, x2), x3), Bp)
    eqs = []
    for k in range(n):
        eqs.append(np.array(sorted(m for m, c in S.items() if (c >> k) & 1), dtype=np.int64))
    return eqs


def descend_S3_closed_form(xR, B, l=L_DIM, n=F.N):
    """Second, independent construction from the hand expansion
    S_3 = sum_{i,j} v_i v_{l+j} (t^{2(i+j)} + x_R t^{i+j})
          + x_R^2 sum_j (v_j + v_{l+j}) t^{2j} + B   (after v^2 = v).
    Used only as a cross-check of descend_S3."""
    coef = {}

    def add(m, c):
        v = coef.get(m, 0) ^ c
        if v:
            coef[m] = v
        else:
            coef.pop(m, None)

    xR2 = F.sq(xR)
    for i in range(l):
        for j in range(l):
            tij = F.power(2, i + j)
            add((1 << i) | (1 << (l + j)), F.sq(tij) ^ F.mul(xR, tij))
    for j in range(l):
        c = F.mul(xR2, F.power(2, 2 * j))
        add(1 << j, c)
        add(1 << (l + j), c)
    add(0, B)
    return [np.array(sorted(m for m, c in coef.items() if (c >> k) & 1), dtype=np.int64) for k in range(n)]


def eval_system_at(eqs, a):
    return [poly_eval(e, a) for e in eqs]


# ---------------------------------------------------------------------------
# E layout helpers (19 x 211; column j = j-th monomial of mu_order(2, 20))
# ---------------------------------------------------------------------------
def E_columns(nv=NV):
    return mu_order(2, nv)


def eqs_to_E(eqs, nv=NV):
    cols = E_columns(nv)
    pos = {m: i for i, m in enumerate(cols)}
    E = np.zeros((len(eqs), len(cols)), dtype=np.uint8)
    for k, e in enumerate(eqs):
        for m in e:
            E[k, pos[int(m)]] ^= 1
    return E


# ---------------------------------------------------------------------------
# Macaulay matrices
# ---------------------------------------------------------------------------
def macaulay(eqs, nv, D):
    """Rows (mu, k): mu over mu_order(D-2, nv), k over the equations, row index
    mu_index * neq + k, content = multilinear reduction of mu * f_k; zero rows
    retained.  Columns: Cols(nv, D).  Returns (packed rows, row labels, cols)."""
    cols = Cols(nv, D)
    mus = mu_order(D - 2, nv)
    neq = len(eqs)
    R = len(mus) * neq
    dense = np.zeros((R, cols.n), dtype=np.uint8)
    labels = []
    for mi, mu in enumerate(mus):
        for k, fk in enumerate(eqs):
            r = mi * neq + k
            labels.append((mu, k))
            if len(fk) == 0:
                continue
            c = cols.idx[np.asarray(fk, dtype=np.int64) | mu]
            assert (c >= 0).all()
            cnt = np.bincount(c, minlength=cols.n) & 1
            dense[r] = cnt.astype(np.uint8)
    return pack_dense(dense), labels, cols


# ---------------------------------------------------------------------------
# Incremental semi-echelon basis (C kernel)
# ---------------------------------------------------------------------------
class Basis:
    def __init__(self, cols, cap=None, tagbits=0):
        self.cols = cols
        self.nw = cols.nw
        self.cap = cap if cap is not None else cols.n
        self.rows = np.zeros((self.cap, self.nw), dtype=np.uint64)
        self.lead = np.full(self.cap, -1, dtype=np.int32)
        self.pivrow = np.full(self.nw * 64, -1, dtype=np.int32)
        self.pivmask = np.zeros(self.nw, dtype=np.uint64)
        self.rank = 0
        self.tw = (tagbits + 63) // 64 if tagbits else 0
        self.tags = np.zeros((self.cap, max(self.tw, 1)), dtype=np.uint64)

    def copy(self):
        b = Basis.__new__(Basis)
        b.cols, b.nw, b.cap = self.cols, self.nw, self.cap
        b.rows = self.rows.copy()
        b.lead = self.lead.copy()
        b.pivrow = self.pivrow.copy()
        b.pivmask = self.pivmask.copy()
        b.rank = self.rank
        b.tw = self.tw
        b.tags = self.tags.copy()
        return b

    def insert(self, V, tagidx=None):
        V = np.ascontiguousarray(V, dtype=np.uint64)
        nv = V.shape[0]
        res = np.zeros(max(nv, 1), dtype=np.int32)
        if nv == 0:
            return res[:0]
        if self.tw:
            ti = np.ascontiguousarray(np.asarray(tagidx, dtype=np.int32))
        else:
            ti = np.zeros(1, dtype=np.int32)
        r = lib().insert_batch(self.nw, self.rows, self.lead, self.pivrow, self.pivmask,
                               self.rank, self.cap, V, nv, res, self.tw, self.tags, ti)
        if r < 0:
            raise RuntimeError("basis capacity overflow")
        self.rank = r
        return res[:nv]

    def reduce(self, V, with_tags=False):
        V = np.ascontiguousarray(V.copy(), dtype=np.uint64)
        nv = V.shape[0]
        lead = np.zeros(max(nv, 1), dtype=np.int32)
        T = np.zeros((max(nv, 1), max(self.tw, 1)), dtype=np.uint64)
        lib().reduce_batch(self.nw, self.rows, self.pivrow, self.pivmask, V, nv, lead,
                           self.tw if with_tags else 0, self.tags, T)
        return V, lead[:nv], T[:nv]

    def lead_degrees(self):
        return self.cols.deg[self.lead[: self.rank]]

    def dims_by_deg(self):
        ld = self.lead_degrees()
        return [int(np.count_nonzero(ld <= d)) for d in range(self.cols.D + 1)]

    def has_one(self):
        return bool(self.pivrow[self.cols.const_col] >= 0)

    def low_rows(self, d):
        """Indices of basis rows whose leading monomial has degree <= d
        (a basis of X cap B_{<=d})."""
        return np.flatnonzero(self.lead_degrees() <= d)

    def full_reduce(self):
        lib().full_reduce(self.nw, self.rows, self.lead, self.rank, self.pivrow,
                          self.tw, self.tags)


def mul_var_packed(src, cols_src, cols_dst, j):
    """v_j * each row of src (rows over cols_src, degree <= D_dst - 1)."""
    src = np.ascontiguousarray(src, dtype=np.uint64)
    n = src.shape[0]
    dst = np.zeros((max(n, 1), cols_dst.nw), dtype=np.uint64)
    if n == 0:
        return dst[:0]
    if cols_src is cols_dst:
        cm = cols_dst.cmap(j)
    else:
        prod = cols_src.masks | (1 << j)
        cm = np.ascontiguousarray(cols_dst.idx[prod].astype(np.int32))
    err = ctypes.c_int(0)
    lib().mul_var(cols_src.nw, cols_dst.nw, src, n, cm, dst, ctypes.byref(err))
    if err.value:
        raise RuntimeError("product left the column set (degree bound violated)")
    return dst


# ---------------------------------------------------------------------------
# Closures
# ---------------------------------------------------------------------------
def macaulay_closure(eqs, nv, D):
    M, labels, cols = macaulay(eqs, nv, D)
    bas = Basis(cols)
    bas.insert(M)
    return {"shape": [int(M.shape[0]), int(cols.n)], "rank": int(bas.rank),
            "one": bas.has_one(), "dims_by_deg": bas.dims_by_deg()}, bas, M, labels


def w_closure_literal(bas0, nv, D, max_iter=64):
    """EXP-CERTBIN-e94b27 object.mutant_closure_W_D, literally:
    W^(0) = rowspace(M_D); W^(i+1) = W^(i) + span{v_j * b : b in a basis of
    W^(i) cap B_{<=D-1}, j = 0..nv-1} (multilinear reduction); stop at the
    first i with dim W^(i+1) = dim W^(i).  A FULL basis of W^(i) cap B_{<=D-1}
    (all echelon rows with leading degree <= D-1 at the start of iteration i)
    is multiplied at every iteration."""
    cols = bas0.cols
    bas = bas0.copy()
    dims = [int(bas.rank)]
    one_first = 0 if bas.has_one() else None
    low_counts = []
    i = 0
    while True:
        low = bas.low_rows(D - 1)
        low_counts.append(int(low.size))
        Bi = bas.rows[low].copy()
        prods = [mul_var_packed(Bi, cols, cols, j) for j in range(nv)]
        P = np.concatenate(prods, axis=0) if prods else np.zeros((0, cols.nw), np.uint64)
        bas.insert(P)
        dims.append(int(bas.rank))
        if one_first is None and bas.has_one():
            one_first = i + 1
        if dims[-1] == dims[-2]:
            fix = i
            break
        i += 1
        if i > max_iter:
            raise RuntimeError("W iteration did not stabilise")
    rec = {"dims": dims, "fixpoint_index": fix, "one_first_iteration": one_first,
           "one": bas.has_one(), "final_dim": int(bas.rank),
           "dims_by_deg": bas.dims_by_deg(), "basis_low_sizes": low_counts}
    return rec, bas


# ---------------------------------------------------------------------------
# Satisfiability
# ---------------------------------------------------------------------------
def var_tables(nv):
    a = np.arange(1 << nv, dtype=np.int64)
    out = []
    for i in range(nv):
        bits = ((a >> i) & 1).astype(np.uint8)
        out.append(np.packbits(bits, bitorder="little").view(np.uint64).copy())
    return out


_VT = {}


def exhaustive_s(eqs, nv=NV, return_solutions=False):
    """Number of v in F_2^nv with f_k(v) = 0 for all k, by evaluating every
    equation on all 2^nv points (packed truth tables)."""
    if nv not in _VT:
        _VT[nv] = var_tables(nv)
    vt = _VT[nv]
    nwords = (1 << nv) // 64
    ones = np.full(nwords, np.uint64(0xFFFFFFFFFFFFFFFF), dtype=np.uint64)
    alive = ones.copy()
    cache = {}
    for e in eqs:
        acc = np.zeros(nwords, dtype=np.uint64)
        for m in e:
            m = int(m)
            if m not in cache:
                t = ones.copy()
                for i in mask_to_tuple(m):
                    t &= vt[i]
                cache[m] = t
            acc ^= cache[m]
        alive &= ~acc
    s = int(np.bitwise_count(alive).sum())
    if return_solutions:
        bits = np.unpackbits(alive.view(np.uint8), bitorder="little")
        return s, np.flatnonzero(bits).astype(np.int64)
    return s


def exhaustive_s_unpacked(eqs, nv=NV):
    """Second evaluator (self-test only): unpacked uint8 arrays."""
    a = np.arange(1 << nv, dtype=np.int64)
    alive = np.ones(1 << nv, dtype=bool)
    for e in eqs:
        val = np.zeros(1 << nv, dtype=np.uint8)
        for m in e:
            m = int(m)
            val ^= ((a & m) == m).astype(np.uint8)
        alive &= (val == 0)
    return int(alive.sum())


def s_route_quadratic(xR, B, l=L_DIM):
    """Route 2 (does not use the descended equations): for each x_1 in V solve
    S_3(x_1, x_2, x_R) = 0 for x_2 in F_{2^19} and count roots in V.
    S_3 = (x_1 + x_R)^2 x_2^2 + x_1 x_R x_2 + x_1^2 x_R^2 + B."""
    x1 = np.arange(1 << l, dtype=np.int64)
    xr = np.full_like(x1, xR)
    a = F.vsq(x1 ^ xr)
    b = F.vmul(x1, xr)
    c = F.vmul(F.vsq(x1), F.vsq(xr)) ^ B
    total = 0
    roots_checked = 0
    per_x1 = np.zeros(1 << l, dtype=np.int64)
    Vlim = 1 << l
    for idx in range(1 << l):
        ai, bi, ci = int(a[idx]), int(b[idx]), int(c[idx])
        roots = []
        if ai != 0 and bi != 0:
            # x2 = (b/a) z, z^2 + z = c a / b^2
            y = F.mul(F.mul(ci, ai), F.inv(F.sq(bi)))
            if F.tr(y) == 0:
                z = F.half_trace(y)
                sc = F.mul(bi, F.inv(ai))
                roots = [F.mul(sc, z), F.mul(sc, z ^ 1)]
        elif ai != 0 and bi == 0:
            roots = [F.sqrt(F.mul(ci, F.inv(ai)))]
        elif ai == 0 and bi != 0:
            roots = [F.mul(ci, F.inv(bi))]
        else:
            if ci == 0:
                per_x1[idx] = Vlim  # every x_2 is a root; all of V counts
                total += Vlim
                continue
            roots = []
        for r in roots:
            val = F.mul(ai, F.sq(r)) ^ F.mul(bi, r) ^ ci
            assert val == 0, "root check failed"
            assert F.S3(int(x1[idx]), r, xR, B) == 0
            roots_checked += 1
        cnt = sum(1 for r in set(roots) if r < Vlim)
        per_x1[idx] = cnt
        total += cnt
    return int(total), roots_checked


def s_route_quadratic_vec(xR, B, l=L_DIM):
    """Vectorised form of s_route_quadratic for the generic case; falls back
    to the scalar routine if any special case (a = 0 or b = 0) occurs."""
    x1 = np.arange(1 << l, dtype=np.int64)
    xr = np.full_like(x1, xR)
    a = F.vsq(x1 ^ xr)
    b = F.vmul(x1, xr)
    if (a == 0).any() or (b == 0).any():
        return None
    c = F.vmul(F.vsq(x1), F.vsq(xr)) ^ B
    y = F.vmul(F.vmul(c, a), F.vinv(F.vsq(b)))
    solv = F.vtr(y) == 0
    z = F.vhalf_trace(y)
    sc = F.vmul(b, F.vinv(a))
    r1 = F.vmul(sc, z)
    r2 = F.vmul(sc, z ^ 1)
    # root checks on solvable x_1
    for r in (r1, r2):
        val = F.vmul(a, F.vsq(r)) ^ F.vmul(b, r) ^ c
        assert (val[solv] == 0).all()
    Vlim = 1 << l
    cnt = ((r1 < Vlim) & solv).astype(np.int64) + ((r2 < Vlim) & solv).astype(np.int64)
    return int(cnt.sum())


# ---------------------------------------------------------------------------
# rc_b
# ---------------------------------------------------------------------------
def left_kernel(Q):
    """Left kernel {c : c^T Q = 0} of an F_2 matrix (rows x cols uint8), by
    row reduction with identity tags.  Returns a list of basis vectors (uint8
    arrays of length rows) in RREF-by-tag form."""
    r, c = Q.shape
    A = np.concatenate([Q.astype(np.uint8), np.eye(r, dtype=np.uint8)], axis=1)
    piv_row = 0
    for col in range(c):
        nz = np.flatnonzero(A[piv_row:, col]) + piv_row
        if nz.size == 0:
            continue
        p = nz[0]
        if p != piv_row:
            A[[piv_row, p]] = A[[p, piv_row]]
        others = np.flatnonzero(A[:, col])
        others = others[others != piv_row]
        A[others] ^= A[piv_row]
        piv_row += 1
        if piv_row == r:
            break
    ker = A[piv_row:, c:]
    # sanity: every kernel vector annihilates Q
    for v in ker:
        assert not ((v.astype(np.int64) @ Q.astype(np.int64)) & 1).any()
    return [k.copy() for k in ker], int(r - piv_row)


def kernel_basis_rref(vecs):
    """Row-reduce a list of 0/1 vectors to RREF (for a canonical kernel basis)."""
    if not vecs:
        return []
    A = np.array(vecs, dtype=np.uint8)
    r, c = A.shape
    pr = 0
    for col in range(c):
        nz = np.flatnonzero(A[pr:, col]) + pr
        if nz.size == 0:
            continue
        p = nz[0]
        if p != pr:
            A[[pr, p]] = A[[p, pr]]
        others = np.flatnonzero(A[:, col])
        others = others[others != pr]
        A[others] ^= A[pr]
        pr += 1
        if pr == r:
            break
    return [A[i].copy() for i in range(pr)]


def substitute(eqs, ell, jstar, nv=NV):
    """pi: v_{j*} := ell + v_{j*} (an affine form in the other variables);
    remaining variables relabelled in ascending order; multilinear reduction.
    ell is a mask array of degree <= 1 containing v_{j*}."""
    ell = np.asarray(ell, dtype=np.int64)
    bit = 1 << jstar
    a = poly_reduce(np.concatenate([ell, np.array([bit], dtype=np.int64)]))  # ell + v_{j*}
    assert not (a & bit).any()
    out = []
    for f in eqs:
        f = np.asarray(f, dtype=np.int64)
        keep = f[(f & bit) == 0]
        hit = f[(f & bit) != 0] & ~bit  # m = v_{j*} * r  ->  a * r
        prod = (a[:, None] | hit[None, :]).ravel() if hit.size and a.size else np.zeros(0, np.int64)
        g = poly_reduce(np.concatenate([keep, prod]))
        # relabel: bits above j* shift down by one
        low = g & (bit - 1)
        high = (g >> (jstar + 1)) << jstar
        out.append(np.sort(low | high))
    return out


def unsubstitute_point(u, jstar, a_poly):
    """Extend a point u of F_2^{nv-1} (relabelled) to F_2^nv with
    v_{j*} = a(u), i.e. ell = 0 (used in the substitution self-test)."""
    bit = 1 << jstar
    low = u & (bit - 1)
    high = (u >> jstar) << (jstar + 1)
    full = low | high
    val = poly_eval(a_poly, full)
    return full | (bit if val else 0)


def rc_b(eqs, nv=NV, xR=None):
    """object.ell_and_rc_b steps (1)-(5) with the BR-5 blind reading of (1)."""
    E = eqs_to_E(eqs, nv)
    Q = E[:, 1 + nv:]  # the 190 quadratic columns 21..210
    kers, kdim = left_kernel(Q)
    kers = kernel_basis_rref(kers)
    rec = {"kernel_dim": kdim}
    c = None
    if kdim == 1:
        c = kers[0]
        rec["kernel_vector_rule"] = "dim 1: the nonzero kernel vector"
    elif kdim > 1:
        zero_rows = [k for k in range(Q.shape[0]) if not Q[k].any()]
        if zero_rows:
            k0 = zero_rows[0]
            c = np.zeros(Q.shape[0], dtype=np.uint8)
            c[k0] = 1
            rec["kernel_vector_rule"] = "dim %d > 1: lowest unit vector e_%d in the kernel" % (kdim, k0)
        else:
            rec["kernel_vector_rule"] = None
    else:
        rec["kernel_vector_rule"] = None
    if c is None:
        rec["applicable"] = False
        rec["status"] = "not applicable (kernel dim %d)" % kdim
        return rec, None
    rec["kernel_vector"] = [int(k) for k in np.flatnonzero(c)]
    if xR is not None:
        xr2inv = F.inv(F.sq(xR)) if xR else None
        if xR:
            pred = [F.tr(F.mul(1 << k, xr2inv)) for k in range(len(eqs))]
            rec["c_equals_Tr(t^k/x_R^2)"] = bool(list(map(int, c)) == pred)
        else:
            rec["c_equals_Tr(t^k/x_R^2)"] = None
    ell = poly_reduce(np.concatenate([np.asarray(eqs[k], dtype=np.int64) for k in np.flatnonzero(c)]))
    assert poly_deg(ell) <= 1, "ell has a quadratic part"
    lin = sorted(int(m).bit_length() - 1 for m in ell if m != 0)
    const = int(np.any(ell == 0))
    rec["ell_linear_support"] = lin
    rec["ell_constant"] = const
    if not lin:
        rec["applicable"] = False
        rec["step3_label"] = "REFUTED-AT-DEGREE-2" if const == 1 else "ELL-TRIVIAL"
        rec["status"] = "step 3: " + rec["step3_label"] + " (no substitution)"
        rec["jstar"] = None
        return rec, {"ell": ell}
    jstar = lin[0]
    rec["step3_label"] = None
    rec["jstar"] = jstar
    rec["applicable"] = True
    rec["status"] = "applied"
    sub = substitute(eqs, ell, jstar, nv)
    r3, _, _, _ = macaulay_closure(sub, nv - 1, 3)
    r4, bas4, _, _ = macaulay_closure(sub, nv - 1, 4)
    rec["R3_shape"] = r3["shape"]
    rec["R4_shape"] = r4["shape"]
    rec["rank_R3"] = r3["rank"]
    rec["one_R3"] = r3["one"]
    rec["rank_R4"] = r4["rank"]
    rec["one_R4"] = r4["one"]
    rec["dims_by_deg_R4"] = r4["dims_by_deg"]
    rec["sigma"] = r4["dims_by_deg"][3] - 360
    rec["T5_applicable"] = bool(r4["dims_by_deg"][3] == r3["rank"])
    return rec, {"ell": ell, "sub": sub, "bas4": bas4}


def ell_route(bas_M4, ell, nv=NV):
    """1 in rowspace(M_4) + ell * B_{<=3}: one extra elimination in nv
    variables, starting from the M_4 basis and inserting ell * m for every
    multilinear monomial m of degree <= 3."""
    cols = bas_M4.cols
    bas = bas_M4.copy()
    mons = cols.masks[cols.deg <= 3]
    ell = np.asarray(ell, dtype=np.int64)
    polys = [poly_reduce(ell | m) for m in mons]
    P = masks_to_packed(polys, cols)
    bas.insert(P)
    return bool(bas.has_one()), int(bas.rank)

"""Independent checkers for wdag-v1 and ann-v1 (TASK-20260926-f0736e).

Self-contained: numpy only.  Shares NO code with algebra.py, certs.py,
field.py or gf2kern.c.  It has its own F_{2^19} multiplication, its own
closed-form construction of the descended S_3 system, its own multilinear
arithmetic on bitmasks (dense parity arrays over all 2^20 masks), its own
coordinate order and its own Gaussian elimination.

Rules implemented verbatim from EXP-CERTBIN-060020 object.certificate_format:

wdag-v1: poly(i) = sum_{(mu,k) in rows} mu*f_k + sum_{(j,c) in prods}
v_j * poly(c) in B.  VALID iff (a) every child c < i; (b) every |mu| <= 2 and
every k in 0..18; (c) every child c used in prods has deg poly(c) <= 3;
(d) every node has deg poly(i) <= 4; (e) poly(output) == 1.

ann-v1: L a list of functionals on B_{<=4} in the coordinate order "all
multilinear monomials of degree <= 4 in v_0..v_19 sorted by (-degree,
bitmask ascending)"; S = {g : lambda(g) = 0 for all lambda in L}.  VALID iff
(A1) every row of M_4 lies in S; (A2) for a basis K of S cap B_{<=3} computed
by the verifier's own elimination, lambda(v_j k) = 0 for every k in K,
j in 0..19, lambda in L; (A3) some lambda in L has lambda(1) = 1.
"""
import itertools

import numpy as np

NV = 20
NEQ = 19
D = 4
MODP = 0b10000000000000100111  # t^19 + t^5 + t^2 + t + 1


# ---- own field arithmetic ---------------------------------------------------
def _fmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> 19:
            a ^= MODP
    return r


def _fpow_t(e):
    r = 1
    for _ in range(e):
        r <<= 1
        if r >> 19:
            r ^= MODP
    return r


def curve_system(xR, B, l=10):
    """Closed form of the descended system (own derivation):
    S_3 = x1^2 x2^2 + x_R^2 (x1^2 + x2^2) + x_R x1 x2 + B with
    x1^2 x2^2 -> sum v_i v_{l+j} t^{2(i+j)}, x1 x2 -> sum v_i v_{l+j} t^{i+j},
    x1^2 -> sum v_j t^{2j}."""
    coef = {}

    def add(m, c):
        coef[m] = coef.get(m, 0) ^ c

    xR2 = _fmul(xR, xR)
    for i in range(l):
        for j in range(l):
            p = _fpow_t(i + j)
            add((1 << i) | (1 << (l + j)), _fmul(p, p) ^ _fmul(xR, p))
    for j in range(l):
        c = _fmul(xR2, _fpow_t(2 * j))
        add(1 << j, c)
        add(1 << (l + j), c)
    add(0, B)
    return [np.array(sorted(m for m, c in coef.items() if (c >> k) & 1), dtype=np.int64) for k in range(19)]


def explicit_system(equations):
    eqs = []
    for eq in equations:
        ms = []
        for mono in eq:
            m = 0
            for v in mono:
                if not (isinstance(v, int) and 0 <= v < NV):
                    raise ValueError("bad variable %r" % (v,))
                m ^= 1 << v  # a repeated index would cancel; rejected below
            if bin(m).count("1") != len(mono):
                raise ValueError("repeated variable in monomial %r" % (mono,))
            ms.append(m)
        u, c = np.unique(np.array(ms, dtype=np.int64), return_counts=True)
        eqs.append(u[(c & 1) == 1])
    return eqs


# ---- dense parity arithmetic over all 2^nv masks ---------------------------
def _pc(a):
    return np.bitwise_count(np.asarray(a, dtype=np.uint64)).astype(np.int64)


def _deg(p):
    return int(_pc(p).max()) if p.size else -1


def _poly_from_multiset(idx, nv=NV):
    if len(idx) == 0:
        return np.zeros(0, dtype=np.int64)
    idx = np.concatenate(idx) if isinstance(idx, list) else idx
    par = np.bincount(idx, minlength=1 << nv) & 1
    return np.flatnonzero(par).astype(np.int64)


def check_wdag(cert, eqs, label, nv=NV, neq=NEQ, D=4):
    """Returns (valid: bool, reason: str).  D = 4 is the frozen format; other
    D (self-tests only) apply the same rules with |mu| <= D-2, child degree
    <= D-1 and node degree <= D."""
    try:
        if cert.get("label") != label:
            return False, "label mismatch"
        if cert.get("D") != D or cert.get("nv") != nv or cert.get("neq") != neq:
            return False, "header mismatch"
        nodes = cert["nodes"]
        ids = [n["id"] for n in nodes]
        if len(set(ids)) != len(ids) or not all(isinstance(i, int) for i in ids):
            return False, "node ids not unique integers"
        byid = {n["id"]: n for n in nodes}
        polys = {}
        for i in sorted(byid):
            n = byid[i]
            parts = []
            for entry in n["rows"]:
                mu, k = entry
                if not isinstance(k, int) or not (0 <= k < neq):
                    return False, "(b) k out of range at node %d" % i
                if not isinstance(mu, list) or len(mu) > D - 2:
                    return False, "(b) |mu| > %d at node %d" % (D - 2, i)
                if any((not isinstance(x, int)) or x < 0 or x >= nv for x in mu):
                    return False, "(b) bad variable in mu at node %d" % i
                if len(set(mu)) != len(mu):
                    return False, "(b) repeated variable in mu at node %d" % i
                mm = 0
                for x in mu:
                    mm |= 1 << x
                parts.append(eqs[k] | mm)
            for entry in n["prods"]:
                j, c = entry
                if not isinstance(j, int) or not (0 <= j < nv):
                    return False, "bad variable j at node %d" % i
                if not isinstance(c, int) or c not in byid:
                    return False, "(a) unknown child %r at node %d" % (c, i)
                if not c < i:
                    return False, "(a) child %d not < %d" % (c, i)
                pc = polys[c]
                if _deg(pc) > D - 1:
                    return False, "(c) child %d has degree %d > %d" % (c, _deg(pc), D - 1)
                parts.append(pc | (1 << j))
            p = _poly_from_multiset(parts, nv) if parts else np.zeros(0, dtype=np.int64)
            if _deg(p) > D:
                return False, "(d) node %d has degree %d > %d" % (i, _deg(p), D)
            polys[i] = p
        o = cert["output"]
        if o not in polys:
            return False, "(e) output node missing"
        po = polys[o]
        if not (po.size == 1 and po[0] == 0):
            return False, "(e) poly(output) != 1 (%d terms)" % po.size
        return True, "valid (a)-(e); %d nodes" % len(nodes)
    except Exception as e:  # malformed structure is a rejection
        return False, "malformed: %s: %s" % (type(e).__name__, e)


# ---- ann-v1 ----------------------------------------------------------------
_COORD = {}


def coords(nv=NV, d=D):
    if (nv, d) not in _COORD:
        ms = []
        for deg in range(d, -1, -1):
            block = []
            for tup in itertools.combinations(range(nv), deg):
                m = 0
                for x in tup:
                    m |= 1 << x
                block.append(m)
            ms.extend(sorted(block))
        ms = np.array(ms, dtype=np.int64)
        pos = np.full(1 << nv, -1, dtype=np.int64)
        pos[ms] = np.arange(ms.size)
        _COORD[(nv, d)] = (ms, pos, _pc(ms))
    return _COORD[(nv, d)]


def m4_rows_dense(eqs, nv=NV):
    ms, pos, deg = coords(nv)
    mus = [0]
    for dd in (1, 2):
        for tup in itertools.combinations(range(nv), dd):
            m = 0
            for x in tup:
                m |= 1 << x
            mus.append(m)
    rows = np.zeros((len(mus) * len(eqs), ms.size), dtype=np.uint8)
    r = 0
    for mu in mus:
        for f in eqs:
            if f.size:
                c = pos[f | mu]
                rows[r] = (np.bincount(c, minlength=ms.size) & 1).astype(np.uint8)
            r += 1
    return rows


def _pack(A):
    r, c = A.shape
    nw = (c + 63) // 64
    pad = np.zeros((r, nw * 64), dtype=np.uint8)
    pad[:, :c] = A
    return np.packbits(pad, axis=1, bitorder="little").view(np.uint64).reshape(r, nw).copy()


def _unpack(P, c):
    return np.unpackbits(P.view(np.uint8), axis=1, bitorder="little")[:, :c]


def nullspace(A):
    """Own elimination: basis of {x : A x = 0} over F_2 (A: r x c uint8).
    Packed Gauss-Jordan, column by column."""
    r, c = A.shape
    P = _pack(A)
    pivcols = []
    prow = 0
    for col in range(c):
        w, b = col >> 6, np.uint64(col & 63)
        colbits = (P[prow:, w] >> b) & np.uint64(1)
        nz = np.flatnonzero(colbits)
        if nz.size == 0:
            continue
        p = prow + int(nz[0])
        if p != prow:
            P[[prow, p]] = P[[p, prow]]
        hit = np.flatnonzero((P[:, w] >> b) & np.uint64(1))
        hit = hit[hit != prow]
        if hit.size:
            P[hit] ^= P[prow]
        pivcols.append(col)
        prow += 1
        if prow == r:
            break
    R = _unpack(P[:prow], c)
    free = np.setdiff1d(np.arange(c), np.array(pivcols, dtype=np.int64))
    K = np.zeros((free.size, c), dtype=np.uint8)
    K[np.arange(free.size), free] = 1
    if prow:
        K[:, np.array(pivcols)] = R[:, free].T
    return K, prow


def _parity_matmul(A, Bm, chunk=2048):
    """(A @ Bm.T) mod 2 for 0/1 uint8 matrices, exact in float32 (sums <= 2^24)."""
    Af = A.astype(np.float32)
    out = np.zeros((A.shape[0], Bm.shape[0]), dtype=np.uint8)
    for s in range(0, Bm.shape[0], chunk):
        Bf = Bm[s:s + chunk].astype(np.float32)
        prod = Af @ Bf.T
        out[:, s:s + chunk] = (np.rint(prod).astype(np.int64) & 1).astype(np.uint8)
    return out


def check_ann(cert, eqs, label, nv=NV, neq=NEQ, m4=None):
    """Returns (valid, reason, details)."""
    det = {}
    try:
        if cert.get("label") != label:
            return False, "label mismatch", det
        if cert.get("D") != 4 or cert.get("nv") != nv or cert.get("neq") != neq:
            return False, "header mismatch", det
        ms, pos, deg = coords(nv)
        n = ms.size
        Lh = cert["L_hex"]
        if not isinstance(Lh, list) or len(Lh) == 0:
            return False, "empty L", det
        nb = (n + 7) // 8
        Lm = np.zeros((len(Lh), n), dtype=np.uint8)
        for i, h in enumerate(Lh):
            x = int(h, 16)
            if x < 0 or x >> n:
                return False, "functional %d has bits beyond coordinate %d" % (i, n - 1), det
            by = np.frombuffer(x.to_bytes(nb, "little"), dtype=np.uint8)
            Lm[i] = np.unpackbits(by, bitorder="little")[:n]
        det["functionals"] = int(Lm.shape[0])
        # (A3)
        const = int(pos[0])
        a3 = bool(Lm[:, const].any())
        # (A1)
        M4 = m4 if m4 is not None else m4_rows_dense(eqs, nv)
        a1_par = _parity_matmul(Lm, M4)
        a1 = not a1_par.any()
        # (A2)
        low = np.flatnonzero(deg <= 3)
        L3 = Lm[:, low]
        K, rk = nullspace(L3)
        # own check of own elimination: L3 K^T = 0 and dimension count
        chk = _parity_matmul(L3, K) if K.size else np.zeros((1, 0), np.uint8)
        if chk.any() or K.shape[0] != low.size - rk:
            return False, "internal elimination check failed", det
        det["dim_S_cap_B3"] = int(K.shape[0])
        lowm = ms[low]
        a2 = True
        for j in range(nv):
            P = np.zeros((K.shape[0], n), dtype=np.uint8)
            for r in range(K.shape[0]):
                mm = lowm[np.flatnonzero(K[r])] | (1 << j)
                P[r] = (np.bincount(pos[mm], minlength=n) & 1).astype(np.uint8)
            if _parity_matmul(Lm, P).any():
                a2 = False
                det["A2_first_failing_j"] = j
                break
        det["A1"] = a1
        det["A2"] = a2
        det["A3"] = a3
        ok = a1 and a2 and a3
        reason = "valid (A1)-(A3)" if ok else "invalid: " + ",".join(
            k for k, v in (("A1", a1), ("A2", a2), ("A3", a3)) if not v)
        return ok, reason, det
    except Exception as e:
        return False, "malformed: %s: %s" % (type(e).__name__, e), det

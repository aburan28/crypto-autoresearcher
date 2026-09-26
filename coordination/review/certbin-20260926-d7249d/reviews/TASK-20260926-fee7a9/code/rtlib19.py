"""Red-team own GF(2) / Boolean-ring library for TASK-20260926-fee7a9.

Written from the specification TEXT only (EXP-CERTBIN-060020 object and
EXP-CERTBIN-e94b27 object definitions). Imports NO crypto_autoresearcher module
and reads none of impl/, verifier/ or src/crypto_autoresearcher/gf2/.

Conventions (my own, not the engine's):
  * A monomial is a bitmask over nv variables (bit i = v_i).
  * A polynomial in B_{<=D} is a Python int whose bit p is the coefficient of
    the p-th monomial of MY order: degree ascending, then combinations in
    lexicographic order of sorted index tuples. Bit 0 is the constant 1. The
    leading (highest) bit is therefore a monomial of maximal degree: the order
    is degree-compatible, so the echelon rows with leading degree <= d span
    X cap B_{<=d}.
  * The E_layout (19 x 211) of the specification is decoded separately
    (columns: constant, v_0..v_19, pairs (i, j), i < j, lexicographic).
"""
from itertools import combinations
import numpy as np

# ---------------------------------------------------------------- F_{2^19}
N19 = 19
MOD19 = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1  # t^19+t^5+t^2+t+1 = 524327


def fmul(a, b, n=N19, mod=MOD19):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> n:
            a ^= mod
    return r


def fsq(a, n=N19, mod=MOD19):
    return fmul(a, a, n, mod)


def fpow(a, e, n=N19, mod=MOD19):
    r = 1
    while e:
        if e & 1:
            r = fmul(r, a, n, mod)
        a = fmul(a, a, n, mod)
        e >>= 1
    return r


def finv(a, n=N19, mod=MOD19):
    assert a != 0
    return fpow(a, (1 << n) - 2, n, mod)


def ftr(a, n=N19, mod=MOD19):
    s = 0
    x = a
    for _ in range(n):
        s ^= x
        x = fmul(x, x, n, mod)
    assert s in (0, 1)
    return s


# ---------------------------------------------------------------- monomials
class Mono:
    """Monomial index for B_{<=D} in nv variables (my order)."""

    def __init__(self, nv, D):
        self.nv, self.D = nv, D
        self.masks = []
        self.deg_start = []
        for d in range(D + 1):
            self.deg_start.append(len(self.masks))
            for c in combinations(range(nv), d):
                m = 0
                for i in c:
                    m |= 1 << i
                self.masks.append(m)
        self.deg_start.append(len(self.masks))
        self.C = len(self.masks)
        self.index = {m: p for p, m in enumerate(self.masks)}
        self.deg = np.array([bin(m).count('1') for m in self.masks], dtype=np.int64)
        self.nbytes = (self.C + 7) // 8
        # product maps for v_j * g (g of degree <= D-1)
        self.S = []   # indices of monomials containing j (degree <= D)
        self.pre = []  # index of m \ {j} for each of those
        for j in range(nv):
            S, P = [], []
            for p, m in enumerate(self.masks):
                if m >> j & 1:
                    S.append(p)
                    P.append(self.index[m ^ (1 << j)])
            self.S.append(np.array(S, dtype=np.int64))
            self.pre.append(np.array(P, dtype=np.int64))

    def lead_deg(self, bit):
        # degree of monomial at bit position
        return int(self.deg[bit])

    def poly_from_masks(self, masks):
        r = 0
        for m in masks:
            r ^= 1 << self.index[m]
        return r

    def masks_of(self, x):
        out = []
        while x:
            b = x & -x
            p = b.bit_length() - 1
            out.append(self.masks[p])
            x ^= b
        return out

    def to_arr(self, x):
        by = x.to_bytes(self.nbytes, 'little')
        return np.unpackbits(np.frombuffer(by, dtype=np.uint8), bitorder='little')[: self.C]

    def from_arr_rows(self, A):
        """A: (n, C) uint8 0/1 -> list of ints."""
        P = np.packbits(A, axis=1, bitorder='little')
        return [int.from_bytes(P[i].tobytes(), 'little') for i in range(P.shape[0])]

    def times_var_batch(self, rows, j):
        """rows: list of ints of degree <= D-1. Returns list of ints v_j * row."""
        if not rows:
            return []
        G = np.stack([self.to_arr(x) for x in rows])
        Pm = np.zeros_like(G)
        Pm[:, self.S[j]] = G[:, self.S[j]] ^ G[:, self.pre[j]]
        return self.from_arr_rows(Pm)

    def times_all_vars_batch(self, rows):
        """All products v_j * row for j in 0..nv-1, rows of degree <= D-1."""
        if not rows:
            return []
        G = np.stack([self.to_arr(x) for x in rows])
        out = []
        for j in range(self.nv):
            Pm = np.zeros_like(G)
            Pm[:, self.S[j]] = G[:, self.S[j]] ^ G[:, self.pre[j]]
            out.extend(self.from_arr_rows(Pm))
        return out


def mul_masks(A, Bm):
    """Product of two polynomials given as sets of monomial masks (Boolean ring)."""
    r = set()
    for a in A:
        for b in Bm:
            m = a | b
            if m in r:
                r.remove(m)
            else:
                r.add(m)
    return r


# ---------------------------------------------------------------- echelon
class Echelon:
    """Incremental GF(2) echelon basis keyed by leading bit."""

    def __init__(self):
        self.piv = {}

    def reduce(self, x):
        piv = self.piv
        while x:
            p = x.bit_length() - 1
            r = piv.get(p)
            if r is None:
                return x
            x ^= r
        return 0

    def add(self, x):
        piv = self.piv
        while x:
            p = x.bit_length() - 1
            r = piv.get(p)
            if r is None:
                piv[p] = x
                return True
            x ^= r
        return False

    def dim(self):
        return len(self.piv)

    def has_one(self):
        return 0 in self.piv

    def dims_by_deg(self, mono):
        ds = []
        keys = np.array(sorted(self.piv.keys()), dtype=np.int64)
        for d in range(mono.D + 1):
            ds.append(int(np.sum(keys < mono.deg_start[d + 1])))
        return ds

    def low_rows(self, mono, maxdeg):
        lim = mono.deg_start[maxdeg + 1]
        return [r for p, r in self.piv.items() if p < lim]

    def copy(self):
        e = Echelon()
        e.piv = dict(self.piv)
        return e


# ---------------------------------------------------------------- systems
def e_layout_masks(nv=20):
    """Column j of the 19 x 211 E_layout -> monomial mask (nv = 20)."""
    cols = [0]
    for i in range(nv):
        cols.append(1 << i)
    for i, j in combinations(range(nv), 2):
        cols.append((1 << i) | (1 << j))
    return cols


E_COLS = e_layout_masks(20)
assert len(E_COLS) == 211


def decode_E_hex(E_hex):
    """List of 19 hex strings -> list of 19 polys as sets of monomial masks."""
    polys = []
    for h in E_hex:
        x = int(h, 16)
        s = set()
        j = 0
        while x:
            if x & 1:
                s.add(E_COLS[j])
            x >>= 1
            j += 1
        polys.append(s)
    return polys


def encode_E(polys):
    out = []
    idx = {m: j for j, m in enumerate(E_COLS)}
    for s in polys:
        x = 0
        for m in s:
            x |= 1 << idx[m]
        out.append(format(x, 'x'))
    return out


def s3_descent(xR, Bc, n=N19, mod=MOD19, l=10):
    """Own descent of S_3(x_1, x_2, x_R) = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B.
    x_1 = sum_{j<l} v_j t^j, x_2 = sum_{j<l} v_{l+j} t^j. Returns n polys (sets of masks)."""
    x1 = {1 << j: 1 << j for j in range(l)}            # mask -> field coeff
    x2 = {1 << (l + j): 1 << j for j in range(l)}

    def padd(P, Q):
        R = dict(P)
        for m, c in Q.items():
            R[m] = R.get(m, 0) ^ c
            if R[m] == 0:
                del R[m]
        return R

    def pmul(P, Q):
        R = {}
        for a, ca in P.items():
            for b, cb in Q.items():
                m = a | b
                R[m] = R.get(m, 0) ^ fmul(ca, cb, n, mod)
        return {m: c for m, c in R.items() if c}

    def pscal(P, c):
        return {m: fmul(v, c, n, mod) for m, v in P.items() if fmul(v, c, n, mod)}

    x1x2 = pmul(x1, x2)
    e2 = padd(padd(x1x2, pscal(x1, xR)), pscal(x2, xR))
    sq = {m: fmul(c, c, n, mod) for m, c in e2.items()}  # char 2, Boolean ring
    s3 = padd(sq, pscal(x1x2, xR))
    s3 = padd(s3, {0: Bc})
    polys = []
    for k in range(n):
        polys.append({m for m, c in s3.items() if c >> k & 1})
    return polys


def eval_poly(s, u):
    v = 0
    for m in s:
        if m & u == m:
            v ^= 1
    return v


def s3_value(xR, Bc, u, n=N19, mod=MOD19, l=10):
    x1 = 0
    x2 = 0
    for j in range(l):
        if u >> j & 1:
            x1 ^= 1 << j
        if u >> (l + j) & 1:
            x2 ^= 1 << j
    e2 = fmul(x1, x2) ^ fmul(x1, xR) ^ fmul(x2, xR)
    return fmul(e2, e2) ^ fmul(fmul(x1, x2), xR) ^ Bc


# ---------------------------------------------------------------- closures
def macaulay_rows(polys, mono, D):
    """Rows mu * f_k, deg mu <= D - 2, as ints in mono's order."""
    rows = []
    mus = [m for m in mono.masks if bin(m).count('1') <= D - 2]
    for mu in mus:
        for f in polys:
            r = 0
            seen = {}
            for m in f:
                mm = mu | m
                seen[mm] = seen.get(mm, 0) ^ 1
            for mm, c in seen.items():
                if c:
                    r ^= 1 << mono.index[mm]
            rows.append(r)
    return rows


def macaulay(polys, mono, D):
    E = Echelon()
    for r in macaulay_rows(polys, mono, D):
        E.add(r)
    return E


def literal_W(polys, mono, D, start=None, record=None):
    """Literal mutant closure: W^(0) = rowspace(M_D); W^(i+1) = W^(i) + span{v_j b :
    b in a basis of W^(i) cap B_{<=D-1}, all j}; every basis element every
    iteration; stop at the first i with dim W^(i+1) = dim W^(i)."""
    E = start.copy() if start is not None else macaulay(polys, mono, D)
    dims = [E.dim()]
    one_first = 0 if E.has_one() else None
    per_iter_dbd = [E.dims_by_deg(mono)]
    it = 0
    while True:
        low = E.low_rows(mono, D - 1)
        prods = mono.times_all_vars_batch(low)
        for p in prods:
            E.add(p)
        it += 1
        dims.append(E.dim())
        per_iter_dbd.append(E.dims_by_deg(mono))
        if one_first is None and E.has_one():
            one_first = it
        if dims[-1] == dims[-2]:
            break
    return {
        'dims': dims[:-1] if len(dims) > 1 else dims,
        'dims_all': dims,
        'iterations_to_fixpoint': it - 1,
        'final_dim': E.dim(),
        'one': E.has_one(),
        'one_first_iteration': one_first,
        'dims_by_deg': E.dims_by_deg(mono),
        'per_iter_dims_by_deg': per_iter_dbd,
    }, E


# ---------------------------------------------------------------- rc_b pieces
def quad_kernel(polys, nv=20):
    """Left kernel of the 19 x (#quadratic monomials) matrix: returns basis vectors c (lists)."""
    quads = [m for m in E_COLS if bin(m).count('1') == 2]
    qi = {m: i for i, m in enumerate(quads)}
    neq = len(polys)
    rows = []
    for k, f in enumerate(polys):
        x = 0
        for m in f:
            if m in qi:
                x |= 1 << qi[m]
        rows.append((x, 1 << k))
    # Gaussian elimination tracking combinations
    piv = {}
    kernel = []
    for x, comb in rows:
        while x:
            p = x.bit_length() - 1
            if p in piv:
                px, pc = piv[p]
                x ^= px
                comb ^= pc
            else:
                piv[p] = (x, comb)
                break
        if x == 0:
            kernel.append(comb)
    # kernel combos are independent (each has a distinct own row bit as highest new row)
    return [[(c >> k) & 1 for k in range(neq)] for c in kernel]


def combo(polys, c):
    s = set()
    for k, f in enumerate(polys):
        if c[k]:
            s ^= f
    return s


def substitute(polys, ell, nv=20):
    """pi: v_{j*} := ell + v_{j*} (j* = least index in ell's linear support),
    multilinear reduction, relabel the remaining variables ascending.
    Returns (substituted polys over nv-1 vars, j*, L as set of masks)."""
    lin = sorted(i for i in range(nv) if (1 << i) in ell)
    assert lin, 'ell has no linear part'
    js = lin[0]
    L = set(ell)
    L ^= {1 << js}  # L = ell + v_{j*}
    assert all(not (m >> js & 1) for m in L)
    assert all(bin(m).count('1') <= 1 for m in L)

    def relabel(m):
        out = 0
        for i in range(nv):
            if m >> i & 1:
                assert i != js
                out |= 1 << (i if i < js else i - 1)
        return out

    res = []
    for f in polys:
        g = set()
        for m in f:
            if m >> js & 1:
                rest = m ^ (1 << js)
                prod = mul_masks({rest}, L)
                g ^= prod
            else:
                g ^= {m}
        res.append({relabel(m) for m in g})
    return res, js, L, relabel

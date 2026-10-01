"""rtlib.py -- own code of TASK-20260926-c58e87 (red team, REVIEW-CERTBIN-20260926-089841).

Written from the specification texts (EXP-CERTBIN-4e92d7 object, EXP-CERTBIN-e94b27
object, EXP-CERTBIN-ddfe75 object.E_layout / parts / union_support) and from
KN-TECH-b18366's S_3. It imports NOTHING from experiments/*/impl/, experiments/*/verifier/
or crypto_autoresearcher. The pinned engine is imported only by the separate engine
driver (o4_engine.py), as the object under test.

Contents:
  * F_{2^17} = F_2[t]/(t^17 + t^3 + 1) arithmetic, trace;
  * binary-curve arithmetic for Y^2 + XY = X^3 + A X^2 + B (self-test of S_3 only);
  * the S_3 descent over an arbitrary 9-element basis b_0..b_8 (polynomial basis t^j or a
    random V'), in the 17 x 172 E_layout (column 0 constant, 1..18 v_0..v_17, 19..171 pairs
    in ascending sorted-tuple order);
  * union support, S_L, the Q_k (N-CONV17) forms;
  * exhaustive 2^18 satisfiability by bit-sliced truth tables;
  * P = rank of the degree-4 projection of M_4 (L-TOP) with Python-int elimination;
  * own M_4 (rank, one, dims_by_deg) and own literal W_4 (every low-degree basis vector
    times every v_j at every iteration) for cross-checks;
  * flat-certificate check sum mu*f_k == 1.
"""
from __future__ import annotations

import hashlib
import itertools
import json

import numpy as np

N = 17
MOD = (1 << 17) | (1 << 3) | 1
NV = 18
A_CURVE = 97044
B_CURVE = 126251

# ---------------------------------------------------------------------------
# field
# ---------------------------------------------------------------------------

def gmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> N:
            a ^= MOD
    return r


def gsq(a: int) -> int:
    return gmul(a, a)


def gpow(a: int, e: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = gmul(r, a)
        a = gmul(a, a)
        e >>= 1
    return r


def ginv(a: int) -> int:
    assert a != 0
    return gpow(a, (1 << N) - 2)


def gtr(a: int) -> int:
    s = 0
    x = a
    for _ in range(N):
        s ^= x
        x = gsq(x)
    assert s in (0, 1), s
    return s


def deg(a: int) -> int:
    return a.bit_length() - 1


def irreducible_check() -> bool:
    # t^(2^17) == t mod f and gcd(t^(2^i) - t, f) = 1 for i = 1..8 (17 prime: enough to
    # check t^(2^17) = t and t^2 != t)
    x = 2
    for _ in range(N):
        x = gsq(x)
    if x != 2:
        return False
    # 17 is prime, so the only proper subfield is F_2; t not in F_2 -> degree 17
    return True

# ---------------------------------------------------------------------------
# curve (self-test only)
# ---------------------------------------------------------------------------

def s3(x1: int, x2: int, x3: int, B: int = B_CURVE) -> int:
    u = gmul(x1, x2) ^ gmul(x1, x3) ^ gmul(x2, x3)
    return gsq(u) ^ gmul(gmul(x1, x2), x3) ^ B


def on_curve(x, y, A=A_CURVE, B=B_CURVE):
    return (gsq(y) ^ gmul(x, y)) == (gmul(gsq(x), x) ^ gmul(A, gsq(x)) ^ B)


def point_add(P, Q, A=A_CURVE):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y1 ^ y2 == x1:  # Q = -P (covers the 2-torsion point x = 0)
            return None
        # y1 == y2: doubling, x1 != 0
        lam = x1 ^ gmul(y1, ginv(x1))
        x3 = gsq(lam) ^ lam ^ A
        y3 = gsq(x1) ^ gmul(lam ^ 1, x3)
        return (x3, y3)
    lam = gmul(y1 ^ y2, ginv(x1 ^ x2))
    x3 = gsq(lam) ^ lam ^ x1 ^ x2 ^ A
    y3 = gmul(lam, x1 ^ x3) ^ x3 ^ y1
    return (x3, y3)


def lift_x(x, rng, A=A_CURVE, B=B_CURVE):
    """Return a point with abscissa x or None. Solve y^2 + x y = rhs."""
    if x == 0:
        return (0, gpow(B, 1 << (N - 1)))
    rhs = gmul(gsq(x), x) ^ gmul(A, gsq(x)) ^ B
    c = gmul(rhs, ginv(gsq(x)))  # z^2 + z = c with y = x z
    if gtr(c) != 0:
        return None
    # half-trace (n odd)
    z = 0
    w = c
    for i in range((N - 1) // 2 + 1):
        z ^= w
        w = gsq(gsq(w))
    assert gsq(z) ^ z == c
    return (x, gmul(x, z))

# ---------------------------------------------------------------------------
# layout
# ---------------------------------------------------------------------------
PAIRS = list(itertools.combinations(range(NV), 2))
COLS = [()] + [(i,) for i in range(NV)] + PAIRS
assert len(COLS) == 172
COLIDX = {m: c for c, m in enumerate(COLS)}
COLMASK = [sum(1 << i for i in m) for m in COLS]
BILINEAR_COLS = [COLIDX[(i, 9 + j)] for i in range(9) for j in range(9)]
QUAD_COLS = list(range(19, 172))
LOW_COLS = list(range(0, 19))


def poly_basis():
    return [1 << j for j in range(9)]


def descent(xr: int, basis, B: int = B_CURVE) -> np.ndarray:
    """E(x_R) over V' = span(basis): 17 x 172 uint8. f = phi(X1 X2) + x_R^2 (X1+X2)^2 + B,
    phi(y) = y^2 + x_R y, X1 = sum v_j b_j, X2 = sum v_{9+j} b_j, multilinearized."""
    E = np.zeros((N, 172), dtype=np.uint8)
    xr2 = gsq(xr)
    for i in range(9):
        for j in range(9):
            y = gmul(basis[i], basis[j])
            c = gsq(y) ^ gmul(xr, y)
            col = COLIDX[(i, 9 + j)]
            for k in range(N):
                if (c >> k) & 1:
                    E[k, col] ^= 1
    for j in range(9):
        c = gmul(xr2, gsq(basis[j]))
        for k in range(N):
            if (c >> k) & 1:
                E[k, 1 + j] ^= 1
                E[k, 1 + 9 + j] ^= 1
    for k in range(N):
        if (B >> k) & 1:
            E[k, 0] ^= 1
    return E


def conv17() -> np.ndarray:
    """N-CONV17 kept part: row k quadratic columns = Q_k = sum_{i+j=k} v_i v_{9+j}."""
    E = np.zeros((N, 172), dtype=np.uint8)
    for i in range(9):
        for j in range(9):
            E[i + j, COLIDX[(i, 9 + j)]] ^= 1
    return E


def eval_poly_row(row, v):
    s = 0
    for c in np.flatnonzero(row):
        m = COLS[c]
        t = 1
        for i in m:
            t &= v[i]
        s ^= t
    return s


def E_to_hex(E):
    out = []
    for k in range(E.shape[0]):
        x = 0
        for c in np.flatnonzero(E[k]):
            x |= 1 << int(c)
        out.append(format(x, "x"))
    return out


def hex_to_E(hexes):
    E = np.zeros((len(hexes), 172), dtype=np.uint8)
    for k, h in enumerate(hexes):
        x = int(h, 16)
        for c in range(172):
            if (x >> c) & 1:
                E[k, c] = 1
    return E


def E_eqs_masks(E):
    """17 lists of monomial masks (bit i = v_i) -- the engine's input format."""
    return [[COLMASK[c] for c in np.flatnonzero(E[k])] for k in range(E.shape[0])]


def E_sha(E):
    return hashlib.sha256(json.dumps(E_to_hex(E)).encode()).hexdigest()


def union_support(basis, B=B_CURVE):
    E0 = descent(0, basis, B)
    U = E0.copy()
    for j in range(N):
        Ej = descent(1 << j, basis, B) ^ E0
        U |= Ej
    return U


def S_L_positions(U):
    """row-major (k ascending, then column ascending) positions of U in columns 0..18"""
    return [(k, c) for k in range(N) for c in range(19) if U[k, c]]

# ---------------------------------------------------------------------------
# exhaustive satisfiability (bit-sliced over 2^18 assignments; v_i = bit i of a)
# ---------------------------------------------------------------------------
_W = (1 << NV) // 64
_TT = None


def truth_tables():
    global _TT
    if _TT is not None:
        return _TT
    a = np.arange(1 << NV, dtype=np.uint64)
    T = []
    for i in range(NV):
        bits = ((a >> np.uint64(i)) & np.uint64(1)).astype(np.uint8)
        T.append(np.packbits(bits, bitorder="little").view(np.uint64).copy())
    _TT = T
    return T


def solutions(E):
    T = truth_tables()
    ones = np.full(_W, np.uint64(0xFFFFFFFFFFFFFFFF), dtype=np.uint64)
    anynz = np.zeros(_W, dtype=np.uint64)
    for k in range(E.shape[0]):
        f = np.zeros(_W, dtype=np.uint64)
        for c in np.flatnonzero(E[k]):
            m = COLS[c]
            if len(m) == 0:
                f ^= ones
            elif len(m) == 1:
                f ^= T[m[0]]
            else:
                f ^= T[m[0]] & T[m[1]]
        anynz |= f
    z = ~anynz
    bits = np.unpackbits(z.view(np.uint8), bitorder="little")
    return np.flatnonzero(bits).tolist()

# ---------------------------------------------------------------------------
# Macaulay: own ordering. Monomials of degree <= 4 as masks; bit position assigned so
# that all degree-4 monomials are above all degree-3 ones, etc. (graded), constant at 0.
# ---------------------------------------------------------------------------
MONO = {}
for _d in range(5):
    for _m in itertools.combinations(range(NV), _d):
        MONO.setdefault(_d, []).append(sum(1 << i for i in _m))
OFF = {}
_pos = 0
POS = {}
for _d in range(5):
    OFF[_d] = _pos
    for _mk in MONO[_d]:
        POS[_mk] = _pos
        _pos += 1
NCOL4 = _pos  # 4048
assert NCOL4 == 4048
MASK_OF_POS = [0] * NCOL4
for _mk, _p in POS.items():
    MASK_OF_POS[_p] = _mk
MUS2 = MONO[0] + MONO[1] + MONO[2]  # degree <= 2 multipliers, 172
DEG4_POS = {mk: i for i, mk in enumerate(MONO[4])}  # 3060


def popc(x: int) -> int:
    return bin(x).count("1")


def row_int(mu: int, fmasks) -> int:
    x = 0
    for m in fmasks:
        x ^= 1 << POS[mu | m]
    return x


class Echelon:
    """Echelon basis keyed by leading (highest) bit."""

    def __init__(self):
        self.piv = {}

    def add(self, x: int) -> bool:
        piv = self.piv
        while x:
            hb = x.bit_length() - 1
            p = piv.get(hb)
            if p is None:
                piv[hb] = x
                return True
            x ^= p
        return False

    def reduce(self, x: int) -> int:
        piv = self.piv
        while x:
            hb = x.bit_length() - 1
            p = piv.get(hb)
            if p is None:
                return x
            x ^= p
        return 0

    def dim(self):
        return len(self.piv)

    def dims_by_deg(self):
        out = []
        for d in range(5):
            lim = OFF[d + 1] if d < 4 else NCOL4
            out.append(sum(1 for hb in self.piv if hb < lim))
        return out


def P_rank(E) -> int:
    """rank of the degree-4 projection of M_4 (L-TOP): rows mu*q_k, |mu| = 2, only the
    degree-4 monomials mu cup m with m in supp q_k disjoint from mu."""
    qs = [[COLMASK[c] for c in np.flatnonzero(E[k]) if c >= 19] for k in range(E.shape[0])]
    ech = Echelon()
    for mu in MONO[2]:
        for k in range(E.shape[0]):
            x = 0
            for m in qs[k]:
                if mu & m == 0:
                    x ^= 1 << DEG4_POS[mu | m]
            if x:
                ech.add(x)
    return ech.dim()


def own_M4(E):
    eqs = E_eqs_masks(E)
    ech = Echelon()
    for mu in MUS2:
        for k in range(len(eqs)):
            x = row_int(mu, eqs[k])
            if x:
                ech.add(x)
    return ech


def own_M4_record(E):
    ech = own_M4(E)
    dbd = ech.dims_by_deg()
    one = ech.reduce(1) == 0
    return {"rank": ech.dim(), "one": one, "dims_by_deg": dbd,
            "P": ech.dim() - dbd[3], "fallen": dbd[3]}


def times_var(x: int, j: int) -> int:
    bj = 1 << j
    out = 0
    while x:
        lb = x & -x
        p = lb.bit_length() - 1
        out ^= 1 << POS[MASK_OF_POS[p] | bj]
        x ^= lb
    return out


def own_W4(E, max_iter=10):
    """Literal W_4: W^(0) = rowspace M_4; W^(i+1) = W^(i) + span{v_j b : b in a basis of
    W^(i) cap B_{<=3}, all j}. Every low-degree basis vector is multiplied at every
    iteration (no 'new only' shortcut)."""
    ech = own_M4(E)
    dims = [ech.dim()]
    one_first = 0 if ech.reduce(1) == 0 else None
    it = 0
    while True:
        low = [x for hb, x in list(ech.piv.items()) if hb < OFF[4]]
        before = ech.dim()
        for x in low:
            for j in range(NV):
                y = times_var(x, j)
                if y:
                    ech.add(y)
        if ech.dim() == before:
            break
        it += 1
        dims.append(ech.dim())
        if one_first is None and ech.reduce(1) == 0:
            one_first = it
        if it >= max_iter:
            break
    return {"iterations_to_fixpoint": it, "dims": dims, "final_dim": dims[-1],
            "one": one_first is not None, "one_first_iteration": one_first,
            "dims_by_deg": ech.dims_by_deg()}


def flat_cert_ok(cert, E):
    """cert: list of (mu_mask, k). True iff sum mu*f_k == 1 in B (multilinear)."""
    eqs = E_eqs_masks(E)
    acc = {}
    for mu, k in cert:
        for m in eqs[k]:
            x = mu | m
            acc[x] = acc.get(x, 0) ^ 1
    res = sorted(x for x, p in acc.items() if p)
    return res == [0], (max(popc(mu) for mu, _ in cert) if cert else None)


def left_kernel_dim_quadratic(E):
    """dimension of the left kernel of the 17 x 153 quadratic-column submatrix (own
    elimination over F_2) and one kernel vector if the dimension is 1."""
    rows = []
    for k in range(E.shape[0]):
        x = 0
        for c in QUAD_COLS:
            if E[k, c]:
                x |= 1 << (c - 19)
        rows.append(x)
    # augment with identity to track combinations
    aug = [(rows[k] << N) | (1 << k) for k in range(E.shape[0])]
    ech = {}
    kern = []
    for x in aug:
        while x >> N:
            hb = x.bit_length() - 1
            if hb in ech:
                x ^= ech[hb]
            else:
                ech[hb] = x
                break
        if not (x >> N):
            kern.append(x & ((1 << N) - 1))
    # kern vectors from the reduction are independent combos giving zero
    kb = Echelon()
    for v in kern:
        kb.add(v)
    return kb.dim(), (kern[0] if len(kern) == 1 else None)

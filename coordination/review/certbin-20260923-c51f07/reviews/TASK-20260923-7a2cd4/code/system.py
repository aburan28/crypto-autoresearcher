"""Descended system, Macaulay matrix, solver, row pass, traces and replay,
written from the `object` block of experiments/EXP-CERTBIN-4e92d7/specification.yaml.

Conventions (all indices 0-based):
  * Boolean variables v_0..v_17, v_0 > v_1 > ... > v_17.
    x_1 = sum_{j<9} v_j t^j,  x_2 = sum_{j<9} v_{9+j} t^j.
  * A multilinear monomial is a bitmask over v_0..v_17 (bit i <=> v_i divides).
  * A multilinear polynomial with F_{2^17} coefficients is a dict
    mask -> field element; its t^k coordinate is descended equation k.
    So E(r) is represented by the 172 coefficient words c_m (bit k of c_m is
    the entry of E(r) in row k, monomial m).
  * Column position of a monomial = its index in the DESCENDING degrevlex
    order (constant last). Bit position of a packed row = column position.
"""
import hashlib
import json
from functools import cmp_to_key
from itertools import combinations

import numpy as np

import gf2n as F

NV = 18
NEQ = 17
L = 9


# ---------------------------------------------------------------- monomials --
def popcount(m: int) -> int:
    return bin(m).count("1")


def index_tuple(m: int):
    return tuple(i for i in range(NV) if (m >> i) & 1)


def monomials_upto(d: int):
    out = []
    for k in range(d + 1):
        for c in combinations(range(NV), k):
            m = 0
            for i in c:
                m |= 1 << i
            out.append(m)
    return out


def mu_order(dmax: int):
    """Row multipliers: deg ascending, then ascending sorted index tuple, lex."""
    return sorted(monomials_upto(dmax), key=lambda m: (popcount(m), index_tuple(m)))


def degrevlex_greater(a: int, b: int) -> bool:
    """Literal spec rule: a > b iff deg a > deg b; or deg a = deg b and, at the
    largest variable index i where a and b differ, a does NOT contain v_i."""
    da, db = popcount(a), popcount(b)
    if da != db:
        return da > db
    if a == b:
        return False
    i = (a ^ b).bit_length() - 1
    return not ((a >> i) & 1)


def column_order(D: int):
    """Descending degrevlex; for equal degree, a > b  <=>  mask(a) < mask(b)
    (the highest differing bit decides both). Constant (deg 0) is last."""
    return sorted(monomials_upto(D), key=lambda m: (-popcount(m), m))


def column_order_literal(D: int):
    def cmp(a, b):
        if degrevlex_greater(a, b):
            return -1
        if degrevlex_greater(b, a):
            return 1
        return 0
    return sorted(monomials_upto(D), key=cmp_to_key(cmp))


# ---------------------------------------------------------------- descent --
def _padd(*ps):
    r = {}
    for p in ps:
        for m, c in p.items():
            r[m] = r.get(m, 0) ^ c
    return {m: c for m, c in r.items() if c}


def _pmul(p, q):
    r = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = m1 | m2                         # multilinear reduction v^2 = v
            r[m] = r.get(m, 0) ^ F.mul(c1, c2)
    return {m: c for m, c in r.items() if c}


X1 = {1 << j: 1 << j for j in range(L)}
X2 = {1 << (L + j): 1 << j for j in range(L)}


def descend(B: int, xR: int):
    """Coefficient dict of S_3(x_1, x_2, x_R) = (x1x2 + x1xR + x2xR)^2 + x1x2xR + B,
    expanded over F_{2^17} in v_0..v_17 and multilinearized. Literal products
    (the square is computed as L*L, not by a coefficientwise shortcut)."""
    XR = {0: xR} if xR else {}
    x1x2 = _pmul(X1, X2)
    Lp = _padd(x1x2, _pmul(X1, XR), _pmul(X2, XR))
    S = _padd(_pmul(Lp, Lp), _pmul(x1x2, XR), {0: B})
    return S


def coef_xor(a, b):
    return _padd(a, b)


def equations(coef):
    """Equation k = set of monomial masks whose coefficient has bit k set."""
    return [frozenset(m for m, c in coef.items() if (c >> k) & 1) for k in range(NEQ)]


def eval_equations_at(eqs, v: int) -> int:
    """17-bit word, bit k = value of Boolean equation k at assignment v."""
    out = 0
    for k, eq in enumerate(eqs):
        bit = 0
        for m in eq:
            if (m & v) == m:
                bit ^= 1
        out |= bit << k
    return out


def s3_field(x1: int, x2: int, x3: int, B: int) -> int:
    """S_3 evaluated directly in F_{2^17} (KN-TECH-b18366 formula)."""
    t = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    return F.sq(t) ^ F.mul(F.mul(x1, x2), x3) ^ B


# ---------------------------------------------------------------- Macaulay --
class Shape:
    def __init__(self, D: int):
        self.D = D
        self.mus = mu_order(D - 2)
        self.cols = column_order(D)
        self.pos = {m: i for i, m in enumerate(self.cols)}
        self.R = len(self.mus) * NEQ
        self.C = len(self.cols)
        self.W = (self.C + 63) // 64


def macaulay(shape: Shape, eqs):
    """Packed M_D: row (idx(mu)*17 + k) = multilinear reduction of mu * f_k.
    Zero rows retained."""
    rows, cols = [], []
    pos = shape.pos
    for mi, mu in enumerate(shape.mus):
        base = mi * NEQ
        for k in range(NEQ):
            r = base + k
            for m in eqs[k]:
                rows.append(r)
                cols.append(pos[mu | m])
    rows = np.asarray(rows, dtype=np.int64)
    cols = np.asarray(cols, dtype=np.int64)
    M = np.zeros((shape.R, shape.W), dtype="<u8")
    bits = np.left_shift(np.uint64(1), (cols & 63).astype(np.uint64))
    np.bitwise_xor.at(M, (rows, cols >> 6), bits)   # XOR handles cancellation
    return M


def row_positions(M, i: int, C: int):
    x = int.from_bytes(M[i].tobytes(), "little")
    return [c for c in range(C) if (x >> c) & 1]


# ------------------------------------------------------------------ solver --
def column_pass(M0, C: int, keep_ops: bool = False):
    """THE SOLVER (spec `object.elimination`). Deterministic forward
    elimination, column-major; pivot = smallest ORIGINAL index among unused rows
    with a 1 in column c; XOR row p into every other unused row with a 1 in
    column c (set X). Rows never move. Returns steps [(p, c)], optional op log
    [(p, c, X)], the streamed sha256 of canonical-JSON T_ops, and sum |X|."""
    M = M0.copy()
    R = M.shape[0]
    unused = np.ones(R, dtype=bool)
    steps = []
    ops = [] if keep_ops else None
    h = hashlib.sha256()
    h.update(b"[")
    first = True
    sumX = 0
    one = np.uint64(1)
    for c in range(C):
        w, b = c >> 6, np.uint64(c & 63)
        colbits = ((M[:, w] >> b) & one).astype(bool)
        cand = np.flatnonzero(colbits & unused)
        if cand.size == 0:
            continue
        p = int(cand[0])
        X = cand[1:]
        if X.size:
            M[X] ^= M[p]
        unused[p] = False
        steps.append((p, c))
        Xl = X.tolist()
        sumX += len(Xl)
        piece = ("" if first else ",") + "[" + str(p) + "," + str(c) + ",[" + ",".join(map(str, Xl)) + "]]"
        h.update(piece.encode("utf-8"))
        first = False
        if keep_ops:
            ops.append((p, c, Xl))
    h.update(b"]")
    # after the last column every unused row must be zero
    residual_nonzero = int(np.count_nonzero(M[unused].any(axis=1))) if unused.any() else 0
    return {
        "steps": steps,
        "ops": ops,
        "T_ops_sha256": h.hexdigest(),
        "sumX": sumX,
        "unused_rows_final": np.flatnonzero(unused).tolist(),
        "residual_nonzero_unused_rows": residual_nonzero,
    }


def row_pass(M0):
    """SEPARATE row-sequential pass: incremental echelon basis in original row
    order. Z = {i : row i in span(rows 0..i-1)}. Leading column = smallest
    column position with a nonzero entry. Python big-int rows (independent of
    the numpy column pass)."""
    basis = {}
    Z = []
    for i in range(M0.shape[0]):
        x = int.from_bytes(M0[i].tobytes(), "little")
        while x:
            lead = (x & -x).bit_length() - 1
            b = basis.get(lead)
            if b is None:
                basis[lead] = x
                break
            x ^= b
        else:
            Z.append(i)
    return sorted(basis.keys()), Z


# ------------------------------------------------------------------ traces --
def canon(obj) -> str:
    return json.dumps(obj, separators=(",", ":"))


def sha(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


def traces(cp, Z):
    steps = cp["steps"]
    rank = len(steps)
    T_rank = rank
    T_set = [sorted(c for _, c in steps), sorted(Z)]
    T_strict = [[p, c] for p, c in steps]
    return T_rank, T_set, T_strict


# ------------------------------------------------------------------ replay --
def replay(blocks, ops):
    """Fixed-schedule replay (spec `object.fixed_schedule_replay`): apply
    exactly the reference's XORs to each block, no data-dependent choice.
    e[k, b] = entry (p_k, c_k) of block b immediately BEFORE step k's XORs.
    All blocks are replayed together (row ops act blockwise)."""
    W = blocks[0].shape[1]
    nb = len(blocks)
    M = np.concatenate(blocks, axis=1).copy()
    offs = W * np.arange(nb)
    e = np.zeros((len(ops), nb), dtype=np.uint8)
    one = np.uint64(1)
    for k, (p, c, X) in enumerate(ops):
        e[k] = ((M[p, offs + (c >> 6)] >> np.uint64(c & 63)) & one).astype(np.uint8)
        if X:
            M[X] ^= M[p]
    return e


def gf2_rank_ints(vecs):
    basis = {}
    for v in vecs:
        x = v
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                break
    return len(basis)

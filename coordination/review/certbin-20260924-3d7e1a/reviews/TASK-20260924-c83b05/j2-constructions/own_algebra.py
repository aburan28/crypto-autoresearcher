"""Validator-owned algebra for TASK-20260924-c83b05 (J2). Written from the
specification text of EXP-CERTBIN-e94b27 (object.*) and EXP-CERTBIN-4e92d7
(object.*); imports NOTHING from experiments/*/impl/ or verifier/.

Representation (deliberately different from the engine's):
  * a monomial is a bit mask (bit i = v_i); multilinear product = OR;
  * a polynomial in B_{<=D} is a Python int whose bit POS(m) is the
    coefficient of monomial m, where POS orders monomials by (degree ascending,
    mask ascending). Hence the TOP bit of a nonzero polynomial is one of its
    highest-degree monomials, and an echelon basis keyed by top bit has the
    property: the basis vectors whose top bit is a monomial of degree <= d span
    W cap B_{<=d} (a combination using any vector whose top monomial has degree
    > d has a nonzero coefficient on that top monomial).
  * elimination: dict top_bit -> vector, plain Python integers (no numpy).
"""
from itertools import combinations
import numpy as np

POLY17 = (1 << 17) | (1 << 3) | 1   # t^17 + t^3 + 1


# ---------------------------------------------------------------------------
# F_{2^17}: own schoolbook arithmetic
# ---------------------------------------------------------------------------
def gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> 17:
            a ^= POLY17
    return r


def gmul_vec(a, b):
    """numpy int64 vectors; shift-and-add with per-step reduction."""
    a = np.asarray(a, dtype=np.int64).copy()
    b = np.asarray(b, dtype=np.int64).copy()
    a, b = np.broadcast_arrays(a, b)
    a = a.copy(); b = b.copy()
    r = np.zeros(a.shape, dtype=np.int64)
    for _ in range(17):
        r ^= np.where(b & 1, a, 0)
        b >>= 1
        a <<= 1
        a ^= np.where((a >> 17) & 1, POLY17, 0)
    return r


# ---------------------------------------------------------------------------
# monomials and positions
# ---------------------------------------------------------------------------
def popcount(x):
    return bin(x).count("1")


def monomials(nv, dmax):
    """all masks of degree <= dmax, ordered (degree asc, mask asc)."""
    out = []
    for d in range(dmax + 1):
        ms = sorted(sum(1 << i for i in c) for c in combinations(range(nv), d))
        out.extend(ms)
    return out


class Space:
    """B_{<=D} in nv variables with this module's position encoding."""

    def __init__(self, nv, D):
        self.nv, self.D = nv, D
        self.mons = monomials(nv, D)
        self.pos = {m: i for i, m in enumerate(self.mons)}
        self.deg_of_pos = [popcount(m) for m in self.mons]
        # highest position of degree <= d (positions are degree-major)
        self.top_pos_le = []
        for d in range(D + 1):
            self.top_pos_le.append(max(i for i, m in enumerate(self.mons) if popcount(m) <= d))

    def poly(self, masks):
        v = 0
        for m in masks:
            v ^= 1 << self.pos[m]
        return v

    def masks_of(self, v):
        out = []
        while v:
            b = v & -v
            out.append(self.mons[b.bit_length() - 1])
            v ^= b
        return out

    def mul_var(self, j, v):
        """multilinear reduction of v_j * v (v must lie in B_{<=D-1} unless
        every monomial already contains v_j)."""
        bj = 1 << j
        out = 0
        while v:
            b = v & -v
            m = self.mons[b.bit_length() - 1]
            out ^= 1 << self.pos[m | bj]
            v ^= b
        return out

    def mul_mono(self, mu, masks):
        """multilinear reduction of mu * f (f given as a list of masks)."""
        out = 0
        for m in masks:
            out ^= 1 << self.pos[mu | m]
        return out


# ---------------------------------------------------------------------------
# elimination (top-bit echelon)
# ---------------------------------------------------------------------------
def insert(basis, v):
    """reduce v against basis (dict top_bit -> vector); add if nonzero.
    Returns True iff v was independent."""
    while v:
        h = v.bit_length() - 1
        p = basis.get(h)
        if p is None:
            basis[h] = v
            return True
        v ^= p
    return False


def in_span(basis, v):
    while v:
        h = v.bit_length() - 1
        p = basis.get(h)
        if p is None:
            return False
        v ^= p
    return True


def span_basis(vectors):
    b = {}
    for v in vectors:
        insert(b, v)
    return b


def dims_by_deg(space, basis):
    return [sum(1 for h in basis if h <= space.top_pos_le[d]) for d in range(space.D + 1)]


# ---------------------------------------------------------------------------
# Macaulay rows per the spec conventions
# ---------------------------------------------------------------------------
def mu_list(nv, dmax):
    """spec order: degree ascending, then ascending sorted index tuple (lex)."""
    out = []
    for d in range(dmax + 1):
        for c in combinations(range(nv), d):
            out.append(sum(1 << i for i in c))
    return out


def macaulay_rows(space, eqs, D):
    """row index = mu_index * neq + k; content = multilinear mu * f_k; zero
    rows retained (as 0)."""
    neq = len(eqs)
    rows = []
    for mu in mu_list(space.nv, D - 2):
        for k in range(neq):
            rows.append(space.mul_mono(mu, eqs[k]))
    return rows


# ---------------------------------------------------------------------------
# LITERAL W_D (spec object.mutant_closure_W_D), no semi-naive shortcut
# ---------------------------------------------------------------------------
def literal_W(space, eqs, D, max_iter=100, keep_bases=False):
    """W^(0) = rowspace(M_D); W^(i+1) = W^(i) + span{v_j * b : b in a basis of
    W^(i) cap B_{<=D-1}, j = 0..nv-1}, EVERY low basis element multiplied at
    EVERY iteration and the whole generating set re-eliminated from scratch.
    Stop at the first i with dim W^(i+1) = dim W^(i)."""
    top_low = space.top_pos_le[D - 1]
    basis = span_basis(macaulay_rows(space, eqs, D))
    dims = [len(basis)]
    first = 0 if 0 in basis else None     # position 0 is the constant monomial
    per_iter = [{"dim": len(basis), "dims_by_deg": dims_by_deg(space, basis),
                 "low_basis_size": sum(1 for h in basis if h <= top_low)}]
    bases = [dict(basis)] if keep_bases else None
    i = 0
    while True:
        low = [v for h, v in basis.items() if h <= top_low]
        gens = list(basis.values())
        for g in low:
            for j in range(space.nv):
                gens.append(space.mul_var(j, g))
        nb = span_basis(gens)                 # full re-elimination
        # containment sanity: W^(i) subset W^(i+1)
        assert all(in_span(nb, v) for v in basis.values())
        if len(nb) == len(basis):
            break
        i += 1
        basis = nb
        dims.append(len(basis))
        if first is None and 0 in basis:
            first = i
        per_iter.append({"dim": len(basis), "dims_by_deg": dims_by_deg(space, basis),
                         "low_basis_size": sum(1 for h in basis if h <= top_low),
                         "generators_eliminated": len(gens)})
        if keep_bases:
            bases.append(dict(basis))
        if i >= max_iter:
            raise RuntimeError("max_iter")
    return {"dims": dims, "iterations_to_fixpoint": i, "final_dim": dims[-1],
            "one": 0 in basis, "one_first_iteration": first,
            "dims_by_deg": dims_by_deg(space, basis), "per_iteration": per_iter}, basis, bases


# ---------------------------------------------------------------------------
# E decoding (17 x 172 rows, bit j = monomial j in EQ order)
# ---------------------------------------------------------------------------
def eq_masks(nv=18):
    return mu_list(nv, 2)       # degree ascending then lex tuple: 172 for nv = 18


def eqs_from_hex(hx, nv=18):
    em = eq_masks(nv)
    out = []
    for h in hx:
        v = int(h, 16)
        out.append([em[j] for j in range(len(em)) if (v >> j) & 1])
    return out


def eval_eqs_all(eqs, nv=18):
    """(neq, 2^nv) truth tables by direct monomial evaluation (vectorised over
    points; own code)."""
    u = np.arange(1 << nv, dtype=np.int64)
    out = np.zeros((len(eqs), 1 << nv), dtype=np.uint8)
    for k, f in enumerate(eqs):
        acc = np.zeros(1 << nv, dtype=np.uint8)
        for m in f:
            acc ^= ((u & m) == m).astype(np.uint8)
        out[k] = acc
    return out


def s3_all_points(B, xR, nv=18, half=9):
    """S_3(x_1, x_2, x_R) = (x1x2 + x1xR + x2xR)^2 + x1x2xR + B at all 2^18
    Boolean points, own vectorised F_{2^17} arithmetic."""
    u = np.arange(1 << nv, dtype=np.int64)
    x1 = u & ((1 << half) - 1)
    x2 = u >> half
    x3 = np.full(u.shape, xR, dtype=np.int64)
    p12 = gmul_vec(x1, x2)
    e = p12 ^ gmul_vec(x1, x3) ^ gmul_vec(x2, x3)
    return gmul_vec(e, e) ^ gmul_vec(p12, x3) ^ np.int64(B)
